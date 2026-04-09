# app.py
from modules.mineracao.ml_api import buscar_produtos_tendencia
from modules.afiliacao.gerador_links import gerar_link_ml
from modules.conteudo.editor_video import baixar_midia, criar_video_reels
from modules.conteudo.locucao import gerar_audio_narracao

def iniciar():
    print("=== [SISTEMA] INICIANDO CICLO DE PRODUÇÃO NO RENDER ===")
    
    # Tente um nicho com muita oferta para garantir o primeiro teste
    produtos = buscar_produtos_tendencia("smartwatch amoled")
    
    if not produtos:
        print("=== [SISTEMA] FIM: Nenhum produto passou nos critérios ===")
        return

    p = produtos[0]
    # Aqui garantimos que pegamos as imagens reais
    caminhos_imagens = baixar_midia(p)
    
    if caminhos_imagens:
        audio = gerar_audio_narracao(p)
        print("=== [SISTEMA] Montando Reels Cinematic... ===")
        video_gerado = criar_video_reels(caminhos_imagens, caminho_audio=audio)
        print(f"=== [SISTEMA] SUCESSO: {video_gerado} gerado! ===")
    else:
        print("=== [SISTEMA] ERRO: Falha ao processar imagens do produto ===")

