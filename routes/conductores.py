from flask import Blueprint, request, jsonify
from models import db, Conductor

conductores_bp = Blueprint('conductores', __name__)

# GET all conductores
@conductores_bp.route('/api/conductores', methods=['GET'])
def get_conductores():
    activo = request.args.get('activo')
    
    if activo:
        activo_bool = activo.lower() == 'true'
        conductores = Conductor.query.filter_by(activo=activo_bool).all()
    else:
        conductores = Conductor.query.all()
    
    return jsonify([{
        'id': c.id,
        'nombre': c.nombre,
        'email': c.email,
        'activo': c.activo
    } for c in conductores])

# POST new conductor
@conductores_bp.route('/api/conductores', methods=['POST'])
def create_conductor():
    data = request.get_json()
    
    if not data or not data.get('nombre'):
        return jsonify({'error': 'nombre es requerido'}), 400
    
    try:
        conductor = Conductor(
            nombre=data.get('nombre'),
            email=data.get('email', ''),
            activo=True
        )
        db.session.add(conductor)
        db.session.commit()
        
        return jsonify({
            'id': conductor.id,
            'nombre': conductor.nombre,
            'email': conductor.email,
            'activo': conductor.activo
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# GET single conductor
@conductores_bp.route('/api/conductores/<int:conductor_id>', methods=['GET'])
def get_conductor(conductor_id):
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor not found'}), 404
    
    return jsonify({
        'id': conductor.id,
        'nombre': conductor.nombre,
        'email': conductor.email,
        'activo': conductor.activo
    })

# PUT update conductor
@conductores_bp.route('/api/conductores/<int:conductor_id>', methods=['PUT'])
def update_conductor(conductor_id):
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'nombre' in data:
            conductor.nombre = data['nombre']
        if 'email' in data:
            conductor.email = data['email']
        if 'activo' in data:
            conductor.activo = data['activo']
        
        db.session.commit()
        
        return jsonify({
            'id': conductor.id,
            'nombre': conductor.nombre,
            'email': conductor.email,
            'activo': conductor.activo
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE conductor
@conductores_bp.route('/api/conductores/<int:conductor_id>', methods=['DELETE'])
def delete_conductor(conductor_id):
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor not found'}), 404
    
    try:
        db.session.delete(conductor)
        db.session.commit()
        return jsonify({'message': 'Conductor deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
