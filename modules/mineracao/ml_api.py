# modules/mineracao/ml_api.py
from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def buscar_produtos_tendencia(termo_busca):
    print(f"--- [MINERADOR] GARIMPANDO VITRINE PARA: {termo_busca} ---")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_busca.replace(' ', '-')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    try:
        response = requests.get(url_busca, impersonate="chrome110", headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'produto.mercadolivre.com.br/MLB-' in href or '/p/MLB' in href:
                url_limpa = href.split('#')[0].split('?')[0]
                if url_limpa not in links:
                    links.append(url_limpa)

        print(f"--- [MINERADOR] {len(links)} links encontrados. Filtrando os melhores... ---")

        produtos_aprovados = []

        # Analisa os links até encontrar 5 produtos perfeitos
        for url_p in links:
            if len(produtos_aprovados) >= 4: # Traz 4 opções para a sua vitrine
                break
                
            res_p = requests.get(url_p, impersonate="chrome110", headers=headers, timeout=30)
            if res_p.status_code != 200: continue
                
            html_p = res_p.text
            
            titulo_tag = BeautifulSoup(html_p, 'html.parser').find('h1', class_='ui-pdp-title')
            titulo = titulo_tag.text.strip() if titulo_tag else "Produto Promocional"
            
            preco_match = re.search(r'"price":\s*([\d\.]+)', html_p)
            if not preco_match:
                preco_match = re.search(r'itemprop="price" content="([\d\.]+)"', html_p)
            preco = float(preco_match.group(1)) if preco_match else 0.0
            
            imagens = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp|https://http2\.mlstatic\.com/D_NQ_NP_2X_[\w\-]+\.jpg', html_p)))

            if len(imagens) >= 2:
                produtos_aprovados.append({
                    "id": "MLB",
                    "titulo": titulo,
                    "preco": preco,
                    "url_original": url_p,
                    "midia": {"imagens_url": imagens[:6]}
                })
        
        return produtos_aprovados

    except Exception as e:
        print(f"--- [MINERADOR] Erro crítico: {e} ---")
        return []

