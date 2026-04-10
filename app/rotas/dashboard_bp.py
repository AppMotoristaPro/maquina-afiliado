# app/rotas/dashboard_bp.py
from flask import Blueprint, render_template, send_file
from app.models.video import Video
import os

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index(): 
    return render_template('dashboard/index.html')

@dashboard_bp.route('/video')
def video(): 
    ultimo_video = Video.query.order_by(Video.criado_em.desc()).first()
    return render_template('dashboard/video.html', video=ultimo_video)

@dashboard_bp.route('/historico')
def historico():
    videos = Video.query.order_by(Video.criado_em.desc()).all()
    return render_template('dashboard/historico.html', videos=videos)

@dashboard_bp.route('/stream')
def stream_video():
    caminho = os.path.abspath("reels_final.mp4")
    if os.path.exists(caminho):
        return send_file(caminho, mimetype="video/mp4")
    return "Vídeo não encontrado no servidor.", 404

@dashboard_bp.route('/download')
def download_video():
    caminho = os.path.abspath("reels_final.mp4")
    if os.path.exists(caminho):
        return send_file(caminho, as_attachment=True)
    return "Vídeo não encontrado no servidor.", 404

