from app.extensions import db
from datetime import datetime

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    link_afiliado = db.Column(db.String(255))
    copy_gerada = db.Column(db.Text)
    status = db.Column(db.String(50), default='concluido')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
