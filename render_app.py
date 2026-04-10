# render_app.py
from flask import Flask, send_file, render_template_string
import threading
import os
import time
import json
from app import iniciar

app = Flask(__name__)
VIDEO_PATH = "reels_final.mp4"
LOG_PATH = "process_log.txt"
INFO_PATH = "produto_info.json"

def escrever_log(mensagem):
    """Escreve o log no terminal e no arquivo para o site ler"""
    print(mensagem)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(mensagem + "\n")

@app.route('/')
def home():
    # Lê os logs; a página se atualiza sozinha a cada 5 segundos
    logs = "Aguardando inicialização do sistema..."
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            logs = f.read()
            
    html = """
    <html>
    <head>
        <meta http-equiv="refresh" content="5">
        <meta charset="utf-8">
        <title>Vórtice Afiliados | Painel</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #121212; color: #fff; padding: 20px; }
            .log-box { background: #000; color: #0f0; padding: 15px; height: 350px; overflow-y: scroll; font-family: monospace; white-space: pre-wrap; border-radius: 8px; border: 1px solid #333; margin-bottom: 20px; }
            .btn { display: inline-block; padding: 15px 30px; background: #007bff; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 18px; transition: 0.3s; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h2>🤖 Vórtice Bot - Status Ao Vivo</h2>
        <div class="log-box">{{ logs }}</div>
        <a href="/video" class="btn">▶ Acessar Vídeo e Link de Afiliado</a>
    </body>
    </html>
    """
    return render_template_string(html, logs=logs)

@app.route('/video')
def video_page():
    if not os.path.exists(VIDEO_PATH) or not os.path.exists(INFO_PATH):
        return "<h2 style='font-family: Arial; text-align: center; margin-top: 50px;'>O vídeo ainda não está pronto. Acompanhe os logs no painel!</h2>", 404
        
    with open(INFO_PATH, "r", encoding="utf-8") as f:
        info = json.load(f)
        
    html = """
    <html>
    <head><meta charset="utf-8"><title>Seu Reels</title></head>
    <body style="font-family: Arial; background: #f4f4f9; padding: 20px; max-width: 500px; margin: auto; text-align: center;">
        <h3 style="color: #333;">{{ info.titulo }}</h3>
        
        <video width="100%" controls style="border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); margin-bottom: 20px; background: #000;">
            <source src="/download" type="video/mp4">
        </video>
        
        <a href="/download" style="display: block; padding: 15px; background: #28a745; color: #fff; text-decoration: none; border-radius: 8px; font-weight: bold; margin-bottom: 20px;">⬇ Baixar Vídeo</a>
        
        <div style="background: #fff; padding: 20px; border-radius: 8px; text-align: left; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h4 style="margin-top: 0; color: #007bff; margin-bottom: 5px;">🔗 Link Base do Produto</h4>
            <input type="text" value="{{ info.link }}" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 5px;" readonly>
            <p style="font-size: 13px; color: #d9534f; margin-top: 0; font-weight: bold;">⚠️ Atenção: Copie o link acima e cole no aplicativo do Mercado Livre para gerar o seu "meli.la" e garantir a comissão!</p>
            
            <h4 style="color: #ff5722; margin-top: 20px;">📝 Descrição para Copiar</h4>
            <textarea style="width: 100%; height: 120px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;" readonly>{{ info.descricao }}</textarea>
        </div>
        
        <a href="/" style="display: inline-block; margin-top: 20px; color: #666; text-decoration: none;">← Voltar ao Painel</a>
    </body>
    </html>
    """
    return render_template_string(html, info=info)

@app.route('/download')
def download_file():
    return send_file(VIDEO_PATH, as_attachment=True)

def loop_principal():
    time.sleep(10)
    # Limpa log antigo para não acumular
    open(LOG_PATH, "w").close() 
    escrever_log("--- [SISTEMA] Iniciando novo ciclo do robô ---")
    
    # Limpa arquivos da rodada anterior
    if os.path.exists(VIDEO_PATH): os.remove(VIDEO_PATH)
    if os.path.exists(INFO_PATH): os.remove(INFO_PATH)
    
    try:
        iniciar(escrever_log) # Passa a função de log do painel web para dentro do robô
    except Exception as e:
        escrever_log(f"--- [ERRO CRÍTICO] {e} ---")

# Inicia a mineração e edição em segundo plano
threading.Thread(target=loop_principal, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

