"""
TDZ API - Servidor Flask para painel web
Rode com: python api.py
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from functools import wraps
import json
import os
import datetime

app = Flask(__name__)
CORS(app)

# ============= CONFIGURAÇÕES =============
CONFIG = {
    "SENHA_PAINEL": "aethtdz2606",
    "PORTA": 5000,
    "ARQUIVO_DB": "tdz_database.json"
}

# ============= BANCO DE DADOS =============
class Database:
    def __init__(self):
        self.arquivo = CONFIG["ARQUIVO_DB"]
    
    def carregar(self):
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "vendas": [], 
                "usuarios": {}, 
                "feedbacks": [], 
                "pendentes": [],
                "config": {"precos": {"vip": 30, "destacar": 15, "global": 20}},
                "canais": []  # Bot preenche isso
            }
    
    def salvar(self, dados):
        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

db = Database()

# ============= AUTENTICAÇÃO =============
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '').replace('Bearer ', '')
        if auth != CONFIG["SENHA_PAINEL"]:
            return jsonify({"erro": "Não autorizado"}), 401
        return f(*args, **kwargs)
    return decorated

# ============= ROTAS =============

@app.route('/')
def painel():
    """Serve o painel.html"""
    try:
        return send_from_directory('.', 'painel.html')
    except:
        return "<h1>Coloque o arquivo painel.html na mesma pasta!</h1>", 404

@app.route('/api/stats')
@require_auth
def stats():
    """Estatísticas gerais"""
    dados = db.carregar()
    vendas = dados.get("vendas", [])
    
    return jsonify({
        "total_vendas": len(vendas),
        "receita_total": sum(v.get("valor", 0) for v in vendas),
        "feedbacks": len(dados.get("feedbacks", [])),
        "pendentes": len(dados.get("pendentes", [])),
        "usuarios": len(dados.get("usuarios", {}))
    })

@app.route('/api/vendas')
@require_auth
def listar_vendas():
    """Lista todas as vendas aprovadas"""
    dados = db.carregar()
    return jsonify(dados.get("vendas", []))

@app.route('/api/vendas/pendentes')
@require_auth
def vendas_pendentes():
    """Lista vendas pendentes (para aprovar)"""
    dados = db.carregar()
    return jsonify(dados.get("pendentes", []))

@app.route('/api/vendas/aprovar', methods=['POST'])
@require_auth
def aprovar_venda():
    """Aprova uma venda pendente"""
    data = request.json
    venda_id = data.get('id')
    
    dados = db.carregar()
    pendentes = dados.get("pendentes", [])
    
    venda = next((v for v in pendentes if v.get('id') == venda_id), None)
    if not venda:
        return jsonify({"erro": "Venda não encontrada"}), 404
    
    # Mover para vendas aprovadas
    dados["pendentes"] = [v for v in pendentes if v.get('id') != venda_id]
    venda["status"] = "aprovado"
    venda["data_aprovacao"] = datetime.datetime.now().isoformat()
    dados["vendas"].append(venda)
    
    # Criar arquivo de sinal para o bot processar (cargo, dm, etc)
    sinal = {
        "tipo": "aprovar_venda",
        "user_id": venda.get("user_id"),
        "produto": venda.get("produto"),
        "venda_id": venda_id
    }
    
    with open(f"sinal_{venda_id}.json", 'w') as f:
        json.dump(sinal, f)
    
    db.salvar(dados)
    return jsonify({"sucesso": True, "venda": venda})

@app.route('/api/config/precos', methods=['GET', 'POST'])
@require_auth
def config_precos():
    """GET: ver preços | POST: atualizar"""
    dados = db.carregar()
    
    if request.method == 'POST':
        novos_precos = request.json
        dados["config"]["precos"] = novos_precos
        db.salvar(dados)
        
        # Sinal para bot atualizar
        with open("sinal_atualizar_precos.json", 'w') as f:
            json.dump({"tipo": "atualizar_precos", "precos": novos_precos}, f)
        
        return jsonify({"sucesso": True})
    
    return jsonify(dados.get("config", {}).get("precos", {}))

@app.route('/api/anunciar', methods=['POST'])
@require_auth
def criar_anuncio():
    """Cria anúncio (bot lê e envia)"""
    data = request.json
    
    anuncio = {
        "tipo": "anuncio",
        "canal_id": data.get('canal_id'),
        "titulo": data.get('titulo'),
        "mensagem": data.get('mensagem'),
        "cor": data.get('cor', 'azul'),
        "criado_em": datetime.datetime.now().isoformat()
    }
    
    # Salvar sinal
    filename = f"anuncio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(anuncio, f)
    
    return jsonify({"sucesso": True, "arquivo": filename})

@app.route('/api/canais')
@require_auth
def listar_canais():
    """Retorna canais (bot atualiza periodicamente)"""
    dados = db.carregar()
    return jsonify(dados.get("canais", []))

# ============= INICIAR =============
if __name__ == '__main__':
    print("=" * 50)
    print("🌐 TDZ API - Painel Web")
    print("=" * 50)
    print(f"📍 URL: http://localhost:{CONFIG['PORTA']}")
    print(f"🔐 Senha: {CONFIG['SENHA_PAINEL']}")
    print("=" * 50)
    print("💡 Coloque painel.html na mesma pasta")
    print("💡 O bot lê os arquivos de sinal e executa as ações")
    print("=" * 50)
    app.run(host='0.0.0.0', port=CONFIG['PORTA'], debug=True)
