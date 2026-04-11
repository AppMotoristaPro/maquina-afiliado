from flask import Blueprint, request, jsonify, current_app
from app.services.mineracao_service import garimpar_produtos, garimpar_por_url
from app.services.shopee_service import garimpar_shopee
from app.services.locucao_service import executar_locucao
from app.services.video_service import renderizar_video
from app.models.produto import Produto
from app.models.video import Video
from app.extensions import db
import threading, json, os, re

api_bp = Blueprint('api', __name__)

def set_progresso(percent, msg):
    with open("progress.json", "w", encoding="utf-8") as f:
        json.dump({"percent": percent, "msg": msg}, f)

@api_bp.route('/garimpar', methods=['POST'])
def api_garimpar():
    data = request.json or {}
    urls_vistas = data.get('urls_vistas', [])
    marketplace = data.get('marketplace', 'ml')
    
    if marketplace == 'shopee':
        return jsonify(garimpar_shopee(urls_vistas))
    return jsonify(garimpar_produtos(urls_vistas))

@api_bp.route('/garimpar/url', methods=['POST'])
def api_garimpar_url():
    data = request.json
    url = data.get('url')
    return jsonify(garimpar_por_url(url))

@api_bp.route('/produzir', methods=['POST'])
def api_produzir():
    data = request.json
    link_afiliado = data.get('link_afiliado')
    plataforma = data.get('plataforma', 'ml')
    
    set_progresso(5, "Iniciando produção...")
    
    produto = Produto(
        titulo=data['titulo'], 
        preco=data['preco'], 
        url_original=data['url'], 
        imagens_json=json.dumps(data['imagens']),
        plataforma=plataforma
    )
    db.session.add(produto)
    db.session.commit()

    # Gerador de Hashtags dinâmico
    palavras = re.sub(r'[^a-zA-Z0-9 ]', '', data['titulo']).split()
    tags = " ".join([f"#{p.lower()}" for p in palavras[:3] if len(p) > 2])
    bloco_tags = f"\n\n{tags} #achadinhos #{'shopee' if plataforma == 'shopee' else 'mercadolivre'} #promocao"

    copy = f"🚨 Achado imperdível!\n\n{data['titulo']}\n\nDeixe um 'EU QUERO' nos comentários que te envio o link no Direct!\n\n🔗 Link na Bio: {link_afiliado}{bloco_tags}"
    
    video = Video(produto_id=produto.id, link_afiliado=link_afiliado, copy_gerada=copy, status='processando')
    db.session.add(video)
    db.session.commit()
    
    app_context = current_app._get_current_object()

    def worker(app, v_id, p_data):
        with app.app_context():
            try:
                set_progresso(20, "Gerando voz do Antonio...")
                audio = executar_locucao(p_data['titulo'], p_data['preco'])
                caminho = renderizar_video(p_data['imagens'], audio, set_progresso)
                
                v = Video.query.get(v_id)
                v.status, v.caminho_arquivo = 'concluido', caminho
                db.session.commit()
                set_progresso(100, "VÍDEO PRONTO")
            except Exception as e:
                set_progresso(100, f"ERRO: {e}")
    
    threading.Thread(target=worker, args=(app_context, video.id, data)).start()
    return jsonify({"status": "iniciado"})

@api_bp.route('/progresso')
def api_progresso(): 
    try:
        with open("progress.json", "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except: return jsonify({"percent": 0, "msg": "Aguardando..."})

