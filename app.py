# app.py
from modules.conteudo.editor_video import baixar_midia, criar_video_reels
from modules.conteudo.locucao import gerar_audio_narracao
import json
import os

def gerar_video_selecionado(produto, link_afiliado, logger):
    """
    Função chamada pelo painel web quando você clica em "Criar Reels"
    """
    logger(f"=== [SISTEMA] INICIANDO PRODUÇÃO: {produto['titulo'][:30]} ===")
    
    # Prepara a Copy (Descrição) com o seu link oficial
    preco_formatado = str(produto['preco']).replace(".", ",")
    copy_post = f"🚨 Achado imperdível no Mercado Livre!\n\n{produto['titulo']}\n\nDeixe um 'EU QUERO' nos comentários que te envio o link no Direct, ou acesse pelo link da bio!\n\n🔗 Link: {link_afiliado}"
    
    # Salva para o Dashboard ler depois
    info_dict = {"titulo": produto['titulo'], "link": link_afiliado, "descricao": copy_post}
    with open("produto_info.json", "w", encoding="utf-8") as f:
        json.dump(info_dict, f)

    logger("--- [SISTEMA] Baixando imagens do produto... ---")
    imagens = baixar_midia(produto)
    
    if not imagens:
        logger("=== [ERRO] Falha ao baixar as imagens do Mercado Livre. ===")
        return False
        
    logger("--- [VOZ] Gerando narração e arquivo de legendas... ---")
    audio, legenda = gerar_audio_narracao(produto)
    
    logger("=== [SISTEMA] Montando vídeo (Isso leva alguns minutos)... ===")
    video_gerado = criar_video_reels(
        caminhos_imagens=imagens, 
        caminho_audio=audio, 
        caminho_legenda=legenda, 
        logger=logger
    )
    
    if video_gerado:
        logger("=== [SUCESSO] VÍDEO PRONTO PARA DOWNLOAD! ===")
        return True
    else:
        logger("=== [ERRO] Falha na renderização do vídeo. ===")
        return False

