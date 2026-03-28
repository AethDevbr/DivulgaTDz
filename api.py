"""
TDZ API - Painel Web para Railway
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from functools import wraps
import json
import os
import datetime
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# ============= CONFIG =============
CONFIG = {
    "SENHA_PAINEL": os.getenv("PAINEL_SENHA", "tdz2026"),
    "MONGODB_URI": os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
    "DB_NAME": "tdz_bot"
}

# ============= MONGODB =============
try:
    client = MongoClient(CONFIG["MONGODB_URI"])
    db = client[CONFIG["DB_NAME"]]
    print("✅ Conectado ao MongoDB!")
except Exception as e:
    print(f"❌ Erro MongoDB: {e}")
    db = None

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
        return send_file('painel.html')
    except:
        return "<h1>Erro: painel.html não encontrado</h1>", 404

@app.route('/api/stats')
@require_auth
def stats():
    """Estatísticas gerais"""
    vendas_col = db["vendas"] if db else None
    
    if vendas_col:
        total_vendas = vendas_col.count_documents({"status": "aprovado"})
        receita = sum(v.get("valor", 0) for v in vendas_col.find({"status": "aprovado"}))
        pendentes = vendas_col.count_documents({"status": "pendente"})
    else:
        dados = carregar_json()
        vendas = [v for v in dados.get("vendas", []) if v.get("status") == "aprovado"]
        total_vendas = len(vendas)
        receita = sum(v.get("valor", 0) for v in vendas)
        pendentes = len(dados.get("pendentes", []))
    
    return jsonify({
        "total_vendas": total_vendas,
        "receita_total": receita,
        "pendentes": pendentes
    })

@app.route('/api/vendas')
@require_auth
def listar_vendas():
    """Lista vendas aprovadas"""
    vendas_col = db["vendas"] if db else None
    
    if vendas_col:
        vendas = list(vendas_col.find({"status": "aprovado"}, {"_id": 0}))
    else:
        dados = carregar_json()
        vendas = dados.get("vendas", [])
    
    return jsonify(vendas)

@app.route('/api/vendas/pendentes')
@require_auth
def vendas_pendentes():
    """Lista vendas pendentes"""
    vendas_col = db["vendas"] if db else None
    
    if vendas_col:
        pendentes = list(vendas_col.find({"status": "pendente"}, {"_id": 0}))
    else:
        dados = carregar_json()
        pendentes = dados.get("pendentes", [])
    
    return jsonify(pendentes)

@app.route('/api/vendas/aprovar', methods=['POST'])
@require_auth
def aprovar_venda():
    """Aprova uma venda"""
    data = request.json
    venda_id = data.get('id')
    
    vendas_col = db["vendas"] if db else None
    
    if vendas_col:
        venda = vendas_col.find_one({"id": venda_id})
        if not venda:
            return jsonify({"erro": "Venda não encontrada"}), 404
        
        vendas_col.update_one(
            {"id": venda_id},
            {"$set": {"status": "aprovado", "data_aprovacao": datetime.datetime.now().isoformat()}}
        )
    else:
        # Fallback JSON
        dados = carregar_json()
        pendentes = dados.get("pendentes", [])
        venda = next((v for v in pendentes if v.get('id') == venda_id), None)
        
        if not venda:
            return jsonify({"erro": "Venda não encontrada"}), 404
        
        dados["pendentes"] = [v for v in pendentes if v.get('id') != venda_id]
        venda["status"] = "aprovado"
        venda["data_aprovacao"] = datetime.datetime.now().isoformat()
        dados["vendas"].append(venda)
        salvar_json(dados)
    
    return jsonify({"sucesso": True})

# ============= FUNÇÕES AUXILIARES =============
def carregar_json():
    try:
        with open("tdz_database.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"vendas": [], "pendentes": [], "canais": [], "config": {}}

def salvar_json(dados):
    with open("tdz_database.json", 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# ============= INICIAR =============
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
