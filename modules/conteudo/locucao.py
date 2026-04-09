# modules/conteudo/locucao.py
import asyncio
import edge_tts
import os
import json

async def sintetizar_com_legenda(texto, arquivo_audio, arquivo_legenda):
    comunicador = edge_tts.Communicate(texto, "pt-BR-ThalitaNeural", rate="+5%")
    legendas = []
    
    with open(arquivo_audio, "wb") as f_audio:
        async for chunk in comunicador.stream():
            if chunk["type"] == "audio":
                f_audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # Converte o tempo do formato da Microsoft (100-nanosegundos) para segundos reais
                start = chunk["offset"] / 10000000.0
                dur = chunk["duration"] / 10000000.0
                legendas.append({
                    "start": start,
                    "end": start + dur,
                    "text": chunk["text"]
                })
                
    # Salva os tempos exatos para o editor de vídeo ler depois
    with open(arquivo_legenda, "w", encoding="utf-8") as f_legenda:
        json.dump(legendas, f_legenda)

def gerar_audio_narracao(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    arquivo_mp3 = os.path.join(pasta_destino, "narracao.mp3")
    arquivo_json = os.path.join(pasta_destino, "legendas.json")
    
    preco = str(produto['preco']).replace(".", ",")
    
    # Roteiro curto e viral
    roteiro = (
        f"Gente, olha esse achadinho! É o {produto['titulo'][:40]}. "
        f"A qualidade é sensacional e por apenas {preco} reais tá valendo muito a pena. "
        "O link com desconto tá na descrição, corre lá!"
    )
    
    print("--- [VOZ] Narrando e extraindo tempos das palavras... ---")
    asyncio.run(sintetizar_com_legenda(roteiro, arquivo_mp3, arquivo_json))
    
    # Agora retornamos os DOIS arquivos
    return arquivo_mp3, arquivo_json

