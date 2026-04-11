import os
from curl_cffi import requests
from app.models.produto import Produto

def garimpar_shopee(urls_vistas=None):
    if urls_vistas is None: 
        urls_vistas = []
    resultados = []
    
    # Puxa a chave de acesso que configuramos no Render / .env
    SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
    
    if not SCRAPER_API_KEY:
        print("ALERTA: SCRAPER_API_KEY não encontrada no sistema.")
        return resultados

    # URL oculta da Shopee que entrega o Ouro (JSON puro)
    url_api = "https://shopee.com.br/api/v4/search/search_items?by=sales&keyword=oferta&limit=20&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    
    # Enviamos a URL da Shopee para dentro da URL do ScraperAPI
    url_proxy = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url_api}"

    try:
        # Timeout aumentado para 45s porque o proxy demora um pouco mais para mascarar e rotear o IP
        res = requests.get(url_proxy, impersonate="chrome110", timeout=45)
        dados = res.json()
        
        if "items" not in dados:
            return resultados
            
        itens_encontrados = 0
        
        for item in dados["items"]:
            if itens_encontrados >= 4: 
                break 
                
            basic = item.get("item_basic")
            if not basic: 
                continue
                
            itemid = basic.get("itemid")
            shopid = basic.get("shopid")
            titulo = basic.get("name")
            
            url_p = f"https://shopee.com.br/product/{shopid}/{itemid}"
            
            if url_p in urls_vistas: continue
            if Produto.query.filter_by(url_original=url_p).first(): continue

            preco_bruto = basic.get("price")
            preco = preco_bruto / 100000 if preco_bruto else 0.0
            
            imagens_ids = basic.get("images", [])
            imgs = [f"https://cf.shopee.com.br/file/{img_id}" for img_id in imagens_ids]

            if len(imgs) >= 3 and preco > 0:
                resultados.append({
                    "titulo": titulo,
                    "preco": preco,
                    "url": url_p,
                    "imagens": imgs[:6],
                    "plataforma": "shopee"
                })
                itens_encontrados += 1
                
    except Exception as e:
        print(f"Erro no minerador Shopee via ScraperAPI: {e}")
        
    return resultados

