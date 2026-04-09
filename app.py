# app.py
from modules.mineracao.ml_api import buscar_produtos_tendencia
from modules.afiliacao.gerador_links import gerar_link_ml
from modules.conteudo.editor_video import baixar_midia, criar_video_reels
from modules.conteudo.locucao import gerar_audio_narracao

def iniciar():
    print("=== INICIANDO PROCESSAMENTO NO RENDER ===\n")
    nicho_teste = "smartwatch" 
    
    produtos = buscar_produtos_tendencia(nicho_teste)
    
    if not produtos:
        print("Nenhum produto aprovado para gerar vídeo.")
        return

    for p in produtos:
        # Gera link e mídias
        link_comissao = gerar_link_ml(p['url_original'])
        imagens = baixar_midia(p)
        audio = gerar_audio_narracao(p)
        
        # Cria o vídeo final
        if imagens:
            video_gerado = criar_video_reels(imagens, caminho_audio=audio)
            print(f"Processamento concluído para: {p['titulo']}")
            # Interrompemos aqui para o teste entregar apenas um vídeo
            break 

if __name__ == "__main__":
    iniciar()

