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
    if os.path.exists(VIDEO_PATH):
        return "Vídeo pronto! Vá para /video para baixar."
    return "Máquina processando o vídeo... Acompanhe os logs do Render."

@app.route('/video')
def download_video():
    if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 0:
        return send_file(VIDEO_PATH, as_attachment=True)
    return "O vídeo ainda está sendo gerado. Tente novamente em 2 minutos.", 404

def loop_principal():
    time.sleep(15)
    if os.path.exists(VIDEO_PATH):
        os.remove(VIDEO_PATH)
    print("--- [SISTEMA] Iniciando ciclo... ---")
    iniciar()

threading.Thread(target=loop_principal, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

