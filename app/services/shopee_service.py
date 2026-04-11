import os
import re
from curl_cffi import requests
from app.models.produto import Produto

def garimpar_shopee(urls_vistas=None):
    if urls_vistas is None: 
        urls_vistas = []
    resultados = []
    
    SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY")
    if not SCRAPER_API_KEY:
        print("ALERTA: SCRAPER_API_KEY não configurada no .env ou Render.")
        return resultados

    url_api = "https://shopee.com.br/api/v4/search/search_items?by=sales&keyword=oferta&limit=20&newest=0&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"
    
    # ATUALIZAÇÃO VITAL: Usando premium=true (IP Residencial) e country_code=br (Brasil)
    url_proxy = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url_api}&premium=true&country_code=br"

    try:
        # Aumentamos o timeout porque proxy residencial demora um pouco mais para conectar
        res = requests.get(url_proxy, timeout=60)
        
        # Trava de segurança para ver o erro real no log do Render se falhar
        if res.status_code != 200:
            print(f"Erro ScraperAPI ({res.status_code}): {res.text[:200]}")
            return resultados

        try:
            dados = res.json()
        except:
            print(f"Erro ao ler JSON. O ScraperAPI retornou HTML bloqueado: {res.text[:200]}")
            return resultados
            
        if "items" not in dados: return resultados
            
        itens_encontrados = 0
        for item in dados["items"]:
            if itens_encontrados >= 4: break 
                
            basic = item.get("item_basic")
            if not basic: continue
                
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
                    "titulo": titulo, "preco": preco, "url": url_p, 
                    "imagens": imgs[:6], "plataforma": "shopee"
                })
                itens_encontrados += 1
                
    except Exception as e:
        print(f"Erro geral no minerador Shopee: {e}")
        
    return resultados

# NOVIDADE: Função Sniper para buscar qualquer link da Shopee diretamente
def garimpar_shopee_url(url_p):
    # Tenta extrair o ID da Loja e ID do Item dos padrões de link da Shopee
    match = re.search(r'-i\.(\d+)\.(\d+)', url_p)
    if not match:
        match = re.search(r'product/(\d+)/(\d+)', url_p)
        
    if not match: 
        return []
    
    shopid, itemid = match.groups()
    api_item = f"https://shopee.com.br/api/v4/item/get?itemid={itemid}&shopid={shopid}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        # A página de um item específico quase nunca é bloqueada, então não usamos o ScraperAPI aqui
        res = requests.get(api_item, impersonate="chrome110", headers=headers, timeout=30)
        dados = res.json()
        
        if "data" not in dados or not dados["data"]: return []
        
        item = dados["data"]
        titulo = item.get("name", "Oferta Shopee")
        preco_bruto = item.get("price")
        preco = preco_bruto / 100000 if preco_bruto else 0.0
        
        imagens_ids = item.get("images", [])
        imgs = [f"https://cf.shopee.com.br/file/{img_id}" for img_id in imagens_ids]

        if len(imgs) >= 3 and preco > 0:
            return [{
                "titulo": titulo, "preco": preco, "url": url_p, 
                "imagens": imgs[:6], "plataforma": "shopee"
            }]
    except Exception as e:
        print(f"Erro URL Direta Shopee: {e}")
        
    return []

