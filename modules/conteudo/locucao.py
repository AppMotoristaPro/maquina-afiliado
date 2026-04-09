# modules/conteudo/locucao.py
import asyncio
import edge_tts
import os

async def sintetizar_voz(texto, arquivo):
    # 'Thalita' costuma soar mais natural para 'achadinhos' que o Antonio
    # Reduzimos levemente a velocidade (rate) para evitar tom de robô apressado
    communicate = edge_tts.Communicate(texto, "pt-BR-ThalitaNeural", rate="-5%", pitch="+0Hz")
    await communicate.save(arquivo)

def gerar_audio_narracao(produto, pasta_destino="downloads"):
    os.makedirs(pasta_destino, exist_ok=True)
    arquivo_mp3 = os.path.join(pasta_destino, "narracao.mp3")
    
    nome_limpo = produto['titulo'].split(" - ")[0][:40]
    preco = str(produto['preco']).replace(".", ",")
    
    # Roteiro com pontuação proposital para pausas naturais
    roteiro = (
        f"Gente... olha só esse achado que eu acabei de encontrar! "
        f"É o {nome_limpo}. "
        f"Ele tá com um preço incrível... apenas {preco} reais. "
        "A qualidade é surpreendente e entrega super rápido. "
        "O link com desconto tá aqui na descrição, aproveita logo antes que o estoque acabe!"
    )
    
    print("Sintetizando locução humanizada...")
    asyncio.run(sintetizar_voz(roteiro, arquivo_mp3))
    return arquivo_mp3

def gerar_copy(produto, link):
    return f"🔥 {produto['titulo']}\n\n💰 R$ {produto['preco']}\n🔗 {link}"

