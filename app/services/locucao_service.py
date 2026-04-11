import asyncio
import edge_tts
import os
import random

async def gerar_voz(texto, path_audio):
    # Apenas gera a narração, muito mais rápido sem calcular tempos de legendas
    communicate = edge_tts.Communicate(texto, "pt-BR-FranciscaNeural", rate="+10%")
    await communicate.save(path_audio)

def executar_locucao(produto_titulo, preco):
    os.makedirs("downloads", exist_ok=True)
    titulo_limpo = produto_titulo.split(',')[0].split('-')[0].split('(')[0].strip()
    
    # Lista de roteiros orgânicos com diferentes gatilhos mentais
    roteiros = [
        # 1. Gatilho de Descoberta (O Original)
        f"Gente, para tudo e olha esse achadinho! É o {titulo_limpo}. A qualidade disso aqui é de outro nível e o melhor é que o preço tá incrível, apenas {preco} reais! É aquele tipo de item que facilita sua vida e dura muito. Eu amei e tenho certeza que você também vai amar. O link oficial com desconto tá na Bio, corre lá!",
        
        # 2. Gatilho de Curiosidade e Utilidade
        f"Sabe aquele produto que você não sabia que precisava até ver? Pois é, olha esse {titulo_limpo}! Tá todo mundo comprando e eu entendi o porquê. Além de ser super útil no dia a dia, tá saindo por só {preco} reais. Sério, não deixa passar. O link tá na minha Bio!",
        
        # 3. Gatilho de Urgência e Escassez
        f"Alerta de oferta imperdível! Acabei de achar esse {titulo_limpo} e fiquei chocada com o preço. Apenas {preco} reais! Se você tava procurando um desses, a hora é agora porque o estoque vai voar. Clica no link da Bio e garante o seu antes que acabe.",
        
        # 4. Gatilho de Custo-Benefício e Compartilhamento
        f"Eu não guardo segredo de promoção boa! Olha que sensacional esse {titulo_limpo}. O custo-benefício tá surreal, custando só {preco} reais. É o melhor preço que eu já vi pra esse nível de qualidade. Vai lá na minha Bio que o link já tá te esperando!",
        
        # 5. Gatilho de Autoridade/Recomendação
        f"Passando rapidinho pra mostrar essa perfeição: {titulo_limpo}. Gente, por {preco} reais, isso aqui é praticamente um presente! Compra, testa e depois me conta aqui se não foi a melhor escolha do seu mês. Link direto na Bio, aproveita demais!"
    ]
    
    # O Python escolhe um roteiro aleatório a cada novo vídeo
    roteiro_escolhido = random.choice(roteiros)
    
    p_audio = "downloads/voz.mp3"
    
    # Roda a função assíncrona
    asyncio.run(gerar_voz(roteiro_escolhido, p_audio))
    
    return p_audio

