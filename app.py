import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models import db, init_db
from routes import conductores_bp, horas_bp, banco_horas_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Inicializar BD
db.init_app(app)

# Registrar blueprints
app.register_blueprint(conductores_bp)
app.register_blueprint(horas_bp)
app.register_blueprint(banco_horas_bp)

# Servir index.html
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Crear tablas si no existen
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Para Render: usar puerto dinámico desde variable de entorno
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
