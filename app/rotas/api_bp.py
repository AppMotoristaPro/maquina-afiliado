from flask import Blueprint, request, jsonify, current_app
from app.services.mineracao_service import garimpar_produtos
from app.services.locucao_service import executar_locucao
from app.services.video_service import renderizar_video
from app.models.produto import Produto
from app.models.video import Video
from app.extensions import db
import threading, json

api_bp = Blueprint('api', __name__)
log_list = []

@api_bp.route('/garimpar')
def api_garimpar():
    # Não precisa mais receber nicho, ele varre as categorias fixas
    return jsonify(garimpar_produtos())

@api_bp.route('/produzir', methods=['POST'])
def api_produzir():
    data = request.json
    link_afiliado = data.get('link_afiliado')
    
    # 1. Salva Produto no Banco
    produto = Produto(
        titulo=data['titulo'],
        preco=data['preco'],
        url_original=data['url'],
        imagens_json=json.dumps(data['imagens'])
    )
    db.session.add(produto)
    db.session.commit()

    # 2. Gera a Copy e Salva Video no Banco
    copy_gerada = f"🚨 Achado imperdível!\n\n{data['titulo']}\n\nDeixe um 'EU QUERO' nos comentários que te envio o link no Direct!\n\n🔗 Link: {link_afiliado}"
    video = Video(produto_id=produto.id, link_afiliado=link_afiliado, copy_gerada=copy_gerada, status='processando')
    db.session.add(video)
    db.session.commit()
    
    video_id = video.id
    app_context = current_app._get_current_object() # Pegando o contexto para a Thread

    def worker(app, v_id, p_data):
        with app.app_context():
            global log_list
            log_list = ["Iniciando Máquina de Comissão..."]
            
            try:
                audio, leg = executar_locucao(p_data['titulo'], p_data['preco'])
                caminho_final = renderizar_video(p_data['imagens'], audio, leg, lambda m: log_list.append(m))
                
                # Atualiza Video como Concluído
                v = Video.query.get(v_id)
                v.status = 'concluido'
                v.caminho_arquivo = caminho_final
                db.session.commit()
                
                log_list.append("VÍDEO PRONTO")
            except Exception as e:
                log_list.append(f"ERRO FATAL: {e}")
                v = Video.query.get(v_id)
                v.status = 'erro'
                db.session.commit()

    threading.Thread(target=worker, args=(app_context, video_id, data)).start()
    return jsonify({"status": "iniciado"})

@api_bp.route('/logs')
def api_logs(): 
    return jsonify({"logs": "\n".join(log_list)})

@api_bp.route('/historico/<int:video_id>', methods=['DELETE'])
def deletar_historico(video_id):
    v = Video.query.get(video_id)
    if v:
        # Apaga o vídeo, e também apaga o produto atrelado para poder voltar à mineração
        p = v.produto
        db.session.delete(v)
        db.session.delete(p)
        db.session.commit()
        return jsonify({"status": "sucesso"})
    return jsonify({"status": "erro"}), 404

