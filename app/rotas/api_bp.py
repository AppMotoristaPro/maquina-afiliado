from flask import Blueprint, request, jsonify, current_app
from app.services.mineracao_service import garimpar_produtos
from app.services.locucao_service import executar_locucao
from app.services.video_service import renderizar_video
from app.models.produto import Produto
from app.models.video import Video
from app.extensions import db
import threading, json, os

api_bp = Blueprint('api', __name__)

def set_progresso(percent, msg):
    with open("progress.json", "w", encoding="utf-8") as f:
        json.dump({"percent": percent, "msg": msg}, f)

@api_bp.route('/garimpar')
def api_garimpar():
    return jsonify(garimpar_produtos())

@api_bp.route('/produzir', methods=['POST'])
def api_produzir():
    data = request.json
    link_afiliado = data.get('link_afiliado')
    
    set_progresso(5, "Iniciando Máquina de Comissão...")
    
    produto = Produto(
        titulo=data['titulo'], preco=data['preco'], url_original=data['url'], imagens_json=json.dumps(data['imagens'])
    )
    db.session.add(produto)
    db.session.commit()

    copy_gerada = f"🚨 Achado imperdível!\n\n{data['titulo']}\n\nDeixe um 'EU QUERO' nos comentários que te envio o link no Direct!\n\n🔗 Link: {link_afiliado}"
    video = Video(produto_id=produto.id, link_afiliado=link_afiliado, copy_gerada=copy_gerada, status='processando')
    db.session.add(video)
    db.session.commit()
    
    video_id = video.id
    app_context = current_app._get_current_object()

    def worker(app, v_id, p_data):
        with app.app_context():
            try:
                set_progresso(15, "Gerando locução persuasiva...")
                audio, vtt_legenda = executar_locucao(p_data['titulo'], p_data['preco'])
                
                caminho_final = renderizar_video(p_data['imagens'], audio, vtt_legenda, set_progresso)
                
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

