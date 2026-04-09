# render_app.py
from flask import Flask, send_file
import threading
import os
import time
import sys
from app import iniciar

app = Flask(__name__)

# Caminho do vídeo
VIDEO_PATH = "reels_final.mp4"

@app.route('/')
def home():
    return "Servidor Ativo. Verifique os logs para acompanhar o progresso do robô."

@app.route('/video')
def download_video():
    if os.path.exists(VIDEO_PATH):
        tamanho = os.path.getsize(VIDEO_PATH)
        if tamanho > 0:
            return send_file(VIDEO_PATH, as_attachment=True)
    return f"Vídeo ainda não processado. Tamanho atual: {os.path.getsize(VIDEO_PATH) if os.path.exists(VIDEO_PATH) else 0} bytes", 404

def rodar_automacao():
    print("--- [SISTEMA] Iniciando limpeza de ambiente ---")
    if os.path.exists(VIDEO_PATH):
        os.remove(VIDEO_PATH)
        print("--- [SISTEMA] Vídeo antigo removido ---")
    
    # Delay para o Render estabilizar
    time.sleep(10)
    
    print("--- [SISTEMA] Chamando a função iniciar() do app.py ---")
    try:
        iniciar()
        print("--- [SISTEMA] Ciclo de iniciar() finalizado com sucesso ---")
    except Exception as e:
        print(f"--- [ERRO CRÍTICO NO ROBÔ] {e} ---")

# Inicia a thread de forma global e forçada
bot_thread = threading.Thread(target=rodar_automacao, daemon=True)
bot_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

