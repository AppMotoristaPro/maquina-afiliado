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

# Lista expandida de categorias para trazer variedade
CATEGORIAS_ML = [
    "fone de ouvido sem fio", "air fryer", "camera de seguranca wifi", 
    "projetor smart", "garrafa termica inteligente", "mochila impermeavel",
    "robo aspirador", "luminaria led rgb", "kit maquiagem", "relogio smartwatch"
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
        <title>Vórtice | Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Inter', sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); min-height: 100vh; color: #f8fafc; }
            .glass-panel { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 1.5rem; }
            .log-box::-webkit-scrollbar { width: 8px; }
            .log-box::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
        </style>
    </head>
    <body class="p-4 md:p-8">
        <div class="max-w-6xl mx-auto">
            
            <header class="text-center mb-10">
                <h1 class="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500 mb-4">Vórtice Afiliados</h1>
                <p class="text-slate-400 text-lg">Seu estúdio de criação automática de Reels</p>
                <div class="mt-8">
                    <button onclick="buscarProdutos()" id="btnGarimpar" class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-4 px-8 rounded-2xl shadow-lg shadow-blue-500/30 transition-all transform hover:scale-105">
                        🎲 Garimpar Produtos Variados
                    </button>
                </div>
            </header>
            
            <div id="loader" class="hidden text-center my-8">
                <div class="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-white mb-4"></div>
                <p class="text-blue-300 font-semibold text-lg">Aspirando o Mercado Livre... Isso pode levar uns 20 segundos.</p>
            </div>
            
            <div id="produtosGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"></div>
            
            <div class="glass-panel p-6 mb-8 shadow-2xl">
                <h3 class="text-xl font-bold mb-4 flex items-center text-slate-200">
                    <svg class="w-5 h-5 mr-2 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M4 18h16a2 2 0 002-2V6a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                    Console de Produção
                </h3>
                <div id="logBox" class="log-box h-48 overflow-y-auto font-mono text-sm text-green-400 whitespace-pre-wrap p-4 bg-black/50 rounded-xl">Pronto para iniciar. Clique em "Garimpar" para trazer opções de categorias diferentes.</div>
            </div>
            
            <a href="/video" id="btnVideoPronto" class="hidden bg-gradient-to-r from-emerald-500 to-teal-500 text-white text-center font-extrabold py-5 px-8 rounded-2xl shadow-lg shadow-emerald-500/30 text-xl transition-all transform hover:scale-[1.02] mb-10">
                🎥 SEU VÍDEO ESTÁ PRONTO! CLIQUE AQUI PARA BAIXAR
            </a>
        </div>

        <script>
            let pollingInterval;

            async function buscarProdutos() {
                document.getElementById('loader').classList.remove('hidden');
                document.getElementById('produtosGrid').innerHTML = '';
                document.getElementById('btnGarimpar').disabled = true;
                
                try {
                    const res = await fetch('/api/vitrine');
                    const produtos = await res.json();
                    document.getElementById('loader').classList.add('hidden');
                    document.getElementById('btnGarimpar').disabled = false;
                    
                    if(produtos.length === 0) {
                        alert("O Mercado Livre bloqueou a busca dessa vez. Tente novamente.");
                        return;
                    }
                    
                    produtos.forEach(p => {
                        const img = p.midia.imagens_url[0];
                        const precoF = p.preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
                        
                        const card = `
                            <div class="glass-panel overflow-hidden flex flex-col group transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-blue-500/20">
                                <img src="${img}" class="w-full h-48 object-cover bg-white">
                                <div class="p-5 flex flex-col flex-grow">
                                    <h4 class="text-sm font-semibold mb-2 line-clamp-2 text-slate-200">${p.titulo}</h4>
                                    <p class="text-lg font-bold text-emerald-400 mb-4">${precoF}</p>
                                    
                                    <div class="mt-auto space-y-2">
                                        <a href="${p.url_original}" target="_blank" class="block w-full text-center bg-slate-700 hover:bg-slate-600 text-white text-sm font-semibold py-2.5 rounded-xl transition-colors">
                                            1. Pegar Link Meli.la
                                        </a>
                                        <button onclick='iniciarVideo(${JSON.stringify(p).replace(/'/g, "&#39;")})' class="w-full bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold py-2.5 rounded-xl transition-colors">
                                            2. Criar Reels
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `;
                        document.getElementById('produtosGrid').innerHTML += card;
                    });
                } catch(e) {
                    alert("Erro na comunicação com o servidor.");
                    document.getElementById('loader').classList.add('hidden');
                    document.getElementById('btnGarimpar').disabled = false;
                }
            }

            function iniciarVideo(produto) {
                const linkAfiliado = prompt(`PASSO 2: Cole aqui o seu link de afiliado oficial (meli.la) para o produto:\\n\\n${produto.titulo.substring(0,40)}...`);
                
                if(!linkAfiliado) return;
                
                document.getElementById('produtosGrid').innerHTML = '';
                document.getElementById('btnGarimpar').parentElement.classList.add('hidden');
                
                fetch('/api/gerar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ produto: produto, link: linkAfiliado })
                });
                
                pollingInterval = setInterval(atualizarLogs, 2000);
                document.getElementById('logBox').innerHTML = "Iniciando processo...";
            }

            async function atualizarLogs() {
                const res = await fetch('/api/logs');
                const data = await res.json();
                
                const box = document.getElementById('logBox');
                box.innerHTML = data.logs;
                box.scrollTop = box.scrollHeight;
                
                if(!data.ocupado && data.logs.includes("VÍDEO PRONTO")) {
                    clearInterval(pollingInterval);
                    document.getElementById('btnVideoPronto').classList.remove('hidden');
                }
            }
        </script>
    </body>
    </html>
    """
    return html

@app.route('/api/vitrine')
def api_vitrine():
    # Sorteia 4 categorias diferentes para garantir variedade
    categorias_sorteadas = random.sample(CATEGORIAS_ML, 4)
    vitrine = []
    
    # Busca 1 produto campeão para cada categoria sorteada
    for cat in categorias_sorteadas:
        produtos = buscar_produtos_tendencia(cat)
        if produtos:
            vitrine.append(produtos[0])
            
    return jsonify(vitrine)

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
        return "<h2 class='text-center mt-10 text-white font-sans'>Vídeo não encontrado.</h2>", 404
        
    with open(INFO_PATH, "r", encoding="utf-8") as f:
        info = json.load(f)
        
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Seu Reels</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    </head>
    <body class="bg-slate-900 font-sans text-slate-200 min-h-screen flex flex-col items-center py-10 px-4">
        
        <div class="max-w-md w-full bg-slate-800/50 backdrop-blur-xl border border-slate-700 p-6 rounded-3xl shadow-2xl">
            <h3 class="text-lg font-bold text-white mb-6 text-center line-clamp-2">{{ info.titulo }}</h3>
            
            <video class="w-full rounded-2xl shadow-lg bg-black mb-6" controls>
                <source src="/download" type="video/mp4">
            </video>
            
            <a href="/download" class="block w-full bg-emerald-500 hover:bg-emerald-400 text-white text-center font-bold py-4 rounded-xl shadow-lg transition-colors mb-6">
                ⬇ Baixar Vídeo
            </a>
            
            <div class="bg-slate-900/50 border border-slate-700 p-5 rounded-2xl">
                <h4 class="text-blue-400 font-bold mb-2">📝 Sua Copy (Para o Instagram/TikTok)</h4>
                <textarea class="w-full h-40 bg-slate-800 text-slate-300 border border-slate-600 rounded-xl p-3 text-sm focus:outline-none focus:border-blue-500" readonly>{{ info.descricao }}</textarea>
            </div>
            
            <div class="mt-8 text-center">
                <a href="/" class="text-slate-400 hover:text-white font-medium transition-colors">← Voltar ao Painel</a>
            </div>
        </div>
        
    </body>
    </html>
    """
    return render_template_string(html, info=info)

@app.route('/download')
def download_file():
    return send_file(VIDEO_PATH, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

