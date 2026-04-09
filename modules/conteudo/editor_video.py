# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image
import PIL.ImageFilter
import numpy as np

# PATCH DE COMPATIBILIDADE PARA VERSÕES NOVAS DO PILLOW
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

def baixar_midia(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    caminhos = []
    for i, url in enumerate(produto['midia']['imagens_url'][:5]):
        try:
            r = requests.get(url, timeout=10)
            caminho = os.path.join(pasta_destino, f"img_{i}.jpg")
            with open(caminho, 'wb') as f: f.write(r.content)
            caminhos.append(caminho)
        except: continue
    return caminhos

def criar_video_reels(caminhos_imagens, caminho_audio=None, nome_saida="reels_final.mp4"):
    print("--- [EDITOR] Renderizando formato Vertical Cinematic ---")
    clips = []
    W, H = 720, 1280 

    for img_path in caminhos_imagens:
        img_pil = PIL.Image.open(img_path).convert("RGB")
        
        # Fundo desfocado
        bg_pil = img_pil.resize((W, H), PIL.Image.ANTIALIAS).filter(PIL.ImageFilter.GaussianBlur(20))
        bg_clip = ImageClip(np.array(bg_pil)).set_duration(2.5)
        
        # Imagem principal
        fg_clip = ImageClip(img_path).set_duration(2.5).resize(width=W-60).set_position("center")
        
        clips.append(CompositeVideoClip([bg_clip, fg_clip], size=(W, H)))

    video = concatenate_videoclips(clips, method="compose")
    if caminho_audio and os.path.exists(caminho_audio):
        audio = AudioFileClip(caminho_audio)
        video = video.set_audio(audio).set_duration(audio.duration)
    
    video.write_videofile(nome_saida, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    return nome_saida

