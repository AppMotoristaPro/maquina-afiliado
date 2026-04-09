# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image
import PIL.ImageFilter
import numpy as np
import json

os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip

def baixar_midia(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    caminhos = []
    for i, url in enumerate(produto['midia']['imagens_url'][:4]):
        try:
            r = requests.get(url, timeout=10)
            caminho = os.path.join(pasta_destino, f"img_{i}.jpg")
            with open(caminho, 'wb') as f: f.write(r.content)
            caminhos.append(caminho)
        except: continue
    return caminhos

def criar_video_reels(caminhos_imagens, caminho_audio=None, caminho_legenda=None, nome_saida="reels_final.mp4", logger=print):
    W, H = 480, 854 
    clips = []

    try:
        # 1. Montagem do Fundo
        for img_path in caminhos_imagens:
            img_pil = PIL.Image.open(img_path).convert("RGB")
            bg_pil = img_pil.resize((W, H), PIL.Image.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(10))
            bg_clip = ImageClip(np.array(bg_pil)).set_duration(3.0)
            fg_clip = ImageClip(img_path).set_duration(3.0).resize(width=W-40).set_position("center")
            clips.append(CompositeVideoClip([bg_clip, fg_clip], size=(W, H)))

        video = concatenate_videoclips(clips, method="compose")

        # 2. Inserção do Áudio principal
        if caminho_audio and os.path.exists(caminho_audio):
            voz = AudioFileClip(caminho_audio)
            video = video.set_audio(voz).set_duration(voz.duration)

        # 3. MÁGICA: Legendas Dinâmicas Palavra por Palavra
        try:
            if caminho_legenda and os.path.exists(caminho_legenda):
                legenda_clips = []
                with open(caminho_legenda, "r", encoding="utf-8") as f:
                    legendas = json.load(f)
                    
                for leg in legendas:
                    # Filtra pontuações sozinhas que a IA às vezes separa
                    if len(leg["text"].strip()) < 2 and leg["text"].strip() not in ["e", "a", "o", "é", "ó"]:
                        continue
                    
                    # Cria a palavra no estilo TikTok (Amarelo com borda)
                    txt_clip = TextClip(
                        leg["text"], 
                        fontsize=65, 
                        color='yellow', 
                        stroke_color='black', 
                        stroke_width=2.5
                    ).set_position(('center', int(H * 0.7))) # Coloca na parte de baixo da tela
                    
                    # Define exatamente em qual milissegundo a palavra aparece e some
                    txt_clip = txt_clip.set_start(leg["start"]).set_end(leg["end"])
                    legenda_clips.append(txt_clip)

                # Junta o vídeo com todas as palavras pipocando
                if legenda_clips:
                    video = CompositeVideoClip([video] + legenda_clips)
        except Exception as e:
            logger(f"--- [AVISO] Falha ao gerar legendas, seguindo sem elas: {e} ---")

        logger("--- [EDITOR] Iniciando gravação do arquivo... ---")
        video.write_videofile(
            nome_saida, 
            fps=20, 
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast",
            threads=1,
            logger=None
        )
        video.close()
        return nome_saida
        
    except Exception as e:
        logger(f"--- [EDITOR] ERRO CRÍTICO NA EDIÇÃO: {e} ---")
        return None

