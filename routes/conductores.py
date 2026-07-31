# routes/conductores.py

from flask import Blueprint, request, jsonify
from models import db, Conductor
from datetime import datetime

conductores_bp = Blueprint('conductores', __name__, url_prefix='/api/conductores')

# ✅ CREAR CONDUCTOR
@conductores_bp.route('/', methods=['POST'])
def crear_conductor():
    """
    POST /api/conductores
    Body: { "nombre": "Juan Pérez", "email": "juan@example.com" }
    """
    data = request.get_json()
    
    if not data or not data.get('nombre'):
        return jsonify({'error': 'Campo "nombre" requerido'}), 400
    
    # Validar si existe
    if Conductor.query.filter_by(nombre=data['nombre']).first():
        return jsonify({'error': f"Conductor {data['nombre']} ya existe"}), 409
    
    nuevo_conductor = Conductor(
        nombre=data['nombre'],
        email=data.get('email'),
        activo=True
    )
    
    db.session.add(nuevo_conductor)
    db.session.commit()
    
    return jsonify({
        'mensaje': 'Conductor creado exitosamente',
        'conductor': nuevo_conductor.to_dict()
    }), 201


# ✅ OBTENER TODOS LOS CONDUCTORES
@conductores_bp.route('/', methods=['GET'])
def obtener_conductores():
    """GET /api/conductores"""
    activo = request.args.get('activo', type=bool)
    
    query = Conductor.query
    if activo is not None:
        query = query.filter_by(activo=activo)
    
    conductores = query.all()
    
    return jsonify({
        'total': len(conductores),
        'conductores': [c.to_dict() for c in conductores]
    }), 200


# ✅ OBTENER CONDUCTOR POR ID
@conductores_bp.route('/<int:conductor_id>', methods=['GET'])
def obtener_conductor(conductor_id):
    """GET /api/conductores/1"""
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    
    return jsonify(conductor.to_dict()), 200


# ✅ ACTUALIZAR CONDUCTOR
@conductores_bp.route('/<int:conductor_id>', methods=['PUT'])
def actualizar_conductor(conductor_id):
    """
    PUT /api/conductores/1
    Body: { "nombre": "Juan Nuevo", "email": "nuevo@example.com", "activo": false }
    """
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    
    data = request.get_json()
    
    if 'nombre' in data:
        # Validar no duplicar nombre
        duplicado = Conductor.query.filter_by(nombre=data['nombre']).filter(Conductor.id != conductor_id).first()
        if duplicado:
            return jsonify({'error': f"Nombre {data['nombre']} ya existe"}), 409
        conductor.nombre = data['nombre']
    
    if 'email' in data:
        conductor.email = data['email']
    
    if 'activo' in data:
        conductor.activo = data['activo']
    
    db.session.commit()
    
    return jsonify({
        'mensaje': 'Conductor actualizado exitosamente',
        'conductor': conductor.to_dict()
    }), 200


# ✅ ELIMINAR CONDUCTOR
@conductores_bp.route('/<int:conductor_id>', methods=['DELETE'])
def eliminar_conductor(conductor_id):
    """DELETE /api/conductores/1"""
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    
    db.session.delete(conductor)
    db.session.commit()
    
    return jsonify({
        'mensaje': f'Conductor {conductor.nombre} eliminado exitosamente'
    }), 200
