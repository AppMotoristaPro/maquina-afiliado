# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image
import PIL.ImageFilter
from PIL import ImageDraw, ImageFont
import numpy as np
import json
import urllib.request

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

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

def desenhar_palavra_legenda(texto, largura_video):
    """Cria uma imagem PNG da palavra usando Pillow (Substitui o ImageMagick do Render)"""
    altura_box = 120
    img = PIL.Image.new('RGBA', (largura_video, altura_box), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_path = "Roboto-Black.ttf"
    if not os.path.exists(font_path):
        try:
            # Baixa a fonte Roboto Black direto do repositório do Google
            urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Black.ttf", font_path)
        except: pass

    try:
        fonte = ImageFont.truetype(font_path, 60) # Tamanho da legenda
    except:
        fonte = ImageFont.load_default()
        
    try:
        bbox = draw.textbbox((0,0), texto, font=fonte)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except:
        tw, th = 200, 50
        
    x = (largura_video - tw) / 2
    y = (altura_box - th) / 2
    
    # Desenha Borda Preta
    contorno = 3
    for dx in range(-contorno, contorno+1):
        for dy in range(-contorno, contorno+1):
            draw.text((x+dx, y+dy), texto, font=fonte, fill="black")
            
    # Preenchimento Amarelo Viral
    draw.text((x, y), texto, font=fonte, fill="#FFEA00")
    
    return np.array(img)

def criar_video_reels(caminhos_imagens, caminho_audio=None, caminho_legenda=None, nome_saida="reels_final.mp4", logger=print):
    W, H = 480, 854 
    clips = []

    try:
        # 1. Monta Imagens (Fundo desfocado)
        for img_path in caminhos_imagens:
            img_pil = PIL.Image.open(img_path).convert("RGB")
            bg_pil = img_pil.resize((W, H), PIL.Image.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(10))
            bg_clip = ImageClip(np.array(bg_pil)).set_duration(3.0)
            fg_clip = ImageClip(img_path).set_duration(3.0).resize(width=W-40).set_position("center")
            clips.append(CompositeVideoClip([bg_clip, fg_clip], size=(W, H)))

        video = concatenate_videoclips(clips, method="compose")

        # 2. Áudio
        if caminho_audio and os.path.exists(caminho_audio):
            voz = AudioFileClip(caminho_audio)
            video = video.set_audio(voz).set_duration(voz.duration)

        # 3. Legendas Nativas (Driblando o Render)
        try:
            if caminho_legenda and os.path.exists(caminho_legenda):
                legenda_clips = []
                with open(caminho_legenda, "r", encoding="utf-8") as f:
                    legendas = json.load(f)
                    
                for leg in legendas:
                    texto = leg["text"].strip().upper()
                    # Ignora caracteres minúsculos isolados
                    if len(texto) < 2 and texto not in ["E", "A", "O", "É", "Ó"]: continue
                    
                    # Usa nosso criador de imagem nativo
                    img_array = desenhar_palavra_legenda(texto, W)
                    
                    # Transforma a imagem em um Clip de vídeo que aparece e some no tempo exato
                    txt_clip = ImageClip(img_array).set_start(leg["start"]).set_end(leg["end"])
                    txt_clip = txt_clip.set_position(('center', int(H * 0.70))) # 70% da altura da tela (parte de baixo)
                    
                    legenda_clips.append(txt_clip)

                if legenda_clips:
                    video = CompositeVideoClip([video] + legenda_clips)
        except Exception as e:
            logger(f"--- [AVISO] O processo da legenda falhou: {e} ---")

        logger("--- [EDITOR] Iniciando gravação otimizada do arquivo... ---")
        video.write_videofile(
            nome_saida, fps=20, codec="libx264", audio_codec="aac", preset="ultrafast", threads=1, logger=None
        )
        video.close()
        return nome_saida
    except Exception as e:
        logger(f"--- [EDITOR] ERRO CRÍTICO NA EDIÇÃO: {e} ---")
        return None

