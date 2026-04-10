import os
import requests
import PIL.Image, PIL.ImageFilter, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
import gc
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

def baixar_fonte():
    font_path = "downloads/font.ttf"
    if not os.path.exists(font_path):
        url = "https://github.com/google/fonts/raw/main/apache/robotocondensed/RobotoCondensed-Bold.ttf"
        r = requests.get(url)
        with open(font_path, "wb") as f: f.write(r.content)
    return font_path

def renderizar_video(imagens_urls, audio_path, json_path, logger):
    W, H = 360, 640
    clips = []
    
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration
    # Calcula o tempo de cada imagem para o vídeo nunca ficar preto
    duration_per_img = total_duration / len(imagens_urls[:6])
    
    font_p = baixar_fonte()

    logger("--- [EDITOR] Processando Imagens Orgânicas ---")
    for i, url in enumerate(imagens_urls[:6]):
        img_data = requests.get(url).content
        temp_img = f"downloads/i_{i}.jpg"
        with open(temp_img, "wb") as f: f.write(img_data)
        
        img = PIL.Image.open(temp_img).convert("RGB")
        # Criando o fundo desfocado estendido
        bg = img.resize((W,H), PIL.Image.Resampling.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(20))
        # Imagem principal centralizada
        fg_w = W - 40
        fg_h = int(fg_w * (img.height / img.width))
        fg = img.resize((fg_w, fg_h), PIL.Image.Resampling.LANCZOS)
        
        final_slide = bg.copy()
        final_slide.paste(fg, (20, (H - fg_h) // 2))
        
        clips.append(ImageClip(np.array(final_slide)).set_duration(duration_per_img))
        
        del img, bg, fg, final_slide
        gc.collect()

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    logger("--- [EDITOR] Gerando Legendas Dinâmicas ---")
    with open(json_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    leg_clips = []
    for item in data:
        txt = item["text"].upper()
        if len(txt) < 2: continue
        
        # Criando uma tarja semi-transparente para a legenda
        canvas = PIL.Image.new("RGBA", (W, 120), (0,0,0,0))
        draw = PIL.ImageDraw.Draw(canvas)
        try:
            fonte = PIL.ImageFont.truetype(font_p, 45) # Fonte grande e negrita
        except:
            fonte = PIL.ImageFont.load_default()

        # Desenha a palavra com contorno para máxima visibilidade
        pos = (W//2, 60)
        draw.text(pos, txt, font=fonte, fill="yellow", stroke_width=3, stroke_fill="black", anchor="mm")
        
        l_clip = ImageClip(np.array(canvas)).set_start(item["start"]).set_end(item["end"]).set_position(("center", H-180))
        leg_clips.append(l_clip)

    if leg_clips:
        video = CompositeVideoClip([video] + leg_clips)

    logger("--- [EDITOR] Renderizando Reels Final ---")
    video.write_videofile("reels_final.mp4", fps=15, codec="libx264", preset="ultrafast", threads=1, logger=None)
    
    video.close()
    audio.close()
    gc.collect()
    return "reels_final.mp4"

