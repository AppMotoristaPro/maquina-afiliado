import asyncio
import edge_tts
import os
import random

async def gerar_voz(texto, path_audio):
    # Voz masculina Antonio para um tom mais orgânico
    communicate = edge_tts.Communicate(texto, "pt-BR-AntonioNeural", rate="+10%")
    await communicate.save(path_audio)

def executar_locucao(produto_titulo, preco):
    os.makedirs("downloads", exist_ok=True)
    titulo_limpo = produto_titulo.split(',')[0].split('-')[0].strip()
    
    roteiros = [
        f"Gente, olha esse achadinho! É o {titulo_limpo}. Qualidade de outro nível e o preço tá incrível, apenas {preco} reais! O link com desconto tá na Bio, na descrição do vídeo, ou comenta EU QUERO que eu te mando no privado!",
        f"Sabe aquele produto que você não sabia que precisava? Olha esse {titulo_limpo}! Por só {preco} reais, não deixa passar. O link tá na minha Bio, na descrição, ou comenta EU QUERO que te envio no direct!",
        f"Alerta de oferta! Esse {titulo_limpo} tá apenas {preco} reais! Estoque vai voar. Clica no link da Bio, olha na descrição, ou escreve EU QUERO nos comentários pra eu te mandar o link.",
        f"Custo-benefício surreal nesse {titulo_limpo}, custando só {preco} reais. Melhor preço que já vi! Vai na minha Bio, olha na descrição, ou comenta EU QUERO que o link vai pro seu direct!",
        f"Passando pra mostrar essa perfeição: {titulo_limpo}. Por {preco} reais é um presente! Link direto na Bio, na descrição, ou comenta EU QUERO que te passo agora!"
    ]
    
    asyncio.run(gerar_voz(random.choice(roteiros), "downloads/voz.mp3"))
    return "downloads/voz.mp3"

