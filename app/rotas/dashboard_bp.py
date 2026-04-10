from flask import Blueprint, render_template
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index(): return render_template('dashboard/index.html')

@dashboard_bp.route('/video')
def video(): return render_template('dashboard/video.html')
