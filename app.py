# app.py
from modules.mineracao.ml_api import buscar_produtos_tendencia
from modules.afiliacao.gerador_links import gerar_link_ml
from modules.conteudo.editor_video import baixar_midia, criar_video_reels
from modules.conteudo.locucao import gerar_copy, gerar_audio_narracao

def iniciar():
    print("=== MÁQUINA DE AFILIADOS INICIADA ===\n")
    nicho_teste = "smartwatch" 
    
    produtos_minerados = buscar_produtos_tendencia(nicho_teste)
    
    print("\n=== RESULTADO DO PROCESSAMENTO ===")
    
    for p in produtos_minerados:
        link_comissao = gerar_link_ml(p['url_original'])
        
        # Gera a Legenda (Copy)
        copy_postagem = gerar_copy(p, link_comissao)
        
        # Baixar Mídias e Gerar a Voz
        imagens_baixadas = baixar_midia(p)
        audio_gerado = gerar_audio_narracao(p)
        
        # Renderizar o Vídeo com as Imagens e o Áudio
        if imagens_baixadas:
            video_gerado = criar_video_reels(imagens_baixadas, caminho_audio=audio_gerado)
            
        print("\n" + "="*20 + " LEGENDA PRONTA " + "="*20)
        print(copy_postagem)
        print("="*56 + "\n")

if __name__ == "__main__":
    iniciar()

