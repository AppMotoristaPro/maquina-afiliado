import asyncio
import edge_tts
import os
import random

async def gerar_voz(texto, path_audio):
    communicate = edge_tts.Communicate(texto, "pt-BR-AntonioNeural", rate="+10%")
    await communicate.save(path_audio)

def executar_locucao(produto_titulo, preco):
    os.makedirs("downloads", exist_ok=True)
    titulo_limpo = produto_titulo.split(',')[0].split('-')[0].split('(')[0].strip()
    
    # Roteiros atualizados com CTA Triplo (Bio, Descrição e Comentário)
    roteiros = [
        f"Pessoal, para tudo e olha esse achadinho! É o {titulo_limpo}. A qualidade disso aqui é de outro nível e o melhor é que o preço tá incrível, apenas {preco} reais! É aquele tipo de item que facilita sua vida e dura muito. O link com desconto tá na Bio, na descrição do vídeo, ou comenta EU QUERO que eu te mando no privado!",
        
        f"Sabe aquele produto que você não sabia que precisava até ver? Pois é, olha esse {titulo_limpo}! Tá todo mundo comprando e eu entendi o porquê. Além de ser super útil no dia a dia, tá saindo por só {preco} reais. Sério, não deixa passar. O link tá na minha Bio, na descrição, ou comenta EU QUERO que te envio no direct!",
        
        f"Alerta de oferta imperdível! Acabei de achar esse {titulo_limpo} e fiquei em choque com o preço. Apenas {preco} reais! Se você tava procurando um desses, a hora é agora porque o estoque vai voar. Clica no link da Bio, acessa pela descrição do vídeo, ou escreve EU QUERO nos comentários pra eu te mandar no privado.",
        
        f"Eu não guardo segredo de promoção boa! Olha que sensacional esse {titulo_limpo}. O custo-benefício tá surreal, custando só {preco} reais. É o melhor preço que eu já vi pra esse nível de qualidade. Vai lá na minha Bio, olha na descrição, ou comenta EU QUERO que o link vai direto pro seu direct!",
        
        f"Passando rapidinho pra mostrar essa perfeição: {titulo_limpo}. Galera, por {preco} reais, isso aqui é praticamente um presente! Compra, testa e depois me conta aqui se não foi a melhor escolha do seu mês. Link direto na Bio, na descrição, ou comenta EU QUERO que te passo no privado!"
    ]
    
    roteiro_escolhido = random.choice(roteiros)
    p_audio = "downloads/voz.mp3"
    
    asyncio.run(gerar_voz(roteiro_escolhido, p_audio))
    return p_audio

