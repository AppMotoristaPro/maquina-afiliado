# render_app.py
from flask import Flask, send_file
import threading
import os
from app import iniciar

app = Flask(__name__)

@app.route('/')
def home():
    return "Máquina de Afiliados Ativa! Acesse /video para baixar o resultado após o processamento."

@app.route('/video')
def download_video():
    # Caminho do vídeo gerado
    caminho_video = "reels_final.mp4"
    if os.path.exists(caminho_video):
        return send_file(caminho_video, as_attachment=True)
    else:
        return "O vídeo ainda não foi gerado ou o processo falhou. Verifique os logs do Render.", 404

def executar_robo():
    # Inicia a mineração e edição
    iniciar()

if __name__ == "__main__":
    # Inicia o robô em segundo plano
    threading.Thread(target=executar_robo).start()
    # Porta padrão do Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

