# modules/conteudo/editor_video.py
import os
import requests
import PIL.Image
import PIL.ImageFilter

if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, ColorClip, CompositeVideoClip

def baixar_midia(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    caminhos_imagens = []
    
    # Filtramos apenas as URLs que são de fato do Mercado Livre (evita picsum de testes antigos)
    urls_reais = [url for url in produto['midia']['imagens_url'] if "mlstatic.com" in url]
    
    print(f"\nBaixando {len(urls_reais)} imagens reais do produto...")
    
    for i, url_img in enumerate(urls_reais[:6]): # Limitamos a 6 imagens para o vídeo não ficar longo
        try:
            response = requests.get(url_img, stream=True, timeout=10)
            response.raise_for_status()
            caminho_arquivo = os.path.join(pasta_destino, f"img_{i}.jpg")
            
            with open(caminho_arquivo, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            caminhos_imagens.append(caminho_arquivo)
        except Exception as e:
            print(f" -> Erro no download da imagem {i}: {e}")
            
    return caminhos_imagens

def criar_video_reels(caminhos_imagens, caminho_audio=None, nome_arquivo_saida="reels_final.mp4"):
    print("\nRenderizando vídeo com efeito de fundo dinâmico (Cinematic)...")
    clips = []
    largura, altura = 720, 1280

    try:
        for img_path in caminhos_imagens:
            # 1. Camada de Fundo (Borrada)
            img_original = PIL.Image.open(img_path).convert("RGB")
            # Redimensiona para preencher a tela (Crop/Fill) e aplica desfoque
            bg_img = img_original.resize((largura, altura), PIL.Image.LANCZOS)
            bg_img = bg_img.filter(PIL.ImageFilter.GaussianBlur(radius=20))
            bg_path = img_path.replace(".jpg", "_bg.jpg")
            bg_img.save(bg_path)
            
            bg_clip = ImageClip(bg_path).set_duration(2.5)
            
            # 2. Camada Frontal (Nítida)
            fg_clip = ImageClip(img_path).set_duration(2.5)
            fg_clip = fg_clip.resize(width=largura - 40) # Margem lateral de 20px
            fg_clip = fg_clip.set_position("center")
            
            # Sobreposição
            slide = CompositeVideoClip([bg_clip, fg_clip], size=(largura, altura))
            clips.append(slide)
            
        video_final = concatenate_videoclips(clips, method="compose")
        
        if caminho_audio and os.path.exists(caminho_audio):
            audio_clip = AudioFileClip(caminho_audio)
            # Ajusta a duração do vídeo para bater com o áudio se necessário
            video_final = video_final.set_audio(audio_clip)
            if video_final.duration > audio_clip.duration:
                video_final = video_final.set_duration(audio_clip.duration)
        
        video_final.write_videofile(
            nome_arquivo_saida, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            threads=2,
            preset="ultrafast"
        )
        
        # Limpeza
        video_final.close()
        return nome_arquivo_saida
    except Exception as e:
        print(f"Erro na renderização: {e}")
        return None

