import asyncio
import edge_tts
import os

async def gerar_voz_e_legenda(texto, path_audio, path_vtt):
    communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural", rate="+10%")
    submaker = edge_tts.SubMaker()
    
    with open(path_audio, "wb") as f_audio:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f_audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # O Submaker gera as legendas automaticamente com a quebra de tempo oficial
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])
                
    with open(path_vtt, "w", encoding="utf-8") as f_vtt:
        f_vtt.write(submaker.generate_subs())

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
    p_vtt = "downloads/legenda.vtt" # Agora é um formato de legenda oficial
    asyncio.run(gerar_voz_e_legenda(roteiro, p_audio, p_vtt))
    
    return p_audio, p_vtt

