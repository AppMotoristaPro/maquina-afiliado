import re
from curl_cffi import requests
from app.models.produto import Produto

def garimpar_shopee(urls_vistas=None):
    # Desativado para evitar bloqueios de IP no Render. 
    # O foco agora é 100% na busca direta por link.
    return []

def garimpar_shopee_url(url_p):
    # Extrai IDs da loja e do item do link colado
    match = re.search(r'-i\.(\d+)\.(\d+)', url_p)
    if not match: 
        match = re.search(r'product/(\d+)/(\d+)', url_p)
        
    if not match: 
        return []
    
    shopid, itemid = match.groups()
    # Acessa a API de detalhes do item (geralmente aberta para IPs de servidor)
    api_item = f"https://shopee.com.br/api/v4/item/get?itemid={itemid}&shopid={shopid}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://shopee.com.br/"
    }
    
    try:
        # Busca direta sem necessidade de proxy pago
        res = requests.get(api_item, impersonate="chrome110", headers=headers, timeout=30)
        dados = res.json()
        
        if "data" not in dados or not dados["data"]: 
            return []
        
        item = dados["data"]
        # Preço Shopee: Divide por 100.000 para converter de micro-cents
        preco = item.get("price") / 100000 if item.get("price") else 0.0
        # Gera links diretos para as imagens no CDN da Shopee
        imgs = [f"https://cf.shopee.com.br/file/{img_id}" for img_id in item.get("images", [])]

        if len(imgs) >= 3:
            return [{
                "titulo": item.get("name", "Oferta Shopee"), 
                "preco": preco, 
                "url": url_p, 
                "imagens": imgs[:6], 
                "plataforma": "shopee"
            }]
    except Exception as e:
        print(f"Erro na extração direta Shopee: {e}")
        
    return []

