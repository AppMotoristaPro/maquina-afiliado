# modules/mineracao/ml_api.py
import requests
import re
from bs4 import BeautifulSoup
from modules.mineracao.validador import produto_e_valido

def buscar_produtos_tendencia(termo_busca):
    print(f"Iniciando extração real para: {termo_busca}")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_busca.replace(' ', '-')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        res = requests.get(url_busca, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            if 'MLB-' in a['href'] and 'produto.mercadolivre' in a['href']:
                url = a['href'].split('#')[0].split('?')[0]
                if url not in links: links.append(url)
        
        for url_p in links[:5]: # Analisa os 5 primeiros para garantir qualidade
            res_p = requests.get(url_p, headers=headers, timeout=15)
            html = res_p.text
            
            # Extração de imagens de alta resolução (finais com _O.jpg ou _2X.jpg)
            # Este padrão captura as imagens reais da galeria do vendedor
            imagens = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp|https://http2\.mlstatic\.com/D_NQ_NP_2X_[\w\-]+\.jpg', html)))
            
            if len(imagens) < 3: continue
            
            # Captura de Preço e Título
            titulo = re.search(r'<h1 class="ui-pdp-title">([^<]+)</h1>', html)
            titulo = titulo.group(1).strip() if titulo else "Produto"
            
            preco_meta = re.search(r'<meta itemprop="price" content="([\d\.]+)"', html)
            if not preco_meta: continue
            preco = float(preco_meta.group(1))
            
            valido, _ = produto_e_valido(preco, 4.5, False, len(imagens))
            
            if valido:
                print(f"[CONECTADO] {titulo}")
                return [{
                    "id": "MLB",
                    "titulo": titulo,
                    "preco": preco,
                    "url_original": url_p,
                    "midia": {"imagens_url": imagens}
                }]
        return []
    except Exception as e:
        print(f"Erro na mineração: {e}")
        return []

