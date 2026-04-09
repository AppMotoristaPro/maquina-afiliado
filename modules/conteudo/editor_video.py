# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

def baixar_midia(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    caminhos_imagens = []
    
    print(f"\nIniciando download das imagens de: {produto['titulo']}")
    
    for i, url_img in enumerate(produto['midia']['imagens_url']):
        try:
            response = requests.get(url_img, stream=True)
            response.raise_for_status()
            caminho_arquivo = os.path.join(pasta_destino, f"img_{i}.jpg")
            
            with open(caminho_arquivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            caminhos_imagens.append(caminho_arquivo)
            print(f" -> Imagem {i+1} baixada: {caminho_arquivo}")
        except requests.exceptions.RequestException as e:
            print(f" -> Erro ao baixar imagem {i+1}: {e}")
            
    return caminhos_imagens

def criar_video_reels(caminhos_imagens, caminho_audio=None, nome_arquivo_saida="reels_final.mp4"):
    print("\nIniciando a renderização do vídeo (isso pode levar alguns minutos)...")
    clips = []
    
    try:
        for img_path in caminhos_imagens:
            clip = ImageClip(img_path).set_duration(2.5)
            clip = clip.resize(height=1280)
            if clip.w > 720:
                clip = clip.resize(width=720)
            clip = clip.on_color(size=(720, 1280), color=(0, 0, 0), pos='center')
            clips.append(clip)
            
        video_final = concatenate_videoclips(clips, method="compose")
        
        # --- ADICIONANDO O ÁUDIO AO VÍDEO ---
        audio_clip = None
        if caminho_audio and os.path.exists(caminho_audio):
            audio_clip = AudioFileClip(caminho_audio)
            video_final = video_final.set_audio(audio_clip)
        
        video_final.write_videofile(
            nome_arquivo_saida, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac", # Codec de áudio obrigatório para rodar em celulares
            threads=1,   
            preset="ultrafast" 
        )
        
        # Liberando a memória
        for c in clips:
            c.close()
        if audio_clip:
            audio_clip.close()
        video_final.close()
        
        print(f"\n[SUCESSO] Vídeo com locução gerado e salvo como: {nome_arquivo_saida}")
        return nome_arquivo_saida
        
    except Exception as e:
        print(f"\n[ERRO] Falha ao gerar vídeo: {e}")
        return None

