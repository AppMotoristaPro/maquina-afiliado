# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image
import PIL.ImageFilter
import numpy as np

# Patch definitivo de compatibilidade
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

def baixar_midia(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    caminhos = []
    # Usamos apenas as 4 primeiras imagens para garantir rapidez no teste
    for i, url in enumerate(produto['midia']['imagens_url'][:4]):
        try:
            r = requests.get(url, timeout=10)
            caminho = os.path.join(pasta_destino, f"img_{i}.jpg")
            with open(caminho, 'wb') as f: f.write(r.content)
            caminhos.append(caminho)
        except: continue
    return caminhos

def criar_video_reels(caminhos_imagens, caminho_audio=None, nome_saida="reels_final.mp4"):
    print("--- [EDITOR] Renderizando formato Vertical Otimizado ---")
    clips = []
    # Resolução otimizada para o Render Free (480p Vertical)
    W, H = 480, 854 

    try:
        for img_path in caminhos_imagens:
            img_pil = PIL.Image.open(img_path).convert("RGB")
            
            # Fundo desfocado
            bg_pil = img_pil.resize((W, H), PIL.Image.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(10))
            bg_clip = ImageClip(np.array(bg_pil)).set_duration(2.5)
            
            # Imagem principal centralizada
            fg_clip = ImageClip(img_path).set_duration(2.5).resize(width=W-40).set_position("center")
            
            clips.append(CompositeVideoClip([bg_clip, fg_clip], size=(W, H)))

        video = concatenate_videoclips(clips, method="compose")
        
        if caminho_audio and os.path.exists(caminho_audio):
            audio = AudioFileClip(caminho_audio)
            video = video.set_audio(audio)
            if video.duration > audio.duration:
                video = video.set_duration(audio.duration)
        
        # Escrevendo o arquivo com preset ultrafast para economizar CPU
        video.write_videofile(
            nome_saida, 
            fps=20, # 20 FPS é suficiente para Reels e economiza processamento
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast",
            threads=1 # Usar 1 thread evita picos de memória no Render
        )
        
        video.close()
        return nome_saida
    except Exception as e:
        print(f"--- [EDITOR] ERRO: {e} ---")
        return None

