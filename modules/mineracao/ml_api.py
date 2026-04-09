# modules/mineracao/ml_api.py
from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def buscar_produtos_tendencia(termo_busca):
    print(f"--- [MINERADOR] TENTATIVA TOTAL: {termo_busca} ---")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_busca.replace(' ', '-')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url_busca, impersonate="chrome110", headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # DEBUG: O que o bot está vendo?
        pagina_titulo = soup.title.string if soup.title else "Sem Título"
        print(f"--- [DEBUG] Título da página recebida: {pagina_titulo} ---")

        links = []
        # Busca agressiva em todos os links da página
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'MLB-' in href or '/p/MLB' in href:
                if 'mercadolivre.com.br' in href:
                    links.append(href.split('#')[0].split('?')[0])

        links = list(set(links))
        print(f"--- [MINERADOR] Encontrados {len(links)} links. ---")

        for url_p in links[:10]:
            print(f"--- [MINERADOR] Entrando em: {url_p[:50]} ---")
            res_p = requests.get(url_p, impersonate="chrome110", timeout=30)
            html_p = res_p.text
            
            # Pega QUALQUER imagem
            imagens = re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[^"\'\s>]+', html_p)
            imagens = [img for img in imagens if img.endswith(('.jpg', '.webp'))]
            imagens = list(set(imagens))

            # Título e Preço sem filtros
            titulo_tag = BeautifulSoup(html_p, 'html.parser').find('h1')
            titulo = titulo_tag.text.strip() if titulo_tag else "Produto Oferta"
            
            # CRITÉRIO ZERO: Achou imagem? Segue o jogo.
            if len(imagens) > 0:
                print(f"--- [MINERADOR] APROVADO: {titulo} ---")
                return [{
                    "id": "MLB",
                    "titulo": titulo,
                    "preco": 0.0, # Preço ignorado para o teste
                    "url_original": url_p,
                    "midia": {"imagens_url": imagens[:6]}
                }]
        
        return []
    except Exception as e:
        print(f"--- [MINERADOR] ERRO: {e} ---")
        return []

