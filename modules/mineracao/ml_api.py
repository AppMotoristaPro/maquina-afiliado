# modules/mineracao/ml_api.py
from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def buscar_produtos_tendencia(termo_busca):
    """
    Realiza a mineração de produtos no Mercado Livre utilizando 
    o motor curl_cffi para contornar bloqueios de TLS Fingerprint.
    """
    print(f"--- [MINERADOR] MODO IMPERSONATE (CHROME) ATIVADO: {termo_busca} ---")
    
    # Formatação da URL de busca
    termo_formatado = termo_busca.replace(' ', '-')
    url_busca = f"https://lista.mercadolivre.com.br/{termo_formatado}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }

    try:
        # A curl_cffi simula o comportamento exato do navegador Chrome (Bypass WAF)
        response = requests.get(url_busca, impersonate="chrome110", headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"--- [MINERADOR] Falha no acesso inicial. Status: {response.status_code} ---")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Log de debug para verificar a integridade da página recebida
        pagina_titulo = soup.title.string if soup.title else "Sem Título"
        print(f"--- [DEBUG] Título da página capturada: {pagina_titulo} ---")

        links = []
        # Captura links de produtos (MLB) de forma abrangente no HTML
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Filtra links que apontam para páginas de produtos ou catálogo
            if 'produto.mercadolivre.com.br/MLB-' in href or '/p/MLB' in href:
                url_limpa = href.split('#')[0].split('?')[0]
                if url_limpa not in links:
                    links.append(url_limpa)

        print(f"--- [MINERADOR] Sucesso! Encontrados {len(links)} links potenciais. ---")

        # Analisa os primeiros links para extrair as mídias reais
        for url_p in links[:5]:
            print(f"--- [MINERADOR] Extraindo dados de: {url_p[:50]}... ---")
            res_p = requests.get(url_p, impersonate="chrome110", headers=headers, timeout=30)
            
            if res_p.status_code != 200:
                continue
                
            html_p = res_p.text
            
            # Extração do Título via Tag H1
            titulo_tag = BeautifulSoup(html_p, 'html.parser').find('h1', class_='ui-pdp-title')
            titulo = titulo_tag.text.strip() if titulo_tag else "Produto Promocional"
            
            # Extração do Preço via metadados ou JSON interno
            preco_match = re.search(r'"price":\s*([\d\.]+)', html_p)
            if not preco_match:
                preco_match = re.search(r'itemprop="price" content="([\d\.]+)"', html_p)
            preco = float(preco_match.group(1)) if preco_match else 0.0
            
            # Extração de Imagens em Alta Resolução (Padrões -O.webp e 2X.jpg)
            imagens = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp|https://http2\.mlstatic\.com/D_NQ_NP_2X_[\w\-]+\.jpg', html_p)))

            # Critério de Aceitação: Se houver pelo menos 2 imagens, o produto é aprovado
            if len(imagens) >= 2:
                print(f"--- [MINERADOR] PRODUTO APROVADO: {titulo} ---")
                return [{
                    "id": "MLB",
                    "titulo": titulo,
                    "preco": preco,
                    "url_original": url_p,
                    "midia": {"imagens_url": imagens[:8]} # Captura até 8 imagens para o carrossel
                }]
        
        print("--- [MINERADOR] Nenhum produto com mídias suficientes foi validado. ---")
        return []

    except Exception as e:
        print(f"--- [MINERADOR] Erro crítico no motor Chrome: {e} ---")
        return []

