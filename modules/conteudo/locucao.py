# modules/conteudo/locucao.py
import asyncio, edge_tts, os

async def sintetizar(texto, arquivo):
    # Francisca é excelente para narração de ofertas
    comunicador = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural", rate="-5%")
    await comunicador.save(arquivo)

def gerar_audio_narracao(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    arquivo_mp3 = os.path.join(pasta_destino, "narracao.mp3")
    
    preco = str(produto['preco']).replace(".", ",")
    # Pontuação estratégica para pausas naturais
    roteiro = (
        f"Gente... olha que achado sensacional. "
        f"Esse {produto['titulo'][:40]}... "
        f"está saindo por apenas {preco} reais! "
        "A qualidade é nota dez e o preço tá imbatível. "
        "O link com desconto está na descrição... corre antes que acabe o estoque!"
    )
    
    print(f"--- [VOZ] Narrando: {produto['titulo'][:20]} ---")
    asyncio.run(sintetizar(roteiro, arquivo_mp3))
    return arquivo_mp3

