# render_app.py
from flask import Flask, send_file
import threading
import os
import time
from app import iniciar

app = Flask(__name__)
VIDEO_PATH = "reels_final.mp4"

@app.route('/')
def home():
    return "Máquina de Afiliados Online. Verifique os logs do Render para o progresso."

@app.route('/video')
def download_video():
    if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 0:
        return send_file(VIDEO_PATH, as_attachment=True)
    return "Vídeo ainda não disponível. Verifique os logs.", 404

def executar_robo():
    print("--- [SISTEMA] Aguardando estabilização do servidor... ---")
    if os.path.exists(VIDEO_PATH):
        os.remove(VIDEO_PATH)
    time.sleep(15) 
    iniciar()

# Thread disparada pelo Gunicorn
threading.Thread(target=executar_robo, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

