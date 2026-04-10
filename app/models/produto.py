from app.extensions import db
from datetime import datetime
import json

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(255), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    url_original = db.Column(db.Text, nullable=False)
    imagens_json = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def set_imagens(self, lista): self.imagens_json = json.dumps(lista)
    def get_imagens(self): return json.loads(self.imagens_json)
