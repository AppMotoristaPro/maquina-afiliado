from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def garimpar_produtos(termo):
    url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
    try:
        res = requests.get(url, impersonate="chrome110", headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = [a['href'].split('#')[0].split('?')[0] for a in soup.find_all('a', href=True) if 'produto.mercadolivre.com.br/MLB-' in a['href'] or '/p/MLB' in a['href']]
        
        resultados = []
        for url_p in list(set(links))[:8]:
            if len(resultados) >= 4: break
            rp = requests.get(url_p, impersonate="chrome110", timeout=30)
            soup_p = BeautifulSoup(rp.text, 'html.parser')
            titulo = soup_p.find('h1').text.strip() if soup_p.find('h1') else "Produto"
            preco = float(re.search(r'"price":\s*([\d\.]+)', rp.text).group(1)) if re.search(r'"price":\s*([\d\.]+)', rp.text) else 0.0
            imgs = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp', rp.text)))
            if len(imgs) >= 2:
                resultados.append({"titulo": titulo, "preco": preco, "url": url_p, "imagens": imgs[:6]})
        return resultados
    except: return []
