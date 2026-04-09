# app.py
from modules.mineracao.ml_api import buscar_produtos_tendencia
from modules.afiliacao.gerador_links import gerar_link_ml
from modules.conteudo.editor_video import baixar_midia, criar_video_reels
from modules.conteudo.locucao import gerar_audio_narracao
import sys

def iniciar():
    try:
        print("--- [BOT] Buscando produtos... ---")
        produtos = buscar_produtos_tendencia("smartwatch")
        
        if not produtos:
            print("--- [BOT] Nenhum produto encontrado ou aprovado ---")
            return

        p = produtos[0]
        print(f"--- [BOT] Processando: {p['titulo']} ---")
        
        link = gerar_link_ml(p['url_original'])
        imagens = baixar_midia(p)
        
        if not imagens:
            print("--- [BOT] Falha ao baixar imagens reais ---")
            return
            
        audio = gerar_audio_narracao(p)
        print("--- [BOT] Iniciando montagem do vídeo... ---")
        
        video = criar_video_reels(imagens, caminho_audio=audio)
        print(f"--- [BOT] VÍDEO PRONTO: {video} ---")
        
    except Exception as e:
        print(f"--- [ERRO EM iniciar()] {e} ---")
        # Força a exibição do erro no log do Render
        sys.stdout.flush() 

