# render_app.py
from flask import Flask, send_file
import threading
import os
import time
from app import iniciar

app = Flask(__name__)

@app.route('/')
def home():
    return "Máquina de Afiliados Rodando! Aguarde o processamento e acesse /video"

@app.route('/video')
def download_video():
    caminho_video = "reels_final.mp4"
    if os.path.exists(caminho_video) and os.path.getsize(caminho_video) > 0:
        return send_file(caminho_video, as_attachment=True)
    return "Vídeo não encontrado ou ainda em processamento. Aguarde 2-3 minutos e atualize.", 404

def executar_robo():
    # Pequeno delay para garantir que o servidor subiu
    time.sleep(5)
    print("--- [BOT] Iniciando ciclo de produção ---")
    iniciar()

# A thread inicia aqui, fora do __main__, para o Gunicorn ativar
threading.Thread(target=executar_robo, daemon=True).start()

if __name__ == "__main__":
    # Apenas para testes locais
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

