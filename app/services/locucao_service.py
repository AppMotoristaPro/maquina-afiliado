import asyncio
import edge_tts
import json
import os

async def gerar_voz_e_legenda(texto, path_audio, path_json):
    communicate = edge_tts.Communicate(texto, "pt-BR-ThalitaNeural", rate="+5%")
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
    txt = f"Olha esse achadinho! {produto_titulo[:50]}. Por apenas {preco} reais. Link na Bio!"
    p_audio, p_json = "downloads/voz.mp3", "downloads/leg.json"
    asyncio.run(gerar_voz_e_legenda(txt, p_audio, p_json))
    return p_audio, p_json
