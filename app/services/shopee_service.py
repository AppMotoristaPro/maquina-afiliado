from curl_cffi import requests
from app.models.produto import Produto

def garimpar_shopee(urls_vistas=None):
    if urls_vistas is None: 
        urls_vistas = []
    resultados = []
    
    # URL da API Oculta (Usada pelo próprio site da Shopee para carregar a vitrine)
    # Estamos buscando a palavra "oferta" ordenada por maiores vendas (by=sales)
    url_api = "https://shopee.com.br/api/v4/search/search_items?by=sales&keyword=oferta&limit=20&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://shopee.com.br/search?keyword=oferta"
    }

    try:
        # Puxa os dados direto em formato JSON limpo
        res = requests.get(url_api, impersonate="chrome110", headers=headers, timeout=30)
        dados = res.json()
        
        # Se a API bloquear ou mudar a estrutura, retorna vazio para não travar o app
        if "items" not in dados:
            return resultados
            
        itens_encontrados = 0
        
        for item in dados["items"]:
            if itens_encontrados >= 4: # Pega os 4 melhores itens para a vitrine
                break 
                
            basic = item.get("item_basic")
            if not basic: 
                continue
                
            itemid = basic.get("itemid")
            shopid = basic.get("shopid")
            titulo = basic.get("name")
            
            # O link oficial do produto é formado pelo ID da loja e do item
            url_p = f"https://shopee.com.br/product/{shopid}/{itemid}"
            
            # Verifica se o item já foi visto no navegador ou salvo no banco de dados
            if url_p in urls_vistas: continue
            if Produto.query.filter_by(url_original=url_p).first(): continue

            # O preço da Shopee vem em micro-cents (Ex: 1500000 = 15.00)
            preco_bruto = basic.get("price")
            preco = preco_bruto / 100000 if preco_bruto else 0.0
            
            # Extrai as fotos direto do servidor de imagens (CDN) deles
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
        print(f"Erro no minerador Shopee: {e}")
        
    return resultados

