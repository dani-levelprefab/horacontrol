from flask import Blueprint, request, jsonify
from models import db, RegistroHoras, Conductor
from utils.calculos import calcular_balance_acumulado
from utils.alertas import actualizar_banco_horas

banco_horas_bp = Blueprint('banco_horas', __name__)

@banco_horas_bp.route('/api/banco-horas/dashboard/', methods=['GET'])
def get_dashboard():
    conductores = Conductor.query.filter_by(activo=True).all()
    
    dashboard = []
    for conductor in conductores:
        registros = RegistroHoras.query.filter_by(conductor_id=conductor.id).all()
        balance = calcular_balance_acumulado(registros)
        
        dashboard.append({
            'conductor_id': conductor.id,
            'nombre': conductor.nombre,
            'balance': balance,
            'total_registros': len(registros)
        })
    
    return jsonify(dashboard)

@banco_horas_bp.route('/api/banco-horas/alertas/', methods=['GET'])
def get_alertas():
    alertas = []
    conductores = Conductor.query.filter_by(activo=True).all()
    
    for conductor in conductores:
        registros = RegistroHoras.query.filter_by(conductor_id=conductor.id).all()
        balance = calcular_balance_acumulado(registros)
        
        if balance >= 8:
            alertas.append({
                'id': f"alert_{conductor.id}_descanso",
                'tipo': 'descanso',
                'conductor_id': conductor.id,
                'message': f"🎯 {conductor.nombre} tiene {balance:.1f}h disponibles para descanso compensatorio"
            })
        
        if balance <= -2:
            alertas.append({
                'id': f"alert_{conductor.id}_deficit",
                'tipo': 'deficit',
                'conductor_id': conductor.id,
                'message': f"⏳ {conductor.nombre} tiene {abs(balance):.1f}h pendientes de trabajar"
            })
    
    return jsonify(alertas)

@banco_horas_bp.route('/api/banco-horas/conductor/<int:conductor_id>', methods=['GET'])
def get_balance_conductor(conductor_id):
    registros = RegistroHoras.query.filter_by(conductor_id=conductor_id).all()
    balance = calcular_balance_acumulado(registros)
    
    return jsonify({
        'conductor_id': conductor_id,
        'balance': balance,
        'total_horas_trabajadas': sum(r.total_horas for r in registros),
        'total_registros': len(registros)
    })

@banco_horas_bp.route('/api/banco-horas/<int:conductor_id>/descanso', methods=['POST'])
def aplicar_descanso(conductor_id):
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor not found'}), 404
    
    data = request.get_json()
    fecha_descanso = data.get('fecha_descanso')
    
    if not fecha_descanso:
        return jsonify({'error': 'fecha_descanso es requerido'}), 400
    
    try:
        registro_descanso = RegistroHoras(
            conductor_id=conductor_id,
            fecha=fecha_descanso,
            hora_entrada='--:--',
            hora_salida='--:--',
            total_horas=-8,
            notas='Compensación de horas'
        )
        
        db.session.add(registro_descanso)
        db.session.commit()
        
        actualizar_banco_horas(conductor_id)
        
        return jsonify({
            'message': 'Descanso compensatorio aplicado',
            'conductor_id': conductor_id,
            'fecha_descanso': fecha_descanso,
            'horas_restadas': -8
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@banco_horas_bp.route('/api/banco-horas/<int:conductor_id>/resetear', methods=['POST'])
def resetear_banco(conductor_id):
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor not found'}), 404
    
    try:
        registros = RegistroHoras.query.filter_by(conductor_id=conductor_id).all()
        for registro in registros:
            db.session.delete(registro)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Banco de horas reseteado',
            'conductor_id': conductor_id,
            'registros_eliminados': len(registros)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
