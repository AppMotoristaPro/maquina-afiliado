# modules/conteudo/locucao.py
import asyncio
import edge_tts
import os

async def sintetizar(texto, arquivo):
    # ThalitaNeural é mais expressiva para vídeos de vendas
    comunicador = edge_tts.Communicate(texto, "pt-BR-ThalitaNeural", rate="+5%", pitch="+0Hz")
    await comunicador.save(arquivo)

def gerar_audio_narracao(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    arquivo_mp3 = os.path.join(pasta_destino, "narracao.mp3")
    
    # Nome curto para não ficar cansativo
    nome_produto = produto['titulo'].split(" - ")[0][:40]
    preco = str(produto['preco']).replace(".", ",")
    
    # Roteiro com entonação de "Dica de Amigo"
    roteiro = (
        f"Gente, para tudo! Olha esse achado que eu acabei de encontrar. "
        f"É esse {nome_produto}. "
        f"O preço tá simplesmente bizarro... Só {preco} reais! "
        "A qualidade é muito superior ao que eu esperava. "
        "Se você quer um desses, corre... O link com desconto tá na descrição antes que acabe o estoque!"
    )
    
    print(f"--- [VOZ] Gerando locução para: {nome_produto} ---")
    asyncio.run(sintetizar(roteiro, arquivo_mp3))
    return arquivo_mp3

