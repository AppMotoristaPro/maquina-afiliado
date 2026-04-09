# modules/mineracao/validador.py
from config import PRECO_MIN, PRECO_MAX, NOTA_MINIMA, QTD_MINIMA_IMAGENS

def produto_e_valido(preco, nota, possui_video, qtd_imagens):
    """
    Avalia se o produto cumpre os requisitos para virar um vídeo de afiliado.
    """
    # 1. Verifica a faixa de preço
    if not (PRECO_MIN <= preco <= PRECO_MAX):
        return False, "Preço fora da zona de conversão."
        
    # 2. Verifica a prova social (Nota)
    if nota < NOTA_MINIMA:
        return False, "Nota de avaliação muito baixa."
        
    # 3. Verifica se tem mídia suficiente para o Reels
    if not possui_video and qtd_imagens < QTD_MINIMA_IMAGENS:
        return False, "Mídia insuficiente (sem vídeo e com poucas fotos)."
        
    return True, "Produto aprovado!"

