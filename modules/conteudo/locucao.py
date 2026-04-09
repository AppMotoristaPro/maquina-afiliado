# modules/conteudo/locucao.py
import asyncio
import edge_tts
import os

def gerar_copy(produto, link_afiliado):
    """Gera o texto persuasivo para a legenda da postagem."""
    texto = (
        f"🚨 ACHADINHO IMPERDÍVEL! 🚨\n\n"
        f"📦 {produto['titulo']}\n"
        f"💰 Por apenas: R$ {produto['preco']:.2f}\n\n"
        f"👉 Garanta o seu com segurança no link abaixo:\n"
        f"🔗 {link_afiliado}\n\n"
        f"⏳ Promoção por tempo limitado!"
    )
    return texto

async def criar_audio_assincrono(texto_narracao, arquivo_saida):
    """Comunica com a API da Microsoft. A voz 'FranciscaNeural' possui entonação excelente."""
    comunicador = edge_tts.Communicate(texto_narracao, "pt-BR-FranciscaNeural", rate="+5%")
    await comunicador.save(arquivo_saida)

def gerar_audio_narracao(produto, pasta_destino="downloads"):
    """Cria um roteiro natural e gera o arquivo de áudio (.mp3)."""
    os.makedirs(pasta_destino, exist_ok=True)
    arquivo_mp3 = os.path.join(pasta_destino, "narracao.mp3")
    
    # Isola apenas a parte principal do título para uma leitura fluida
    titulo_curto = produto['titulo'].split(" - ")[0].split(",")[0][:40] 
    
    # Formata o preço para garantir a pronúncia correta da IA
    preco_formatado = str(produto['preco']).replace('.', ',')
    
    # Roteiro otimizado para soar como recomendação humana
    roteiro = (
        "Gente, eu não estou acreditando nesse achado. "
        f"Olha só esse {titulo_curto}. "
        f"Ele está saindo por apenas {preco_formatado} reais. "
        "A qualidade é muito boa pelo preço. "
        "Eu deixei o link promocional na descrição para quem quiser aproveitar antes que acabe."
    )
    
    print("\nGerando áudio da narração realista...")
    asyncio.run(criar_audio_assincrono(roteiro, arquivo_mp3))
    
    if os.path.exists(arquivo_mp3):
        print(f" -> Áudio gerado com sucesso: {arquivo_mp3}")
        return arquivo_mp3
    return None

