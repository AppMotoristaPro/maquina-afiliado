import os
import requests
import PIL.Image, PIL.ImageFilter, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
import gc
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

# Patch ImageMagick/Pillow
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

def renderizar_video(imagens_urls, audio_path, json_path, logger):
    W, H = 360, 640 # Resolução reduzida agressivamente para evitar Out Of Memory no Render
    clips = []
    
    logger("--- [EDITOR] Baixando Imagens ---")
    for i, url in enumerate(imagens_urls[:4]):
        img_data = requests.get(url).content
        with open(f"downloads/i_{i}.jpg", "wb") as f: f.write(img_data)
        
        img = PIL.Image.open(f"downloads/i_{i}.jpg").convert("RGB")
        bg = img.resize((W,H), PIL.Image.Resampling.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(15))
        fg = img.resize((W-30, int((W-30)*(img.height/img.width))), PIL.Image.Resampling.LANCZOS)
        
        final_slide = PIL.Image.fromarray(np.array(bg))
        final_slide.paste(fg, (15, (H-fg.height)//2))
        
        clip = ImageClip(np.array(final_slide)).set_duration(3.0)
        clips.append(clip)
        
        # Libera memória imediatamente
        del img, bg, fg, final_slide
        gc.collect()

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio).set_duration(audio.duration)

    logger("--- [EDITOR] Aplicando Legendas ---")
    with open(json_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    leg_clips = []
    for item in data:
        txt = item["text"].upper()
        if len(txt) < 2 and txt not in ["E", "A", "O", "É", "Ó"]: continue
        
        canvas = PIL.Image.new("RGBA", (W, 100), (0,0,0,0))
        draw = PIL.ImageDraw.Draw(canvas)
        # Fonte default para não depender de pacotes externos
        fonte = PIL.ImageFont.load_default() 
        draw.text((W//2, 50), txt, font=fonte, fill="yellow", stroke_width=2, stroke_fill="black", anchor="mm")
        
        l_clip = ImageClip(np.array(canvas)).set_start(item["start"]).set_end(item["end"]).set_position(("center", H-150))
        leg_clips.append(l_clip)

    if leg_clips:
        video = CompositeVideoClip([video] + leg_clips)

    logger("--- [EDITOR] Gravando arquivo (FPS=15)... ---")
    # Forçar fps baixo e preset muito rápido para estabilidade de servidor
    video.write_videofile("reels_final.mp4", fps=15, codec="libx264", preset="ultrafast", threads=1, logger=None)
    
    video.close()
    audio.close()
    gc.collect()
    
    return "reels_final.mp4"

