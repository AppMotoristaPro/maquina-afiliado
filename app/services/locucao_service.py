import asyncio
import edge_tts
import os

def formata_tempo_vtt(segundos):
    # Converte segundos float (ex: 1.25) para o formato VTT (HH:MM:SS.mmm)
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    segs = int(segundos % 60)
    mili = int((segundos - int(segundos)) * 1000)
    return f"{horas:02d}:{minutos:02d}:{segs:02d}.{mili:03d}"

async def gerar_voz_e_legenda(texto, path_audio, path_vtt):
    communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural", rate="+10%")
    
    # Prepara o arquivo VTT manualmente
    with open(path_vtt, "w", encoding="utf-8") as f_vtt:
        f_vtt.write("WEBVTT\n\n")
        
        with open(path_audio, "wb") as f_audio:
            contador = 1
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f_audio.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # Pega o tempo em segundos
                    inicio = chunk["offset"] / 10000000.0
                    duracao = chunk["duration"] / 10000000.0
                    fim = inicio + duracao
                    palavra = chunk["text"]
                    
                    # Escreve o bloco VTT
                    f_vtt.write(f"{contador}\n")
                    f_vtt.write(f"{formata_tempo_vtt(inicio)} --> {formata_tempo_vtt(fim)}\n")
                    f_vtt.write(f"{palavra}\n\n")
                    contador += 1

def executar_locucao(produto_titulo, preco):
    os.makedirs("downloads", exist_ok=True)
    titulo_limpo = produto_titulo.split(',')[0].split('-')[0].split('(')[0].strip()
    
    roteiro = (
        f"Gente, para tudo e olha esse achadinho! É o {titulo_limpo}. "
        f"A qualidade disso aqui é de outro nível e o melhor é que o preço tá incrível, "
        f"apenas {preco} reais! É aquele tipo de item que facilita sua vida e dura muito. "
        f"Eu amei e tenho certeza que você também vai amar. O link oficial com desconto tá na Bio, corre lá!"
    )
    
    p_audio = "downloads/voz.mp3"
    p_vtt = "downloads/legenda.vtt" 
    
    asyncio.run(gerar_voz_e_legenda(roteiro, p_audio, p_vtt))
    
    return p_audio, p_vtt

