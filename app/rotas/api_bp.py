from flask import Blueprint, request, jsonify, current_app
from app.services.mineracao_service import garimpar_produtos, garimpar_por_url
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

# Agora é POST para poder receber a lista de itens já vistos
@api_bp.route('/garimpar', methods=['POST'])
def api_garimpar():
    data = request.json or {}
    urls_vistas = data.get('urls_vistas', [])
    return jsonify(garimpar_produtos(urls_vistas))

# NOVA ROTA: Buscar produto por URL exata
@api_bp.route('/garimpar/url', methods=['POST'])
def api_garimpar_url():
    data = request.json
    url = data.get('url')
    return jsonify(garimpar_por_url(url))

@api_bp.route('/produzir', methods=['POST'])
def api_produzir():
    data = request.json
    link_afiliado = data.get('link_afiliado')
    
    set_progresso(5, "Iniciando Máquina de Comissão...")
    
    produto = Produto(titulo=data['titulo'], preco=data['preco'], url_original=data['url'], imagens_json=json.dumps(data['imagens']))
    db.session.add(produto)
    db.session.commit()

    palavras_limpas = re.sub(r'[^a-zA-Z0-9 ]', '', data['titulo']).split()
    tags_dinamicas = " ".join([f"#{p.lower()}" for p in palavras_limpas[:3] if len(p) > 2])
    bloco_hashtags = f"\n\n{tags_dinamicas} #achadinhos #mercadolivre #promocao #oferta #tendencia"

    copy_gerada = f"🚨 Achado imperdível!\n\n{data['titulo']}\n\nDeixe um 'EU QUERO' nos comentários que te envio o link no Direct!\n\n🔗 Link na Bio: {link_afiliado}{bloco_hashtags}"
    
    video = Video(produto_id=produto.id, link_afiliado=link_afiliado, copy_gerada=copy_gerada, status='processando')
    db.session.add(video)
    db.session.commit()
    
    video_id = video.id
    app_context = current_app._get_current_object()

    def worker(app, v_id, p_data):
        with app.app_context():
            try:
                set_progresso(15, "Gerando locução persuasiva...")
                audio = executar_locucao(p_data['titulo'], p_data['preco'])
                caminho_final = renderizar_video(p_data['imagens'], audio, set_progresso)
                
                v = Video.query.get(v_id)
                v.status = 'concluido'
                v.caminho_arquivo = caminho_final
                db.session.commit()
                
                set_progresso(100, "VÍDEO PRONTO")
            except Exception as e:
                set_progresso(100, f"ERRO FATAL: {e}")
                v = Video.query.get(v_id)
                v.status = 'erro'
                db.session.commit()

    threading.Thread(target=worker, args=(app_context, video_id, data)).start()
    return jsonify({"status": "iniciado"})

@api_bp.route('/progresso')
def api_progresso(): 
    try:
        with open("progress.json", "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify({"percent": 0, "msg": "Aguardando..."})

@api_bp.route('/historico/<int:video_id>', methods=['DELETE'])
def deletar_historico(video_id):
    v = Video.query.get(video_id)
    if v:
        p = v.produto
        db.session.delete(v)
        db.session.delete(p)
        db.session.commit()
        return jsonify({"status": "sucesso"})
    return jsonify({"status": "erro"}), 404

