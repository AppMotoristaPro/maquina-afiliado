# modules/afiliacao/gerador_links.py
import urllib.parse
from config import AFILIADO_ID_ML

def gerar_link_ml(url_original):
    """
    Limpa a URL original e injeta os parâmetros de rastreamento do afiliado.
    """
    # 1. Limpa a URL original (remove parâmetros de pesquisa antigos que o ML coloca)
    url_limpa = url_original.split("?")[0].split("#")[0]
    
    # 2. Monta os parâmetros de afiliado
    parametros_afiliado = {
        "camp": "afiliado",
        "af_id": AFILIADO_ID_ML,
        "origem": "automacao_python"
    }
    
    # 3. Codifica os parâmetros e junta com a URL limpa
    query_string = urllib.parse.urlencode(parametros_afiliado)
    link_final = f"{url_limpa}?{query_string}"
    
    return link_final


