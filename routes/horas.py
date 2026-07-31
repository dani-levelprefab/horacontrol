# routes/horas.py

from flask import Blueprint, request, jsonify
from models import db, Conductor, RegistroHoras, BancoHoras
from datetime import datetime, date
from utils.calculos import calcular_horas_trabajadas
from utils.alertas import generar_alertas, actualizar_banco_horas

horas_bp = Blueprint('horas', __name__, url_prefix='/api/horas')

# ✅ REGISTRAR HORAS DEL DÍA
@horas_bp.route('/', methods=['POST'])
def registrar_horas():
    """
    POST /api/horas
    Body: {
        "conductor_id": 1,
        "fecha": "2026-08-03",
        "hora_entrada": "07:30",
        "hora_salida": "17:45",
        "notas": "Entrega urgente a cliente X"
    }
    """
    data = request.get_json()
    
    # Validaciones
    requeridos = ['conductor_id', 'fecha', 'hora_entrada', 'hora_salida']
    for campo in requeridos:
        if not data.get(campo):
            return jsonify({'error': f'Campo "{campo}" requerido'}), 400
    
    # Validar conductor existe
    conductor = Conductor.query.get(data['conductor_id'])
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    
    # Validar no existe registro para ese día
    fecha_obj = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
    existente = RegistroHoras.query.filter_by(
        conductor_id=data['conductor_id'],
        fecha=fecha_obj
    ).first()
    
    if existente:
        return jsonify({'error': f'Ya existe registro para {conductor.nombre} en {data["fecha"]}'}), 409
    
    # Calcular horas trabajadas
    total_horas = calcular_horas_trabajadas(data['hora_entrada'], data['hora_salida'])
    
    # Determinar si son horas extra o déficit
    horas_extra = max(0, total_horas - 8)
    horas_deficit = max(0, 8 - total_horas)
    
    # Crear registro
    nuevo_registro = RegistroHoras(
        conductor_id=data['conductor_id'],
        fecha=fecha_obj,
        hora_entrada=data['hora_entrada'],
        hora_salida=data['hora_salida'],
        total_horas=round(total_horas, 2),
        horas_extra=round(horas_extra, 2),
        horas_deficit=round(horas_deficit, 2),
        notas=data.get('notas', '')
    )
    
    db.session.add(nuevo_registro)
    db.session.flush()  # Guardar sin commit
    
    # Actualizar banco de horas y generar alertas
    alertas = actualizar_banco_horas(data['conductor_id'], horas_extra, horas_deficit)
    
    db.session.commit()
    
    return jsonify({
        'mensaje': 'Horas registradas exitosamente',
        'registro': nuevo_registro.to_dict(),
        'alertas': alertas
    }), 201


# ✅ OBTENER REGISTROS POR CONDUCTOR Y RANGO FECHAS
@horas_bp.route('/conductor/<int:conductor_id>', methods=['GET'])
def obtener_horas_conductor(conductor_id):
    """
    GET /api/horas/conductor/1?fecha_inicio=2026-08-01&fecha_fin=2026-08-31
    """
    conductor = Conductor.query.get(conductor_id)
    if not conductor:
        return jsonify({'error': 'Conductor no encontrado'}), 404
    
    # Parámetros de fecha
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    query = RegistroHoras.query.filter_by(conductor_id=conductor_id)
    
    if fecha_inicio:
        fi = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        query = query.filter(RegistroHoras.fecha >= fi)
    
    if fecha_fin:
        ff = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        query = query.filter(RegistroHoras.fecha <= ff)
    
    registros = query.order_by(RegistroHoras.fecha.desc()).all()
    
    # Calcular totales
    total_horas = sum(r.total_horas for r in registros)
    total_extra = sum(r.horas_extra for r in registros)
    total_deficit = sum(r.horas_deficit for r in registros)
    
    return jsonify({
        'conductor': conductor.to_dict(),
        'registros': [r.to_dict() for r in registros],
        'resumen': {
            'total_registros': len(registros),
            'total_horas_trabajadas': round(total_horas, 2),
            'total_horas_extra': round(total_extra, 2),
            'total_horas_deficit': round(total_deficit, 2)
        }
    }), 200


# ✅ OBTENER TODOS LOS REGISTROS (DASHBOARD)
@horas_bp.route('/', methods=['GET'])
def obtener_todos_registros():
    """GET /api/horas?fecha=2026-08-03"""
    fecha = request.args.get('fecha')
    
    query = RegistroHoras.query
    
    if fecha:
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        query = query.filter_by(fecha=fecha_obj)
    
    registros = query.all()
    
    # Agrupar por conductor
    por_conductor = {}
    for reg in registros:
        conductor_nombre = reg.conductor.nombre
        if conductor_nombre not in por_conductor:
            por_conductor[conductor_nombre] = {
                'conductor_id': reg.conductor_id,
                'email': reg.conductor.email,
                'registros': []
            }
        por_conductor[conductor_nombre]['registros'].append(reg.to_dict())
    
    return jsonify({
        'total_registros': len(registros),
        'por_conductor': por_conductor
    }), 200


# ✅ ACTUALIZAR REGISTRO DE HORAS
@horas_bp.route('/<int:registro_id>', methods=['PUT'])
def actualizar_registro(registro_id):
    """
    PUT /api/horas/1
    Body: { "hora_entrada": "08:00", "hora_salida": "17:30", "notas": "..." }
    """
    registro = RegistroHoras.query.get(registro_id)
    
    if not registro:
        return jsonify({'error': 'Registro no encontrado'}), 404
    
    data = request.get_json()
    
    # Guardar valores previos
    horas_extra_prev = registro.horas_extra
    horas_deficit_prev = registro.horas_deficit
    
    # Actualizar
    if 'hora_entrada' in data:
        registro.hora_entrada = data['hora_entrada']
    
    if 'hora_salida' in data:
        registro.hora_salida = data['hora_salida']
    
    if 'notas' in data:
        registro.notas = data['notas']
    
    # Recalcular horas si cambió entrada/salida
    if 'hora_entrada' in data or 'hora_salida' in data:
        total_horas = calcular_horas_trabajadas(registro.hora_entrada, registro.hora_salida)
        registro.total_horas = round(total_horas, 2)
        registro.horas_extra = round(max(0, total_horas - 8), 2)
        registro.horas_deficit = round(max(0, 8 - total_horas), 2)
        
        # Ajustar banco de horas por diferencia
        diferencia_extra = registro.horas_extra - horas_extra_prev
        diferencia_deficit = registro.horas_deficit - horas_deficit_prev
        
        if diferencia_extra != 0 or diferencia_deficit != 0:
            actualizar_banco_horas(registro.conductor_id, diferencia_extra, diferencia_deficit)
    
    db.session.commit()
    
    return jsonify({
        'mensaje': 'Registro actualizado exitosamente',
        'registro': registro.to_dict()
    }), 200


# ✅ ELIMINAR REGISTRO
@horas_bp.route('/<int:registro_id>', methods=['DELETE'])
def eliminar_registro(registro_id):
    """DELETE /api/horas/1"""
    registro = RegistroHoras.query.get(registro_id)
    
    if not registro:
        return jsonify({'error': 'Registro no encontrado'}), 404
    
    # Revertir cambios en banco de horas
    actualizar_banco_horas(
        registro.conductor_id,
        -registro.horas_extra,
        -registro.horas_deficit
    )
    
    db.session.delete(registro)
    db.session.commit()
    
    return jsonify({
        'mensaje': 'Registro eliminado exitosamente'
    }), 200
