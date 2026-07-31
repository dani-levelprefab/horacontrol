from flask import Blueprint, request, jsonify
from datetime import datetime
from models import db, RegistroHoras
from utils.calculos import calcular_horas_trabajadas
from utils.alertas import actualizar_banco_horas

horas_bp = Blueprint('horas', __name__)

# GET all registros
@horas_bp.route('/api/horas', methods=['GET'])
def get_registros():
    fecha = request.args.get('fecha')
    conductor_id = request.args.get('conductor_id')
    
    query = RegistroHoras.query
    
    if fecha:
        query = query.filter_by(fecha=fecha)
    if conductor_id:
        query = query.filter_by(conductor_id=conductor_id)
    
    registros = query.all()
    
    return jsonify([{
        'id': r.id,
        'conductor_id': r.conductor_id,
        'fecha': str(r.fecha),
        'hora_entrada': r.hora_entrada,
        'hora_salida': r.hora_salida,
        'total_horas': r.total_horas,
        'notas': r.notas
    } for r in registros])

# POST new registro
@horas_bp.route('/api/horas', methods=['POST'])
def create_registro():
    data = request.get_json()
    
    required = ['conductor_id', 'fecha', 'hora_entrada', 'hora_salida']
    if not all(k in data for k in required):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    try:
        total_horas = calcular_horas_trabajadas(data['hora_entrada'], data['hora_salida'])
        
        registro = RegistroHoras(
            conductor_id=data['conductor_id'],
            fecha=data['fecha'],
            hora_entrada=data['hora_entrada'],
            hora_salida=data['hora_salida'],
            total_horas=total_horas,
            notas=data.get('notas', '')
        )
        
        db.session.add(registro)
        db.session.commit()
        
        # Actualizar banco de horas
        actualizar_banco_horas(data['conductor_id'])
        
        return jsonify({
            'id': registro.id,
            'conductor_id': registro.conductor_id,
            'fecha': str(registro.fecha),
            'hora_entrada': registro.hora_entrada,
            'hora_salida': registro.hora_salida,
            'total_horas': registro.total_horas,
            'notas': registro.notas
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# GET registros by conductor
@horas_bp.route('/api/horas/conductor/<int:conductor_id>', methods=['GET'])
def get_registros_conductor(conductor_id):
    registros = RegistroHoras.query.filter_by(conductor_id=conductor_id).all()
    
    return jsonify([{
        'id': r.id,
        'conductor_id': r.conductor_id,
        'fecha': str(r.fecha),
        'hora_entrada': r.hora_entrada,
        'hora_salida': r.hora_salida,
        'total_horas': r.total_horas,
        'notas': r.notas
    } for r in registros])

# PUT update registro
@horas_bp.route('/api/horas/<int:registro_id>', methods=['PUT'])
def update_registro(registro_id):
    registro = RegistroHoras.query.get(registro_id)
    
    if not registro:
        return jsonify({'error': 'Registro not found'}), 404
    
    data = request.get_json()
    
    try:
        if 'hora_entrada' in data and 'hora_salida' in data:
            registro.hora_entrada = data['hora_entrada']
            registro.hora_salida = data['hora_salida']
            registro.total_horas = calcular_horas_trabajadas(data['hora_entrada'], data['hora_salida'])
        
        if 'notas' in data:
            registro.notas = data['notas']
        
        db.session.commit()
        
        # Actualizar banco de horas
        actualizar_banco_horas(registro.conductor_id)
        
        return jsonify({
            'id': registro.id,
            'conductor_id': registro.conductor_id,
            'fecha': str(registro.fecha),
            'hora_entrada': registro.hora_entrada,
            'hora_salida': registro.hora_salida,
            'total_horas': registro.total_horas,
            'notas': registro.notas
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE registro
@horas_bp.route('/api/horas/<int:registro_id>', methods=['DELETE'])
def delete_registro(registro_id):
    registro = RegistroHoras.query.get(registro_id)
    
    if not registro:
        return jsonify({'error': 'Registro not found'}), 404
    
    conductor_id = registro.conductor_id
    
    try:
        db.session.delete(registro)
        db.session.commit()
        
        # Actualizar banco de horas
        actualizar_banco_horas(conductor_id)
        
        return jsonify({'message': 'Registro deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
