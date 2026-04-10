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
    duration_per_img = total_duration / len(imagens_urls[:6])

    set_progresso(30, "Baixando imagens oficiais...")
    for i, url in enumerate(imagens_urls[:6]):
        img_data = requests.get(url).content
        temp_img = f"downloads/i_{i}.jpg"
        with open(temp_img, "wb") as f: f.write(img_data)
        
        img = PIL.Image.open(temp_img).convert("RGB")
        bg = img.resize((W,H), PIL.Image.Resampling.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(20))
        fg_w = W - 40
        fg_h = int(fg_w * (img.height / img.width))
        fg = img.resize((fg_w, fg_h), PIL.Image.Resampling.LANCZOS)
        
        final_slide = bg.copy()
        final_slide.paste(fg, (20, (H - fg_h) // 2))
        
        clips.append(ImageClip(np.array(final_slide)).set_duration(duration_per_img))
        
        del img, bg, fg, final_slide
        gc.collect()

    set_progresso(60, "Montando o vídeo base...")
    video = concatenate_videoclips(clips, method="compose").set_audio(audio)
    
    # 1. Gera o vídeo temporário (Sem as legendas)
    temp_video = "downloads/temp_video.mp4"
    video.write_videofile(temp_video, fps=15, codec="libx264", preset="ultrafast", logger=None)
    
    video.close()
    audio.close()
    gc.collect()

    set_progresso(85, "Queimando legendas nativas com FFmpeg...")
    
    # 2. Chama o FFMPEG para fixar a legenda.vtt na tela
    # A fonte será Arial, 24px, cor principal Amarela (00FFFF) com borda Preta (000000) e alinhamento central em baixo (MarginV=40)
    estilo = "FontName=Arial,FontSize=24,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=40"
    
    # Ajuste de caminho para não dar erro no comando bash
    vtt_path_safe = vtt_path.replace("\\", "/")
    
    cmd = [
        "ffmpeg", "-y", 
        "-i", temp_video, 
        "-vf", f"subtitles={vtt_path_safe}:force_style='{estilo}'", 
        "-c:a", "copy", 
        "reels_final.mp4"
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Erro no FFMPEG: {e}")

    return "reels_final.mp4"

