from curl_cffi import requests
from bs4 import BeautifulSoup
import re
from app.models.produto import Produto

def garimpar_shopee(urls_vistas=None):
    if urls_vistas is None: urls_vistas = []
    resultados = []
    
    # Foco em coleções de ofertas e mais vendidos
    url_alvo = "https://shopee.com.br/m/ofertas-relampago"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    try:
        res = requests.get(url_alvo, impersonate="chrome110", headers=headers, timeout=30)
        
        # Busca links de produtos com o padrão de ID da Shopee
        links = re.findall(r'https://shopee\.com\.br/[\w\d\.\-]+\-i\.\d+\.\d+', res.text)
        
        itens_encontrados = 0
        for url_p in list(set(links)):
            if itens_encontrados >= 8: break 
            if url_p in urls_vistas: continue
            if Produto.query.filter_by(url_original=url_p).first(): continue

            rp = requests.get(url_p, impersonate="chrome110", headers=headers, timeout=30)
            soup_p = BeautifulSoup(rp.text, 'html.parser')
            
            titulo = soup_p.find('title').text.replace('| Shopee Brasil', '').strip()
            
            # Extração de preço (ajustada para formato micro-cents da Shopee)
            preco_match = re.search(r'"price":\s*(\d+)', rp.text)
            preco = float(preco_match.group(1)) / 100000 if preco_match else 0.0
            
            # Captura imagens do CDN oficial
            imgs = re.findall(r'https://cf\.shopee\.com\.br/file/[\w\d]+', rp.text)
            imgs = list(dict.fromkeys(imgs)) 

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

