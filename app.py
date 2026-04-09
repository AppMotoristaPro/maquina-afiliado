# app.py
from modules.mineracao.ml_api import buscar_produtos_tendencia
from modules.afiliacao.gerador_links import gerar_link_ml
from modules.conteudo.editor_video import baixar_midia, criar_video_reels
from modules.conteudo.locucao import gerar_audio_narracao
import os

def iniciar():
    print("=== [SISTEMA] INICIANDO MODO DE TESTE TOTAL ===")
    
    # Use um termo bem comum para garantir resultados
    produtos = buscar_produtos_tendencia("relogio")
    
    if not produtos:
        print("=== [SISTEMA] ERRO: O Mercado Livre bloqueou a leitura do HTML no Render. ===")
        return

    p = produtos[0]
    link = gerar_link_ml(p['url_original'])
    
    print(f"=== [SISTEMA] Baixando mídias de: {p['titulo']} ===")
    imagens = baixar_midia(p)
    
    if imagens:
        audio = gerar_audio_narracao(p)
        print("=== [SISTEMA] Iniciando renderização do vídeo... ===")
        video_gerado = criar_video_reels(imagens, caminho_audio=audio)
        print(f"=== [SISTEMA] PROCESSO FINALIZADO: {video_gerado} ===")
    else:
        print("=== [SISTEMA] ERRO: Não foi possível baixar as fotos capturadas. ===")

