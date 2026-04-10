import os
from pathlib import Path

def criar_projeto():
    # Nome do projeto e estrutura
    base_path = Path(".")
    
    estrutura = [
        "app/models",
        "app/repositories",
        "app/rotas",
        "app/services",
        "app/static/css",
        "app/templates/dashboard",
        "app/templates/errors"
    ]

    print("🏗️ Criando estrutura de pastas...")
    for pasta in estrutura:
        Path(base_path / pasta).mkdir(parents=True, exist_ok=True)

    # Dicionário de arquivos e conteúdos
    arquivos = {
        # --- RAIZ ---
        "requirements.txt": """Flask==3.0.3
gunicorn==22.0.0
moviepy==1.0.3
edge-tts
curl_cffi
beautifulsoup4
Pillow
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
python-dotenv==1.0.1
requests
""",
        ".env": """DATABASE_URL=postgresql://neondb_owner:npg_UBg0b7YKqLPm@ep-super-heart-afa7ngcb-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=maquina-comissao-ultra-secret
""",
        "config.py": """import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    db_url = os.environ.get('DATABASE_URL', '')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
""",
        "run.py": """from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
""",

        # --- APP CORE ---
        "app/__init__.py": """from flask import Flask
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
""",
        "app/extensions.py": """from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
""",

        # --- MODELS ---
        "app/models/produto.py": """from app.extensions import db
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
""",
        "app/models/video.py": """from app.extensions import db
from datetime import datetime

class Video(db.Model):
    __tablename__ = 'videos'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    link_afiliado = db.Column(db.String(255))
    copy_gerada = db.Column(db.Text)
    status = db.Column(db.String(50), default='concluido')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
""",

        # --- SERVICES ---
        "app/services/mineracao_service.py": """from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def garimpar_produtos(termo):
    url = f"https://lista.mercadolivre.com.br/{termo.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
    try:
        res = requests.get(url, impersonate="chrome110", headers=headers, timeout=30)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = [a['href'].split('#')[0].split('?')[0] for a in soup.find_all('a', href=True) if 'produto.mercadolivre.com.br/MLB-' in a['href'] or '/p/MLB' in a['href']]
        
        resultados = []
        for url_p in list(set(links))[:8]:
            if len(resultados) >= 4: break
            rp = requests.get(url_p, impersonate="chrome110", timeout=30)
            soup_p = BeautifulSoup(rp.text, 'html.parser')
            titulo = soup_p.find('h1').text.strip() if soup_p.find('h1') else "Produto"
            preco = float(re.search(r'"price":\s*([\d\.]+)', rp.text).group(1)) if re.search(r'"price":\s*([\d\.]+)', rp.text) else 0.0
            imgs = list(set(re.findall(r'https://http2\.mlstatic\.com/D_NQ_NP_[\w\-]+-O\.webp', rp.text)))
            if len(imgs) >= 2:
                resultados.append({"titulo": titulo, "preco": preco, "url": url_p, "imagens": imgs[:6]})
        return resultados
    except: return []
""",
        "app/services/locucao_service.py": """import asyncio
import edge_tts
import json
import os

async def gerar_voz_e_legenda(texto, path_audio, path_json):
    communicate = edge_tts.Communicate(texto, "pt-BR-ThalitaNeural", rate="+5%")
    subs = []
    with open(path_audio, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio": f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 10000000.0
                subs.append({"text": chunk["text"], "start": start, "end": start + (chunk["duration"]/10000000.0)})
    with open(path_json, "w", encoding="utf-8") as f: json.dump(subs, f)

def executar_locucao(produto_titulo, preco):
    os.makedirs("downloads", exist_ok=True)
    txt = f"Olha esse achadinho! {produto_titulo[:50]}. Por apenas {preco} reais. Link na Bio!"
    p_audio, p_json = "downloads/voz.mp3", "downloads/leg.json"
    asyncio.run(gerar_voz_e_legenda(txt, p_audio, p_json))
    return p_audio, p_json
""",
        "app/services/video_service.py": """import os
import requests
import PIL.Image, PIL.ImageFilter, PIL.ImageDraw, PIL.ImageFont
import numpy as np
import json
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip

def renderizar_video(imagens_urls, audio_path, json_path, logger):
    W, H = 480, 854
    clips = []
    logger("--- [EDITOR] Baixando Imagens ---")
    for i, url in enumerate(imagens_urls[:4]):
        img_data = requests.get(url).content
        with open(f"downloads/i_{i}.jpg", "wb") as f: f.write(img_data)
        
        img = PIL.Image.open(f"downloads/i_{i}.jpg").convert("RGB")
        bg = img.resize((W,H), PIL.Image.Resampling.LANCZOS).filter(PIL.ImageFilter.GaussianBlur(15))
        fg = img.resize((W-40, int((W-40)*(img.height/img.width))), PIL.Image.Resampling.LANCZOS)
        
        final_slide = PIL.Image.fromarray(np.array(bg))
        final_slide.paste(fg, (20, (H-fg.height)//2))
        clips.append(ImageClip(np.array(final_slide)).set_duration(3.0))

    video = concatenate_videoclips(clips, method="compose")
    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio).set_duration(audio.duration)

    # Legendas dinâmicas com Pillow (Bypass ImageMagick)
    logger("--- [EDITOR] Aplicando Legendas ---")
    with open(json_path, "r") as f: data = json.load(f)
    leg_clips = []
    for item in data:
        txt = item["text"].upper()
        if len(txt) < 2: continue
        canvas = PIL.Image.new("RGBA", (W, 100), (0,0,0,0))
        draw = PIL.ImageDraw.Draw(canvas)
        draw.text((W//2, 50), txt, fill="yellow", stroke_width=2, stroke_fill="black", anchor="mm")
        l_clip = ImageClip(np.array(canvas)).set_start(item["start"]).set_end(item["end"]).set_position(("center", H-150))
        leg_clips.append(l_clip)

    final_video = CompositeVideoClip([video] + leg_clips)
    final_video.write_videofile("reels_final.mp4", fps=20, codec="libx264", preset="ultrafast", logger=None)
    return "reels_final.mp4"
""",

        # --- ROTAS ---
        "app/rotas/dashboard_bp.py": """from flask import Blueprint, render_template
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index(): return render_template('dashboard/index.html')

@dashboard_bp.route('/video')
def video(): return render_template('dashboard/video.html')
""",
        "app/rotas/api_bp.py": """from flask import Blueprint, request, jsonify
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
def api_logs(): return jsonify({"logs": "\\n".join(log_list)})
""",

        # --- TEMPLATES (Tailwind) ---
        "app/templates/base.html": """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Máquina de Comissão</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>body { background: #0f172a; color: white; }</style>
</head>
<body class="p-5">
    <div class="max-w-4xl mx-auto">
        {% block content %}{% endblock %}
    </div>
</body>
</html>""",
        "app/templates/dashboard/index.html": """{% extends 'base.html' %}
{% block content %}
<h1 class="text-3xl font-black text-blue-500 mb-5 text-center">🤖 MÁQUINA DE COMISSÃO</h1>
<div class="flex gap-2 mb-10">
    <input id="nicho" class="flex-1 p-3 rounded bg-slate-800 border border-slate-700" placeholder="Digite um nicho...">
    <button onclick="buscar()" class="bg-blue-600 px-6 rounded font-bold">GARIMPAR</button>
</div>
<div id="grid" class="grid grid-cols-2 gap-4 mb-10"></div>
<div class="bg-black p-5 rounded font-mono text-green-500 h-40 overflow-y-auto" id="logs">Console pronto...</div>
<script>
    async function buscar() {
        const n = document.getElementById('nicho').value;
        const res = await fetch('/api/garimpar?nicho=' + n);
        const data = await res.json();
        const grid = document.getElementById('grid');
        grid.innerHTML = '';
        data.forEach(p => {
            grid.innerHTML += `<div class="bg-slate-800 p-4 rounded border border-slate-700">
                <img src="${p.imagens[0]}" class="h-32 w-full object-cover rounded mb-2">
                <h3 class="text-sm font-bold truncate">${p.titulo}</h3>
                <button onclick='gerar(${JSON.stringify(p)})' class="w-full bg-green-600 mt-2 py-2 rounded text-xs font-bold">CRIAR REELS</button>
            </div>`;
        });
    }
    async function gerar(p) {
        const link = prompt("Cole seu link meli.la:");
        if(!link) return;
        await fetch('/api/produzir', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({...p, link_afiliado: link})
        });
        setInterval(async () => {
            const r = await fetch('/api/logs');
            const d = await r.json();
            document.getElementById('logs').innerText = d.logs;
            if(d.logs.includes("VÍDEO PRONTO")) window.location.href = '/video';
        }, 3000);
    }
</script>
{% endblock %}""",
        "app/templates/dashboard/video.html": """{% extends 'base.html' %}
{% block content %}
<h1 class="text-2xl font-bold mb-5 text-center">VÍDEO GERADO COM SUCESSO!</h1>
<div class="flex flex-col items-center">
    <video controls class="w-72 rounded-xl border-4 border-slate-700 shadow-2xl mb-5">
        <source src="/api/logs" type="video/mp4"> </video>
    <p class="text-slate-400 mb-10 text-center">O arquivo reels_final.mp4 foi salvo na raiz do projeto.</p>
    <a href="/" class="text-blue-500">← Voltar e Criar Outro</a>
</div>
{% endblock %}"""
    }

    print("📝 Escrevendo arquivos...")
    for caminho, conteudo in arquivos.items():
        with open(base_path / caminho, "w", encoding="utf-8") as f:
            f.write(conteudo)
        # Cria arquivos __init__.py vazios onde necessário
        if "/" in caminho:
            pasta_init = Path(base_path / caminho.split("/")[0] / "__init__.py")
            if not pasta_init.exists(): pasta_init.touch()

    print("\n✅ PROJETO CONSTRUÍDO COM SUCESSO!")
    print("Próximos passos:")
    print("1. Instale as dependências: pip install -r requirements.txt")
    print("2. Rode o sistema: python run.py")

if __name__ == "__main__":
    criar_projeto()

