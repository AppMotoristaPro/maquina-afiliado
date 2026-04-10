from flask import Blueprint, render_template
from app.models.video import Video

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index(): 
    return render_template('dashboard/index.html')

@dashboard_bp.route('/video')
def video(): 
    # Para o front-end antigo funcionar, vamos mandar o último vídeo feito
    ultimo_video = Video.query.order_by(Video.criado_em.desc()).first()
    return render_template('dashboard/video.html', video=ultimo_video)

@dashboard_bp.route('/historico')
def historico():
    videos = Video.query.order_by(Video.criado_em.desc()).all()
    return render_template('dashboard/historico.html', videos=videos)

