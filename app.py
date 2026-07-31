import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from config import Config
from models import db

# ===== CREAR APLICACIÓN =====
app = Flask(__name__, static_folder='.', static_url_path='')
app.config.from_object(Config)

# ===== CONFIGURAR CORS CORRECTAMENTE =====
CORS(app, 
     origins=['https://horacontrol.onrender.com', 'http://localhost:5000', 'http://127.0.0.1:5000'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# Inicializar BD
db.init_app(app)

# ===== RUTAS DE LOGIN =====
@app.route('/api/login', methods=['POST'])
def login():
    from utils.auth import verify_credentials
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if verify_credentials(username, password):
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'token': 'valid'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Usuario o contraseña incorrectos'
        }), 401

# ===== REGISTRAR BLUEPRINTS =====
from routes.conductores import conductores_bp
from routes.horas import horas_bp
from routes.banco_horas import banco_horas_bp

app.register_blueprint(conductores_bp)
app.register_blueprint(horas_bp)
app.register_blueprint(banco_horas_bp)

# ===== SERVIR ARCHIVOS ESTÁTICOS =====
@app.route('/logo.png')
def serve_logo():
    return send_from_directory('.', 'logo.png')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ruta no encontrada'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Error interno del servidor'}), 500

# ===== CREAR TABLAS =====
with app.app_context():
    db.create_all()
    print("✅ Tablas de BD creadas/verificadas")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
