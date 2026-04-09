# modules/conteudo/locucao.py
import asyncio
import edge_tts
import os

async def sintetizar(texto, arquivo):
    # Francisca tem uma entonação mais amigável. 
    # Diminuir o 'rate' deixa a fala mais pausada e menos robótica.
    comunicador = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural", rate="-10%", pitch="+0Hz")
    await comunicador.save(arquivo)

def gerar_audio_narracao(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    arquivo_mp3 = os.path.join(pasta_destino, "narracao.mp3")
    
    preco = str(produto['preco']).replace(".", ",")
    # Roteiro com pontuação para pausas naturais (vírgulas e reticências)
    roteiro = (
        f"Gente... Olha só que achado incrível. "
        f"Esse {produto['titulo'][:40]}... "
        f"Tá saindo por apenas {preco} reais. "
        "Aproveita que o estoque acaba rápido. O link com desconto tá aqui na descrição!"
    )
    
    print("Gerando narração humanizada...")
    asyncio.run(sintetizar(roteiro, arquivo_mp3))
    return arquivo_mp3

