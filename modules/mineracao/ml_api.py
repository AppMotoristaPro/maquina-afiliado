# modules/mineracao/ml_api.py
import requests
import re
from bs4 import BeautifulSoup

def buscar_produtos_tendencia(termo_busca):
    print(f"--- [MINERADOR] Iniciando busca real para: {termo_busca} ---")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_busca.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    try:
        res = requests.get(url_busca, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Captura links de forma mais flexível
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'MLB-' in href and 'produto.mercadolivre.com.br' in href:
                url_limpa = href.split('#')[0].split('?')[0]
                if url_limpa not in links: links.append(url_limpa)

        print(f"--- [MINERADOR] Encontrados {len(links)} candidatos. Analisando... ---")

        for url_p in links[:8]: # Analisa os 8 primeiros
            res_p = requests.get(url_p, headers=headers, timeout=15)
            html = res_p.text
            
            # Título e Preço
            titulo = re.search(r'<h1 class="ui-pdp-title">([^<]+)</h1>', html)
            titulo = titulo.group(1).strip() if titulo else "Produto"
            
            preco_match = re.search(r'<meta itemprop="price" content="([\d\.]+)"', html)
            preco = float(preco_match.group(1)) if preco_match else 0.0
            
            # Imagens: Buscamos o padrão de alta resolução (-O.webp ou -F.webp)
            imagens = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-[OF]\.webp', html)))
            
            # --- LOG DE VALIDAÇÃO (Para sabermos por que falha) ---
            if preco < 30: # Baixei o limite para teste
                print(f" -> Ignorado: {titulo[:20]}... (Preço R$ {preco} muito baixo)")
                continue
            if len(imagens) < 2:
                print(f" -> Ignorado: {titulo[:20]}... (Fotos insuficientes: {len(imagens)})")
                continue
            
            print(f"--- [MINERADOR] SUCESSO! APROVADO: {titulo} ---")
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

