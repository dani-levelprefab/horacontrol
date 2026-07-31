# routes/banco_horas.py

from flask import Blueprint, request, jsonify
from models import db, Conductor, BancoHoras
from datetime import datetime

banco_horas_bp = Blueprint('banco_horas', __name__, url_prefix='/api/banco-horas')

# ✅ OBTENER BANCO DE HORAS POR CONDUCTOR
@banco_horas_bp.route('/conductor/<int:conductor_id>', methods=['GET'])
def obtener_banco_conductor(conductor_id):
    """GET /api/banco-horas/conductor/1"""
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    
    banco = BancoHoras.query.filter_by(conductor_id=conductor_id).first()
    
    if not banco:
        return jsonify({
            'conductor': conductor.to_dict(),
            'banco': None,
            'mensaje': 'Sin registros de banco de horas aún'
        }), 200
    
    return jsonify({
        'conductor': conductor.to_dict(),
        'banco': banco.to_dict()
    }), 200


# ✅ OBTENER BANCO DE HORAS DE TODOS LOS CONDUCTORES
@banco_horas_bp.route('/', methods=['GET'])
def obtener_banco_todos():
    """GET /api/banco-horas"""
    conductores = Conductor.query.filter_by(activo=True).all()
    
    resultado = []
    for conductor in conductores:
        banco = BancoHoras.query.filter_by(conductor_id=conductor.id).first()
        
        resultado.append({
            'conductor': conductor.to_dict(),
            'banco': banco.to_dict() if banco else {
                'balance_acumulado': 0,
                'descanso_compensatorio_disponible': False,
                'estado': 'Pendiente'
            }
        })
    
    return jsonify({
        'total_conductores': len(resultado),
        'conductores': resultado
    }), 200


# ✅ REGISTRAR DESCANSO COMPENSATORIO
@banco_horas_bp.route('/<int:conductor_id>/descanso', methods=['POST'])
def registrar_descanso(conductor_id):
    """
    POST /api/banco-horas/1/descanso
    Body: { "fecha_descanso": "2026-08-10" }
    """
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    
    banco = BancoHoras.query.filter_by(conductor_id=conductor_id).first()
    
    if not banco:
        return jsonify({'error': 'Sin banco de horas registrado'}), 404
    
    if not banco.descanso_compensatorio_disponible:
        return jsonify({'error': 'No hay descanso compensatorio disponible'}), 400
    
    data = request.get_json()
    if not data.get('fecha_descanso'):
        return jsonify({'error': 'Campo "fecha_descanso" requerido'}), 400
    
    fecha_descanso = datetime.strptime(data['fecha_descanso'], '%Y-%m-%d').date()
    
    # Actualizar banco
    banco.fecha_descanso_tomado = fecha_descanso
    banco.descanso_compensatorio_disponible = False
    banco.balance_acumulado -= 8  # Consumir las 8 horas
    banco.estado = 'Descansado'
    
    db.session.commit()
    
    return jsonify({
        'mensaje': f'Descanso compensatorio registrado para {fecha_descanso}',
        'banco': banco.to_dict()
    }), 200


# ✅ OBTENER ALERTAS ACTIVAS
@banco_horas_bp.route('/alertas/', methods=['GET'])
def obtener_alertas():
    """GET /api/banco-horas/alertas/"""
    conductores = Conductor.query.filter_by(activo=True).all()
    
    alertas = []
    
    for conductor in conductores:
        banco = BancoHoras.query.filter_by(conductor_id=conductor.id).first()
        
        if not banco:
            continue
        
        # Alerta 1: +8h acumuladas (descanso compensatorio disponible)
        if banco.balance_acumulado >= 8 and not banco.descanso_compensatorio_disponible:
            alertas.append({
                'tipo': 'DESCANSO_DISPONIBLE',
                'conductor_id': conductor.id,
                'conductor_nombre': conductor.nombre,
                'email': conductor.email,
                'mensaje': f'{conductor.nombre} ha acumulado {banco.balance_acumulado}h - Planificar descanso',
                'severidad': 'ALTA',
                'fecha': datetime.utcnow().isoformat()
            })
        
        # Alerta 2: -2h pendientes de compensar
        if banco.balance_acumulado <= -2:
            alertas.append({
                'tipo': 'DEFICIT_COMPENSAR',
                'conductor_id': conductor.id,
                'conductor_nombre': conductor.nombre,
                'email': conductor.email,
                'mensaje': f'{conductor.nombre} tiene {abs(banco.balance_acumulado)}h pendientes de compensar',
                'severidad': 'MEDIA',
                'fecha': datetime.utcnow().isoformat()
            })
    
    return jsonify({
        'total_alertas': len(alertas),
        'alertas': alertas
    }), 200


# ✅ RESETEAR BANCO (administrativo - ej: nuevo mes)
@banco_horas_bp.route('/<int:conductor_id>/resetear', methods=['POST'])
def resetear_banco(conductor_id):
    """
    POST /api/banco-horas/1/resetear
    Solo administrador. Resetea el banco de horas.
    """
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    
    banco = BancoHoras.query.filter_by(conductor_id=conductor_id).first()
    
    if banco:
        db.session.delete(banco)
    
    nuevo_banco = BancoHoras(
        conductor_id=conductor_id,
        balance_acumulado=0,
        estado='Pendiente'
    )
    
    db.session.add(nuevo_banco)
    db.session.commit()
    
    return jsonify({
        'mensaje': f'Banco de horas de {conductor.nombre} reseteado',
        'banco': nuevo_banco.to_dict()
    }), 200


# ✅ OBTENER DASHBOARD COMPLETO
@banco_horas_bp.route('/dashboard/', methods=['GET'])
def dashboard():
    """GET /api/banco-horas/dashboard/ - Vista completa para Gustavo + Dani"""
    conductores = Conductor.query.filter_by(activo=True).all()
    
    dashboard_data = []
    
    for conductor in conductores:
        banco = BancoHoras.query.filter_by(conductor_id=conductor.id).first()
        
        # Determinar estado visual
        if not banco:
            estado = 'SIN REGISTROS'
            balance = 0
            alerta = None
        elif banco.balance_acumulado >= 8:
            estado = '⚠️ DESCANSO DISPONIBLE'
            balance = banco.balance_acumulado
            alerta = 'DESCANSO'
        elif banco.balance_acumulado <= -2:
            estado = '⚠️ COMPENSAR HORAS'
            balance = banco.balance_acumulado
            alerta = 'DEFICIT'
        else:
            estado = '✅ NORMAL'
            balance = banco.balance_acumulado
            alerta = None
        
        dashboard_data.append({
            'conductor_id': conductor.id,
            'conductor_nombre': conductor.nombre,
            'email': conductor.email,
            'balance_horas': balance,
            'estado': estado,
            'alerta': alerta,
            'descanso_tomado': banco.fecha_descanso_tomado.isoformat() if banco and banco.fecha_descanso_tomado else None
        })
    
    return jsonify({
        'fecha_consulta': datetime.utcnow().isoformat(),
        'total_conductores': len(dashboard_data),
        'conductores': dashboard_data
    }), 200
