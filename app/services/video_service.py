import os
import requests
import PIL.Image, PIL.ImageFilter
import numpy as np
import subprocess
import gc
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

def renderizar_video(imagens_urls, audio_path, vtt_path, set_progresso):
    W, H = 360, 640
    clips = []
    
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    # Garante que o vídeo dure o tempo exato do áudio, sem tela preta
    duration_per_img = total_duration / len(imagens_urls[:6])

    set_progresso(30, "Baixando fotos oficiais...")
    for i, url in enumerate(imagens_urls[:6]):
        img_data = requests.get(url).content
        temp_img = f"downloads/i_{i}.jpg"
        with open(temp_img, "wb") as f: f.write(img_data)
        
        img = PIL.Image.open(temp_img).convert("RGB")
        # Efeito Cinema: Fundo desfocado + Imagem centralizada
        bg = img.resize((W,H), PIL.Image.Resampling.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(20))
        fg_w = W - 40
        fg_h = int(fg_w * (img.height / img.width))
        fg = img.resize((fg_w, fg_h), PIL.Image.Resampling.LANCZOS)
        
        final_slide = bg.copy()
        final_slide.paste(fg, (20, (H - fg_h) // 2))
        
        clips.append(ImageClip(np.array(final_slide)).set_duration(duration_per_img))
        del img, bg, fg, final_slide
        gc.collect()

    set_progresso(60, "Montando Reels Base...")
    video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    
    temp_video = "downloads/temp_video.mp4"
    video.write_videofile(temp_video, fps=15, codec="libx264", preset="ultrafast", logger=None)
    
    video.close()
    audio.close()
    gc.collect()

    set_progresso(85, "Fixando Legendas Virais...")
    
    # IMPORTANTE: Removi o nome da fonte para o Linux usar a padrão e não falhar.
    # Aumentei o contorno (Outline) e a sombra para garantir visibilidade.
    estilo = "FontSize=22,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=60"
    
    # Comando FFmpeg com caminhos simplificados para o Linux do Render
    cmd = [
        "ffmpeg", "-y", 
        "-i", temp_video, 
        "-vf", f"subtitles={vtt_path}:force_style='{estilo}'", 
        "-c:a", "copy", 
        "reels_final.mp4"
    ]
    
    subprocess.run(cmd, check=True)
    return "reels_final.mp4"

