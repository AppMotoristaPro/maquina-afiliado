# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image
import PIL.ImageFilter
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

def baixar_midia(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    caminhos = []
    print(f"--- [EDITOR] Baixando {len(produto['midia']['imagens_url'])} imagens reais ---")
    
    for i, url in enumerate(produto['midia']['imagens_url'][:5]):
        try:
            r = requests.get(url, timeout=10)
            caminho = os.path.join(pasta_destino, f"img_{i}.jpg")
            with open(caminho, 'wb') as f: f.write(r.content)
            caminhos.append(caminho)
        except: continue
    return caminhos

def criar_video_reels(caminhos_imagens, caminho_audio=None, nome_saida="reels_final.mp4"):
    print("--- [EDITOR] Renderizando formato Vertical Cinematic... ---")
    clips = []
    L, A = 720, 1280 # Formato Reels

    for img_path in caminhos_imagens:
        # Fundo desfocado
        bg = ImageClip(img_path).set_duration(2.5).resize(height=A)
        if bg.w < L: bg = bg.resize(width=L)
        bg = bg.fl_image(lambda image: PIL.Image.fromarray(image).filter(PIL.ImageFilter.GaussianBlur(15)).convert("RGB"))
        bg = bg.set_position("center")

        # Imagem principal
        fg = ImageClip(img_path).set_duration(2.5).resize(width=L-60).set_position("center")
        
        clips.append(CompositeVideoClip([bg, fg], size=(L, A)))

    video = concatenate_videoclips(clips, method="compose")
    if caminho_audio and os.path.exists(caminho_audio):
        audio = AudioFileClip(caminho_audio)
        video = video.set_audio(audio).set_duration(audio.duration)
    
    video.write_videofile(nome_saida, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    return nome_saida

