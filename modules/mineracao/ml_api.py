# modules/mineracao/ml_api.py (Trecho principal atualizado)
import requests
import re
from bs4 import BeautifulSoup

def buscar_produtos_tendencia(termo_busca):
    print(f"Buscando produtos reais para: {termo_busca}")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_busca.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url_busca, headers=headers)
        # Pega os links reais dos produtos
        links = re.findall(r'https://produto\.mercadolivre\.com\.br/MLB-\d+-[^"]+', res.text)
        links = list(set(links)) # Remove duplicatas

        for url_p in links[:3]: # Tenta os 3 primeiros
            res_p = requests.get(url_p, headers=headers)
            html = res_p.text
            
            # Pega apenas imagens originais grandes
            imagens = re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_\d+-O\.webp', html)
            
            if len(imagens) >= 3:
                titulo = re.search(r'<h1 class="ui-pdp-title">([^<]+)</h1>', html)
                titulo = titulo.group(1).strip() if titulo else "Produto"
                
                preco_meta = re.search(r'<meta itemprop="price" content="([\d\.]+)"', html)
                preco = float(preco_meta.group(1)) if preco_meta else 0.0
                
                print(f"Produto encontrado: {titulo}")
                return [{
                    "id": "MLB",
                    "titulo": titulo,
                    "preco": preco,
                    "url_original": url_p,
                    "midia": {"imagens_url": list(set(imagens))}
                }]
        return []
    except Exception as e:
        print(f"Erro na mineração: {e}")
        return []

