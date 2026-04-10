import asyncio
import edge_tts
import json
import os

async def gerar_voz_e_legenda(texto, path_audio, path_json):
    # Usando a voz Francisca para um tom mais natural e menos robótico
    communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural", rate="+10%")
    subs = []
    with open(path_audio, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio": f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10000000.0
                subs.append({"text": chunk["text"], "start": start, "end": start + (chunk["duration"]/10000000.0)})
    with open(path_json, "w", encoding="utf-8") as f: json.dump(subs, f)

def executar_locucao(produto_titulo, preco):
    os.makedirs("downloads", exist_ok=True)
    
    # Criando uma "Copy" orgânica baseada no título
    # Removemos termos muito técnicos do título para a fala
    titulo_limpo = produto_titulo.split(',')[0].split('-')[0].split('(')[0].strip()
    
    roteiro = (
        f"Gente, para tudo e olha esse achadinho! É o {titulo_limpo}. "
        f"A qualidade disso aqui é de outro nível e o melhor é que o preço tá incrível, "
        f"apenas {preco} reais! É aquele tipo de item que facilita sua vida e dura muito. "
        f"Eu amei e tenho certeza que você também vai amar. O link oficial com desconto tá na Bio, corre lá!"
    )
    
    p_audio, p_json = "downloads/voz.mp3", "downloads/leg.json"
    asyncio.run(gerar_voz_e_legenda(roteiro, p_audio, p_json))
    return p_audio, p_json

