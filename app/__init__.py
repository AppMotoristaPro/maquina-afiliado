from flask import Flask
from config import Config
from app.extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)

    with app.app_context():
        from app.models.produto import Produto
        from app.models.video import Video
        db.create_all()

    from app.rotas.dashboard_bp import dashboard_bp
    from app.rotas.api_bp import api_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
