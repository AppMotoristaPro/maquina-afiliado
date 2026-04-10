# modules/afiliacao/gerador_links.py

def gerar_link_ml(url_original):
    """
    Limpa a URL capturada para você colar no gerador oficial do Mercado Livre.
    """
    url_limpa = url_original.split('#')[0].split('?')[0]
    return url_limpa

