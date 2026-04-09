# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image
import PIL.ImageFilter
import numpy as np

# Configuração necessária para o TextClip (Legenda) funcionar no Render (Linux)
os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"

# Patch definitivo de compatibilidade para o erro do MoviePy com versões novas do Pillow
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, TextClip

def baixar_midia(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    caminhos = []
    # Baixamos até 4 imagens para otimizar o tempo de renderização
    for i, url in enumerate(produto['midia']['imagens_url'][:4]):
        try:
            r = requests.get(url, timeout=10)
            caminho = os.path.join(pasta_destino, f"img_{i}.jpg")
            with open(caminho, 'wb') as f: 
                f.write(r.content)
            caminhos.append(caminho)
        except: 
            continue
    return caminhos

def criar_video_reels(caminhos_imagens, caminho_audio=None, nome_saida="reels_final.mp4", logger=print):
    W, H = 480, 854 # Resolução otimizada para o Render Free
    clips = []

    try:
        # 1. Montagem das Imagens com efeito de fundo desfocado
        for img_path in caminhos_imagens:
            img_pil = PIL.Image.open(img_path).convert("RGB")
            
            # Fundo
            bg_pil = img_pil.resize((W, H), PIL.Image.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(10))
            bg_clip = ImageClip(np.array(bg_pil)).set_duration(3.0)
            
            # Frente
            fg_clip = ImageClip(img_path).set_duration(3.0).resize(width=W-40).set_position("center")
            
            slide = CompositeVideoClip([bg_clip, fg_clip], size=(W, H))
            clips.append(slide)

        video = concatenate_videoclips(clips, method="compose")

        # 2. Adicionando a "Tarja Viral" (Legenda de Título estilo TikTok)
        try:
            texto_viral = TextClip(
                "🚨 OLHA ESSE ACHADINHO!", 
                fontsize=35, 
                color='black', 
                bg_color='yellow', 
                font='Arial-Bold'
            )
            # Posiciona no topo do vídeo
            texto_viral = texto_viral.set_position(('center', 80)).set_duration(video.duration)
            video = CompositeVideoClip([video, texto_viral])
        except Exception as e:
            logger(f"--- [AVISO] O ImageMagick falhou ao criar o texto, seguindo sem a tarja: {e} ---")

        # 3. Adicionando o Áudio da Locução (Sem mixagem complexa)
        if caminho_audio and os.path.exists(caminho_audio):
            voz = AudioFileClip(caminho_audio)
            video = video.set_audio(voz)
            # Ajusta a duração do vídeo para bater exatamente com a fala da IA
            if video.duration > voz.duration:
                video = video.set_duration(voz.duration) 

        logger("--- [EDITOR] Iniciando gravação do arquivo (Pode levar 1-2 minutos)... ---")
        
        # 4. Gravação otimizada
        video.write_videofile(
            nome_saida, 
            fps=20, 
            codec="libx264", 
            audio_codec="aac", 
            preset="ultrafast",
            threads=1,
            logger=None # Desliga a barra de progresso no terminal para não poluir nosso dashboard
        )
        
        video.close()
        return nome_saida
        
    except Exception as e:
        logger(f"--- [EDITOR] ERRO CRÍTICO NA EDIÇÃO: {e} ---")
        return None

