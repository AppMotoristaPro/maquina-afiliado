# render_app.py
from flask import Flask, send_file, render_template_string, request, jsonify
import threading
import os
import json
import random
from app import gerar_video_selecionado
from modules.mineracao.ml_api import buscar_produtos_tendencia

app = Flask(__name__)
VIDEO_PATH = "reels_final.mp4"
LOG_PATH = "process_log.txt"
INFO_PATH = "produto_info.json"

status_sistema = {"ocupado": False}

# Lista de nichos virais pré-programados
NICHOS_VIRAIS = [
    "smartwatch", "fone bluetooth", "robo aspirador", "projetor inteligente", 
    "mini liquidificador", "garrafa termica inteligente", "camera wifi", "luminaria rgb"
]

def escrever_log(mensagem):
    print(mensagem)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(mensagem + "\n")

@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vórtice | Vitrine Automática</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #8b5cf6; --success: #10b981; }
            body { font-family: 'Inter', sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 20px; }
            .container { max-width: 1000px; margin: 0 auto; }
            h1 { text-align: center; font-weight: 800; margin-bottom: 30px; color: var(--primary); }
            
            .header-actions { text-align: center; margin-bottom: 40px; }
            .btn-garimpo { padding: 18px 36px; border: none; border-radius: 12px; background: var(--primary); color: white; font-weight: 800; font-size: 18px; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4); }
            .btn-garimpo:hover { transform: scale(1.05); }
            
            .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
            .card { background: var(--card); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; border: 1px solid #334155; }
            .card-img { width: 100%; height: 200px; object-fit: cover; background: #fff; }
            .card-body { padding: 15px; display: flex; flex-direction: column; flex: 1; }
            .card-title { font-size: 14px; margin: 0 0 10px 0; font-weight: 600; line-height: 1.4; }
            .btn-create { margin-top: auto; background: var(--success); color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; }
            
            .log-container { background: #000; padding: 15px; border-radius: 8px; border: 1px solid #334155; }
            .log-box { height: 200px; overflow-y: auto; font-family: monospace; font-size: 13px; color: #4ade80; white-space: pre-wrap; }
            
            .loader { display: none; text-align: center; margin: 20px; font-weight: bold; color: var(--primary); font-size: 18px; }
            .video-btn { display: none; background: var(--success); width: 100%; padding: 20px; font-size: 20px; margin-top: 20px; text-align: center; text-decoration: none; border-radius: 12px; font-weight: bold; box-sizing: border-box; color: white;}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Vórtice Vitrine Automática</h1>
            
            <div class="header-actions">
                <button onclick="buscarProdutos()" class="btn-garimpo" id="btnGarimpar">🎲 Garimpar Produtos Virais</button>
            </div>
            
            <div id="loader" class="loader">Aspirando o Mercado Livre... Isso leva uns 15 segundos.</div>
            <div id="produtosGrid" class="grid"></div>
            
            <h3>Console de Produção</h3>
            <div class="log-container">
                <div id="logBox" class="log-box">Pronto para iniciar. Clique em Garimpar para ver as opções.</div>
            </div>
            
            <a href="/video" id="btnVideoPronto" class="video-btn">🎥 VÍDEO PRONTO! CLIQUE AQUI PARA BAIXAR</a>
        </div>

        <script>
            let pollingInterval;

            async function buscarProdutos() {
                document.getElementById('loader').style.display = 'block';
                document.getElementById('produtosGrid').innerHTML = '';
                document.getElementById('btnGarimpar').disabled = true;
                
                try {
                    const res = await fetch('/api/vitrine');
                    const produtos = await res.json();
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('btnGarimpar').disabled = false;
                    
                    if(produtos.length === 0) {
                        alert("O Mercado Livre bloqueou a busca dessa vez. Clique em garimpar novamente.");
                        return;
                    }
                    
                    produtos.forEach(p => {
                        const img = p.midia.imagens_url[0];
                        const precoF = p.preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                        const card = `
                            <div class="card">
                                <img src="${img}" class="card-img">
                                <div class="card-body">
                                    <h4 class="card-title">${p.titulo.substring(0, 60)}...</h4>
                                    <p style="color: #4ade80; font-weight: bold; margin-top: 0;">${precoF}</p>
                                    <button class="btn-create" onclick='iniciarVideo(${JSON.stringify(p)})'>Criar Reels</button>
                                </div>
                            </div>
                        `;
                        document.getElementById('produtosGrid').innerHTML += card;
                    });
                } catch(e) {
                    alert("Erro na comunicação com o servidor.");
                    document.getElementById('loader').style.display = 'none';
                    document.getElementById('btnGarimpar').disabled = false;
                }
            }

            function iniciarVideo(produto) {
                const linkAfiliado = prompt(`Cole o seu Link de Afiliado OFICIAL (meli.la) para o produto:\\n\\n${produto.titulo.substring(0,40)}...`);
                
                if(!linkAfiliado) return;
                
                document.getElementById('produtosGrid').innerHTML = '';
                document.getElementById('btnGarimpar').style.display = 'none';
                
                fetch('/api/gerar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ produto: produto, link: linkAfiliado })
                });
                
                pollingInterval = setInterval(atualizarLogs, 2000);
            }

            async function atualizarLogs() {
                const res = await fetch('/api/logs');
                const data = await res.json();
                
                const box = document.getElementById('logBox');
                box.innerHTML = data.logs;
                box.scrollTop = box.scrollHeight;
                
                if(!data.ocupado && data.logs.includes("VÍDEO PRONTO")) {
                    clearInterval(pollingInterval);
                    document.getElementById('btnVideoPronto').style.display = 'block';
                }
            }
        </script>
    </body>
    </html>
    """
    return html

@app.route('/api/vitrine')
def api_vitrine():
    # Sorteia um nicho viral para garantir vídeos diferentes a cada clique
    nicho_sorteado = random.choice(NICHOS_VIRAIS)
    produtos = buscar_produtos_tendencia(nicho_sorteado)
    return jsonify(produtos)

@app.route('/api/gerar', methods=['POST'])
def api_gerar():
    global status_sistema
    if status_sistema["ocupado"]:
        return jsonify({"erro": "Já existe um vídeo sendo gerado!"}), 400
        
    dados = request.json
    produto = dados.get('produto')
    link_afiliado = dados.get('link')
    
    open(LOG_PATH, "w").close()
    if os.path.exists(VIDEO_PATH): os.remove(VIDEO_PATH)
    if os.path.exists(INFO_PATH): os.remove(INFO_PATH)
    
    status_sistema["ocupado"] = True
    
    def worker():
        gerar_video_selecionado(produto, link_afiliado, escrever_log)
        status_sistema["ocupado"] = False
        
    threading.Thread(target=worker).start()
    return jsonify({"sucesso": True})

@app.route('/api/logs')
def api_logs():
    logs = ""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            logs = f.read()
    return jsonify({"logs": logs, "ocupado": status_sistema["ocupado"]})

@app.route('/video')
def video_page():
    if not os.path.exists(INFO_PATH):
        return "Vídeo não encontrado.", 404
        
    with open(INFO_PATH, "r", encoding="utf-8") as f:
        info = json.load(f)
        
    html = """
    <body style="font-family: Arial; background: #0f172a; color: white; padding: 20px; max-width: 500px; margin: auto; text-align: center;">
        <h2>Seu Reels Está Pronto! 🎉</h2>
        <video width="100%" controls style="border-radius: 12px; margin-bottom: 20px;">
            <source src="/download" type="video/mp4">
        </video>
        <a href="/download" style="display: block; padding: 15px; background: #10b981; color: #fff; text-decoration: none; border-radius: 8px; font-weight: bold; margin-bottom: 20px;">⬇ Baixar Vídeo</a>
        <div style="background: #1e293b; padding: 20px; border-radius: 8px; text-align: left;">
            <h4 style="margin-top: 0; color: #8b5cf6;">📝 Copie a sua Legenda</h4>
            <textarea style="width: 100%; height: 150px; padding: 10px; border-radius: 5px; background: #0f172a; color: white; border: 1px solid #334155;" readonly>{{ info.descricao }}</textarea>
        </div>
        <a href="/" style="display: inline-block; margin-top: 20px; color: #94a3b8; text-decoration: none;">← Voltar ao Painel</a>
    </body>
    """
    return render_template_string(html, info=info)

@app.route('/download')
def download_file():
    return send_file(VIDEO_PATH, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

