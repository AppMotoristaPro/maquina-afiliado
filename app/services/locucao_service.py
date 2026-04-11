import asyncio
import edge_tts
import os

async def gerar_voz(texto, path_audio):
    # Apenas gera a narração, muito mais rápido sem calcular tempos de legendas
    communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural", rate="+10%")
    await communicate.save(path_audio)

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
    
    # Roda a função assíncrona
    asyncio.run(gerar_voz(roteiro, p_audio))
    
    # Retorna apenas o caminho do áudio
    return p_audio

