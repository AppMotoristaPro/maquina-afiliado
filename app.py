# app.py
from modules.mineracao.ml_api import buscar_produtos_tendencia
from modules.afiliacao.gerador_links import gerar_link_ml
from modules.conteudo.editor_video import baixar_midia, criar_video_reels
from modules.conteudo.locucao import gerar_audio_narracao
import json

def iniciar(logger):
    logger("=== [SISTEMA] INICIANDO MODO DE TESTE TOTAL ===")
    
    produtos = buscar_produtos_tendencia("smartwatch")
    
    if not produtos:
        logger("=== [SISTEMA] ERRO: O Mercado Livre não retornou produtos válidos ===")
        return

    p = produtos[0]
    logger(f"--- [MINERADOR] PRODUTO APROVADO: {p['titulo'][:30]}... ---")
    
    # Gera o link
    link_afiliado = gerar_link_ml(p['url_original'])
    
    # Cria a copy
    preco_formatado = str(p['preco']).replace(".", ",")
    copy_post = f"🚨 Achado imperdível!\n\n{p['titulo']}\n\nDeixe um 'EU QUERO' nos comentários que te envio o link no Direct, ou acesse pelo link da bio!\n\n🔗 Link: {link_afiliado}"
    
    # Salva para o Dashboard ler
    info_dict = {"titulo": p['titulo'], "link": link_afiliado, "descricao": copy_post}
    with open("produto_info.json", "w", encoding="utf-8") as f:
        json.dump(info_dict, f)

    logger("=== [SISTEMA] Baixando imagens do produto... ===")
    imagens = baixar_midia(p)
    
    if imagens:
        logger("--- [VOZ] Gerando narração... ---")
        audio = gerar_audio_narracao(p)
        
        logger("=== [SISTEMA] Montando vídeo com MÚSICA e LEGENDA... ===")
        video_gerado = criar_video_reels(caminhos_imagens=imagens, caminho_audio=audio, logger=logger)
        
        if video_gerado:
            logger("=== [SISTEMA] VÍDEO PRONTO! Acesse a página /video ===")
        else:
            logger("=== [SISTEMA] Falha na renderização do vídeo ===")
    else:
        logger("=== [SISTEMA] Erro no download das fotos ===")


