from app.extensions import db
from datetime import datetime

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    link_afiliado = db.Column(db.String(255), nullable=False)
    copy_gerada = db.Column(db.Text, nullable=False)
    caminho_arquivo = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='processando') 
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    
    produto = db.relationship('Produto', backref=db.backref('videos', lazy=True))

