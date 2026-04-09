# app.py
from modules.mineracao.ml_api import buscar_produtos_tendencia
from modules.afiliacao.gerador_links import gerar_link_ml
from modules.conteudo.editor_video import baixar_midia, criar_video_reels
from modules.conteudo.locucao import gerar_audio_narracao
import json

def iniciar(logger=print):
    logger("=== [SISTEMA] INICIANDO CICLO (COM LEGENDA) ===")
    
    produtos = buscar_produtos_tendencia("smartwatch")
    
    if not produtos:
        logger("=== [SISTEMA] ERRO: O Mercado Livre bloqueou a busca ===")
        return

    p = produtos[0]
    logger(f"--- [MINERADOR] PRODUTO APROVADO: {p['titulo'][:30]}... ---")
    
    link_afiliado = gerar_link_ml(p['url_original'])
    copy_post = f"🚨 Achado imperdível!\n\n{p['titulo']}\n\nDeixe um 'EU QUERO' que te envio o link no Direct!\n\n🔗 Link: {link_afiliado}"
    
    info_dict = {"titulo": p['titulo'], "link": link_afiliado, "descricao": copy_post}
    with open("produto_info.json", "w", encoding="utf-8") as f:
        json.dump(info_dict, f)

    logger("=== [SISTEMA] Baixando imagens do produto... ===")
    imagens = baixar_midia(p)
    
    if imagens:
        logger("--- [VOZ] Gerando narração e legendas... ---")
        # Recebendo os dois arquivos
        audio, legenda = gerar_audio_narracao(p)
        
        logger("=== [SISTEMA] Montando vídeo com imagens e legendas dinâmicas... ===")
        video_gerado = criar_video_reels(
            caminhos_imagens=imagens, 
            caminho_audio=audio, 
            caminho_legenda=legenda, # Passando a legenda pro editor
            logger=logger
        )
        
        if video_gerado:
            logger("=== [SISTEMA] VÍDEO PRONTO! Acesse o painel. ===")
        else:
            logger("=== [SISTEMA] Falha na renderização ===")

