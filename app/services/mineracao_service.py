from curl_cffi import requests
from bs4 import BeautifulSoup
import re
from app.models.produto import Produto

# Categorias globais do Mercado Livre em alta
CATEGORIAS = [
    "celulares-smartphones", 
    "eletrodomesticos", 
    "beleza-cuidado-pessoal", 
    "informatica",
    "joias-relogios"
]

def garimpar_produtos():
    resultados = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
    
    # Faz uma varredura em todas as categorias
    for cat in CATEGORIAS:
        url_busca = f"https://lista.mercadolivre.com.br/{cat}#tendencias"
        try:
            res = requests.get(url_busca, impersonate="chrome110", headers=headers, timeout=30)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Pega links oficiais da categoria
            links = [a['href'].split('#')[0].split('?')[0] for a in soup.find_all('a', href=True) if 'produto.mercadolivre.com.br/MLB-' in a['href'] or '/p/MLB' in a['href']]
            
            itens_encontrados_nesta_categoria = 0
            
            for url_p in list(set(links)):
                if itens_encontrados_nesta_categoria >= 2: break # Limite: 2 por categoria
                
                # --- VERIFICAÇÃO NO BANCO DE DADOS (Não repete itens já feitos) ---
                ja_processado = Produto.query.filter_by(url_original=url_p).first()
                if ja_processado:
                    continue

                rp = requests.get(url_p, impersonate="chrome110", headers=headers, timeout=30)
                soup_p = BeautifulSoup(rp.text, 'html.parser')
                
                # --- FILTRO ANTILIXO: Busca apenas na Galeria Oficial ---
                # A classe 'ui-pdp-gallery' contém apenas as fotos de capa, isolando as fotos de avaliações.
                galeria = soup_p.find('div', class_='ui-pdp-gallery')
                if not galeria: continue
                
                titulo = soup_p.find('h1').text.strip() if soup_p.find('h1') else "Produto Oferta"
                preco_match = re.search(r'"price":\s*([\d\.]+)', rp.text)
                preco = float(preco_match.group(1)) if preco_match else 0.0
                
                # Extrai as imagens de alta qualidade apenas de dentro do HTML da galeria
                imgs = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-[OF]\.webp', str(galeria))))
                
                if len(imgs) >= 2:
                    resultados.append({
                        "titulo": titulo, 
                        "preco": preco, 
                        "url": url_p, 
                        "imagens": imgs[:4] # Pega até 4 fotos oficiais
                    })
                    itens_encontrados_nesta_categoria += 1
                    
        except Exception as e:
            print(f"Erro ao varrer categoria {cat}: {e}")
            continue
            
    return resultados

