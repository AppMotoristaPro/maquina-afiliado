# render_app.py
from flask import Flask
import threading
from app import iniciar

app = Flask(__name__)

@app.route('/')
def home():
    return "Máquina de Afiliados Rodando!"

def executar_robo():
    # Chama a função principal do seu app.py
    iniciar()

if __name__ == "__main__":
    # Inicia o robô em uma thread separada
    threading.Thread(target=executar_robo).start()
    # Inicia o servidor web na porta 10000 (padrão do Render)
    app.run(host="0.0.0.0", port=10000)

