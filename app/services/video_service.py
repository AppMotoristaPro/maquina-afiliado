import os
import requests
import PIL.Image, PIL.ImageFilter, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

def renderizar_video(imagens_urls, audio_path, json_path, logger):
    W, H = 480, 854
    clips = []
    logger("--- [EDITOR] Baixando Imagens ---")
    for i, url in enumerate(imagens_urls[:4]):
        img_data = requests.get(url).content
        with open(f"downloads/i_{i}.jpg", "wb") as f: f.write(img_data)
        
        img = PIL.Image.open(f"downloads/i_{i}.jpg").convert("RGB")
        bg = img.resize((W,H), PIL.Image.Resampling.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(15))
        fg = img.resize((W-40, int((W-40)*(img.height/img.width))), PIL.Image.Resampling.LANCZOS)
        
        final_slide = PIL.Image.fromarray(np.array(bg))
        final_slide.paste(fg, (20, (H-fg.height)//2))
        clips.append(ImageClip(np.array(final_slide)).set_duration(3.0))

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio).set_duration(audio.duration)

    # Legendas dinâmicas com Pillow (Bypass ImageMagick)
    logger("--- [EDITOR] Aplicando Legendas ---")
    with open(json_path, "r") as f: data = json.load(f)
    leg_clips = []
    for item in data:
        txt = item["text"].upper()
        if len(txt) < 2: continue
        canvas = PIL.Image.new("RGBA", (W, 100), (0,0,0,0))
        draw = PIL.ImageDraw.Draw(canvas)
        draw.text((W//2, 50), txt, fill="yellow", stroke_width=2, stroke_fill="black", anchor="mm")
        l_clip = ImageClip(np.array(canvas)).set_start(item["start"]).set_end(item["end"]).set_position(("center", H-150))
        leg_clips.append(l_clip)

    final_video = CompositeVideoClip([video] + leg_clips)
    final_video.write_videofile("reels_final.mp4", fps=20, codec="libx264", preset="ultrafast", logger=None)
    return "reels_final.mp4"
