from flask import Blueprint, request, jsonify
from app.services.mineracao_service import garimpar_produtos
from app.services.locucao_service import executar_locucao
from app.services.video_service import renderizar_video
import threading, os

api_bp = Blueprint('api', __name__)
log_list = []

@api_bp.route('/garimpar')
def api_garimpar():
    nicho = request.args.get('nicho', 'ofertas')
    return jsonify(garimpar_produtos(nicho))

@api_bp.route('/produzir', methods=['POST'])
def api_produzir():
    data = request.json
    def worker():
        global log_list
        log_list = ["Iniciando Máquina de Comissão..."]
        audio, leg = executar_locucao(data['titulo'], data['preco'])
        renderizar_video(data['imagens'], audio, leg, lambda m: log_list.append(m))
        log_list.append("VÍDEO PRONTO")
    threading.Thread(target=worker).start()
    return jsonify({"status": "iniciado"})

@api_bp.route('/logs')
def api_logs(): return jsonify({"logs": "\n".join(log_list)})
