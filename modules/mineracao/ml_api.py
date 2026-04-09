# modules/mineracao/ml_api.py
import requests
import re
from bs4 import BeautifulSoup
from modules.mineracao.validador import produto_e_valido

def buscar_produtos_tendencia(termo_busca):
    print(f"--- [MINERADOR] Iniciando busca para: {termo_busca} ---")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_busca.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(url_busca, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Busca links de forma mais abrangente
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'MLB-' in href and 'produto.mercadolivre.com.br' in href:
                url_limpa = href.split('#')[0].split('?')[0]
                if url_limpa not in links:
                    links.append(url_limpa)

        print(f"--- [MINERADOR] Encontrados {len(links)} links potenciais ---")

        for url_p in links[:10]: # Analisa os 10 primeiros para achar um bom
            res_p = requests.get(url_p, headers=headers, timeout=15)
            html = res_p.text
            
            # Título e Preço
            titulo_match = re.search(r'<h1 class="ui-pdp-title">([^<]+)</h1>', html)
            titulo = titulo_match.group(1).strip() if titulo_match else "Produto sem título"
            
            preco_match = re.search(r'<meta itemprop="price" content="([\d\.]+)"', html)
            preco = float(preco_match.group(1)) if preco_match else 0.0
            
            # Imagens: Pegamos o maior tamanho disponível (_O.webp ou _2X.jpg)
            imagens = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp|https://http2\.mlstatic\.com/D_NQ_NP_2X_[\w\-]+\.jpg', html)))
            
            # Validação manual detalhada no log para sabermos o que ocorre
            if preco < 50:
                print(f" -> Recusado: {titulo[:20]}... (Preço R$ {preco} muito baixo)")
                continue
            if len(imagens) < 3:
                print(f" -> Recusado: {titulo[:20]}... (Poucas imagens: {len(imagens)})")
                continue
            
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
        print(f"--- [MINERADOR] Erro crítico: {e} ---")
        return []

