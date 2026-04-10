from curl_cffi import requests
from bs4 import BeautifulSoup
import re
from app.models.produto import Produto

CATEGORIAS = ["celulares-smartphones", "eletrodomesticos", "beleza-cuidado-pessoal", "informatica", "games"]

def garimpar_produtos():
    resultados = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
    
    for cat in CATEGORIAS:
        url_busca = f"https://lista.mercadolivre.com.br/{cat}#tendencias"
        try:
            res = requests.get(url_busca, impersonate="chrome110", headers=headers, timeout=30)
            soup = BeautifulSoup(res.text, 'html.parser')
            links = [a['href'].split('#')[0].split('?')[0] for a in soup.find_all('a', href=True) if 'produto.mercadolivre.com.br/MLB-' in a['href'] or '/p/MLB' in a['href']]
            
            itens_categoria = 0
            for url_p in list(set(links)):
                if itens_categoria >= 2: break
                if Produto.query.filter_by(url_original=url_p).first(): continue

                rp = requests.get(url_p, impersonate="chrome110", headers=headers, timeout=30)
                soup_p = BeautifulSoup(rp.text, 'html.parser')
                galeria = soup_p.find('div', class_='ui-pdp-gallery')
                if not galeria: continue
                
                titulo = soup_p.find('h1').text.strip() if soup_p.find('h1') else "Oferta"
                preco_match = re.search(r'"price":\s*([\d\.]+)', rp.text)
                preco = float(preco_match.group(1)) if preco_match else 0.0
                
                # Pegamos as 6 primeiras imagens (geralmente as fotos de estúdio)
                # O filtro 'D_NQ_NP_[\w\-]+-F\.webp' foca em imagens de alta definição
                imgs = re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp', str(galeria))
                imgs = list(dict.fromkeys(imgs)) # Remove duplicatas mantendo a ordem

                if len(imgs) >= 3:
                    resultados.append({
                        "titulo": titulo, "preco": preco, "url": url_p, "imagens": imgs[:6]
                    })
                    itens_categoria += 1
        except: continue
    return resultados

