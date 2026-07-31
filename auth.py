import os
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# CREDENCIALES (CAMBIA ESTOS)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'horacontrol2024')

# Hash de contraseña (más seguro)
PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD)

def verify_credentials(username, password):
    """Verifica username y password"""
    return username == ADMIN_USERNAME and check_password_hash(PASSWORD_HASH, password)

def require_auth(f):
    """Decorador para proteger rutas API"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        
        if not auth or not verify_credentials(auth.username, auth.password):
            return jsonify({'error': 'Unauthorized'}), 401
        
        return f(*args, **kwargs)
    return decorated

def get_token(username, password):
    """Retorna token si credenciales son válidas"""
    if verify_credentials(username, password):
        return {'token': 'valid', 'message': 'Login exitoso'}
    return None
