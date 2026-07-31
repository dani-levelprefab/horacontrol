import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from config import Config
from models import db

app = Flask(__name__, static_folder='.', static_url_path='')
app.config.from_object(Config)
CORS(app)

# Inicializar BD
db.init_app(app)

# Ruta de login (sin protección)
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

# Importar y registrar blueprints DESPUÉS de crear app
from routes.conductores import conductores_bp
from routes.horas import horas_bp
from routes.banco_horas import banco_horas_bp

app.register_blueprint(conductores_bp)
app.register_blueprint(horas_bp)
app.register_blueprint(banco_horas_bp)

# Servir archivos estáticos
@app.route('/logo.png')
def serve_logo():
    return send_from_directory('.', 'logo.png')

# Servir index.html
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Crear tablas si no existen
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
