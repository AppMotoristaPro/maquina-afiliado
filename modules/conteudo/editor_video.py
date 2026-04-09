# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image
import PIL.ImageFilter
import numpy as np

# Patch para corrigir o erro de versão do Pillow (ANTIALIAS -> LANCZOS)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

def baixar_midia(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    caminhos = []
    print(f"--- [EDITOR] Baixando imagens reais de: {produto['titulo'][:30]} ---")
    
    for i, url in enumerate(produto['midia']['imagens_url'][:5]):
        try:
            r = requests.get(url, timeout=10)
            caminho = os.path.join(pasta_destino, f"img_{i}.jpg")
            with open(caminho, 'wb') as f:
                f.write(r.content)
            caminhos.append(caminho)
        except:
            continue
    return caminhos

def criar_video_reels(caminhos_imagens, caminho_audio=None, nome_saida="reels_final.mp4"):
    print("--- [EDITOR] Iniciando renderização Cinematic (9:16) ---")
    clips = []
    W, H = 720, 1280 

    try:
        for img_path in caminhos_imagens:
            # 1. Carrega e prepara a imagem com Pillow
            img_pil = PIL.Image.open(img_path).convert("RGB")
            
            # 2. Fundo desfocado (Blur)
            # Usando Resampling.LANCZOS para evitar o erro de atributo
            bg_pil = img_pil.resize((W, H), PIL.Image.Resampling.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(20))
            bg_clip = ImageClip(np.array(bg_pil)).set_duration(2.5)
            
            # 3. Imagem central nítida
            fg_clip = ImageClip(img_path).set_duration(2.5).resize(width=W-60).set_position("center")
            
            # 4. Sobreposição
            slide = CompositeVideoClip([bg_clip, fg_clip], size=(W, H))
            clips.append(slide)

        video = concatenate_videoclips(clips, method="compose")
        
        if caminho_audio and os.path.exists(caminho_audio):
            audio = AudioFileClip(caminho_audio)
            video = video.set_audio(audio)
            # Garante que o vídeo não seja maior que a locução
            if video.duration > audio.duration:
                video = video.set_duration(audio.duration)
        
        video.write_videofile(
            nome_saida, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast",
            threads=2
        )
        
        video.close()
        return nome_saida
    except Exception as e:
        print(f"--- [EDITOR] ERRO NA RENDERIZAÇÃO: {e} ---")
        return None

