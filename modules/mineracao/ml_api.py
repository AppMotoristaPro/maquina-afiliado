# modules/mineracao/ml_api.py
from curl_cffi import requests
from bs4 import BeautifulSoup
import re
from modules.mineracao.validador import produto_e_valido

def buscar_produtos_tendencia(termo_busca):
    print(f"Iniciando mineração profissional (Imitação de TLS Chrome) para: '{termo_busca}'...")
    
    termo_formatado = termo_busca.replace(" ", "-")
    url_scraping = f"https://lista.mercadolivre.com.br/{termo_formatado}"
    
    # A curl_cffi usa o parâmetro 'impersonate' para copiar exatamente o comportamento do Chrome
    try:
        response = requests.get(
            url_scraping, 
            impersonate="chrome110", # Aqui está o segredo para furar o WAF
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Falha no acesso inicial. Status: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        links_unicos = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if 'produto.mercadolivre.com.br/MLB' in href or 'mercadolivre.com.br/p/MLB' in href:
                url_limpa = href.split('?')[0].split('#')[0]
                if url_limpa not in links_unicos:
                    links_unicos.append(url_limpa)

        if not links_unicos:
            print("Página carregada, mas nenhum link identificado. O layout pode ter mudado.")
            return []

        print(f"Sucesso! {len(links_unicos)} links capturados. Analisando mídias...")
        produtos_aprovados = []

        for url_produto in links_unicos:
            res_item = requests.get(url_produto, impersonate="chrome110")
            if res_item.status_code != 200:
                continue

            html = res_item.text
            item_soup = BeautifulSoup(html, 'html.parser')

            # Extração de dados
            titulo_tag = item_soup.find('h1', class_='ui-pdp-title')
            titulo = titulo_tag.text.strip() if titulo_tag else "Produto"

            preco_tag = item_soup.find('meta', itemprop='price')
            if not preco_tag: continue
            preco = float(preco_tag['content'])

            imagens = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_2X_[\w\-]+\.(?:jpg|webp)', html)))
            possui_video = 'video_id' in html or 'youtube.com/embed' in html

            valido, motivo = produto_e_valido(preco, 4.8, possui_video, len(imagens))

            if valido:
                produtos_aprovados.append({
                    "id": "MLB" + re.search(r'MLB-?(\d+)', url_produto).group(1),
                    "titulo": titulo,
                    "preco": preco,
                    "url_original": url_produto,
                    "midia": {"possui_video": possui_video, "imagens_url": imagens}
                })
                print(f"[APROVADO] {titulo}")
                break
            else:
                print(f"[REPROVADO] {titulo[:20]}... - {motivo}")

        return produtos_aprovados

    except Exception as e:
        print(f"Erro crítico no motor de mineração: {e}")
        return []

