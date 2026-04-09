# modules/mineracao/ml_api.py
import requests
from bs4 import BeautifulSoup
import re
from config import SCRAPER_API_KEY

def buscar_produtos_tendencia(termo_busca):
    print(f"--- [MINERADOR] ACESSANDO VIA PROXY RESIDENCIAL: {termo_busca} ---")
    url_alvo = f"https://lista.mercadolivre.com.br/{termo_busca.replace(' ', '-')}"
    
    # Payload para o ScraperAPI
    params = {
        'api_key': SCRAPER_API_KEY,
        'url': url_alvo,
        'render': 'false' 
    }

    try:
        response = requests.get('http://api.scraperapi.com', params=params, timeout=60)
        if response.status_code != 200:
            print(f"--- [MINERADOR] Erro no Proxy: {response.status_code} ---")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            if 'produto.mercadolivre.com.br/MLB-' in a['href']:
                url = a['href'].split('#')[0].split('?')[0]
                if url not in links: links.append(url)

        print(f"--- [MINERADOR] Sucesso! {len(links)} produtos encontrados via Proxy. ---")

        for url_p in links[:3]:
            params['url'] = url_p
            res_p = requests.get('http://api.scraperapi.com', params=params, timeout=60)
            html = res_p.text
            
            titulo = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
            titulo = titulo.group(1).strip() if titulo else "Produto"
            
            # Captura imagens reais em alta resolução
            imagens = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp', html)))

            if len(imagens) >= 2:
                print(f"--- [MINERADOR] PRODUTO SELECIONADO: {titulo} ---")
                return [{
                    "id": "MLB",
                    "titulo": titulo,
                    "preco": 0.0,
                    "url_original": url_p,
                    "midia": {"imagens_url": imagens}
                }]
        return []
    except Exception as e:
        print(f"--- [MINERADOR] Erro Crítico: {e} ---")
        return []

