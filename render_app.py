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
    return "Máquina de Afiliados Ativa. Verifique os logs para ver o progresso!"

@app.route('/video')
def download_video():
    if os.path.exists(VIDEO_PATH) and os.path.getsize(VIDEO_PATH) > 0:
        return send_file(VIDEO_PATH, as_attachment=True)
    return "Vídeo ainda não processado. Aguarde a mensagem 'VÍDEO PRONTO' nos logs.", 404

def loop_principal():
    # Dá tempo para o Render registrar que o serviço subiu (evita restarts)
    time.sleep(20)
    print("--- [SISTEMA] Iniciando ciclo de produção... ---")
    if os.path.exists(VIDEO_PATH):
        os.remove(VIDEO_PATH)
    
    try:
        iniciar()
    except Exception as e:
        print(f"--- [ERRO CRÍTICO] {e} ---")

# Dispara o robô em background
threading.Thread(target=loop_principal, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

