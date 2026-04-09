# modules/mineracao/ml_api.py
from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def buscar_produtos_tendencia(termo_busca):
    print(f"--- [MINERADOR] MODO IMPERSONATE (CHROME) ATIVADO: {termo_busca} ---")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_busca.replace(' ', '-')}"
    
    try:
        # A curl_cffi simula o comportamento exato do navegador Chrome
        response = requests.get(url_busca, impersonate="chrome110", timeout=30)
        
        if response.status_code != 200:
            print(f"--- [MINERADOR] Falha no acesso. Status: {response.status_code} ---")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # Captura links de produtos
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'produto.mercadolivre.com.br/MLB-' in href:
                url_limpa = href.split('#')[0].split('?')[0]
                if url_limpa not in links:
                    links.append(url_limpa)

        print(f"--- [MINERADOR] Sucesso! Encontrados {len(links)} links reais. ---")

        for url_p in links[:5]:
            print(f"--- [MINERADOR] Extraindo mídias de: {url_p[:40]}... ---")
            res_p = requests.get(url_p, impersonate="chrome110", timeout=30)
            
            if res_p.status_code != 200:
                continue
                
            html = res_p.text
            
            # Título
            titulo_match = re.search(r'<h1 class="ui-pdp-title">([^<]+)</h1>', html)
            titulo = titulo_match.group(1).strip() if titulo_match else "Produto"
            
            # Preço
            preco_match = re.search(r'"price":\s*([\d\.]+)', html)
            preco = float(preco_match.group(1)) if preco_match else 0.0
            
            # Imagens Reais (Alta Resolução)
            imagens = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp', html)))

            if len(imagens) >= 2:
                print(f"--- [MINERADOR] PRODUTO APROVADO: {titulo} ---")
                return [{
                    "id": "MLB",
                    "titulo": titulo,
                    "preco": preco,
                    "url_original": url_p,
                    "midia": {"imagens_url": imagens}
                }]
        
        return []

    except Exception as e:
        print(f"--- [MINERADOR] Erro crítico no motor Chrome: {e} ---")
        return []

