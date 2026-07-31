# utils/alertas.py

from models import db, BancoHoras, Conductor
from datetime import datetime
import json

def generar_alertas(conductor_id, balance_acumulado):
    """
    Genera alertas basadas en el balance de horas.
    
    Args:
        conductor_id (int): ID del conductor
        balance_acumulado (float): Balance neto de horas
    
    Returns:
        list: Lista de alertas generadas
    """
    alertas = []
    conductor = Conductor.query.get(conductor_id)
    
    if not conductor:
        return alertas
    
    # Alerta 1: Descanso compensatorio disponible (+8h)
    if balance_acumulado >= 8:
        alertas.append({
            'tipo': 'DESCANSO_DISPONIBLE',
            'conductor_id': conductor_id,
            'conductor_nombre': conductor.nombre,
            'email': conductor.email,
            'mensaje': f'✅ ALERTA: {conductor.nombre} ha acumulado {balance_acumulado}h de descanso compensatorio. Planificar descanso.',
            'severidad': 'ALTA',
            'accion': 'Registrar descanso en POST /api/banco-horas/{id}/descanso'
        })
    
    # Alerta 2: Déficit de horas pendientes de compensar (-2h)
    if balance_acumulado <= -2:
        alertas.append({
            'tipo': 'DEFICIT_COMPENSAR',
            'conductor_id': conductor_id,
            'conductor_nombre': conductor.nombre,
            'email': conductor.email,
            'mensaje': f'⚠️ ALERTA: {conductor.nombre} tiene {abs(balance_acumulado)}h de déficit. Necesita compensar próximos días.',
            'severidad': 'MEDIA',
            'accion': 'Asignar horas extra próximos días'
        })
    
    # Log de alertas
    registrar_alerta_log(conductor_id, alertas)
    
    return alertas


def actualizar_banco_horas(conductor_id, horas_extra_nueva, horas_deficit_nueva):
    """
    Actualiza el banco de horas del conductor y genera alertas.
    
    Args:
        conductor_id (int): ID del conductor
        horas_extra_nueva (float): Horas extra del registro nuevo
        horas_deficit_nueva (float): Horas déficit del registro nuevo
    
    Returns:
        list: Lista de alertas generadas
    """
    banco = BancoHoras.query.filter_by(conductor_id=conductor_id).first()
    
    # Si no existe banco, crear uno nuevo
    if not banco:
        banco = BancoHoras(
            conductor_id=conductor_id,
            balance_acumulado=0,
            horas_extra_acumuladas=0,
            horas_deficit_acumuladas=0,
            estado='Pendiente'
        )
        db.session.add(banco)
        db.session.flush()
    
    # Actualizar acumulados
    banco.horas_extra_acumuladas += horas_extra_nueva
    banco.horas_deficit_acumuladas += horas_deficit_nueva
    
    # Calcular balance neto
    balance_neto = banco.horas_extra_acumuladas - banco.horas_deficit_acumuladas
    banco.balance_acumulado = round(balance_neto, 2)
    
    # Actualizar fecha última modificación
    banco.fecha_registro = datetime.utcnow()
    
    # Generar alertas
    alertas = generar_alertas(conductor_id, banco.balance_acumulado)
    
    db.session.add(banco)
    
    return alertas


def registrar_alerta_log(conductor_id, alertas):
    """
    Registra alertas en archivo log para auditoría.
    
    Args:
        conductor_id (int): ID del conductor
        alertas (list): Lista de alertas
    """
    if not alertas:
        return
    
    try:
        with open('logs/alertas.log', 'a', encoding='utf-8') as f:
            for alerta in alertas:
                log_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'conductor_id': conductor_id,
                    'tipo': alerta['tipo'],
                    'mensaje': alerta['mensaje'],
                    'severidad': alerta['severidad']
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f'Error al registrar alerta en log: {str(e)}')


def enviar_notificacion_email(alerta, emails):
    """
    Envía notificación por email (stub para futuro).
    
    Args:
        alerta (dict): Datos de la alerta
        emails (list): Lista de emails destinatarios
    """
    # TODO: Implementar con SMTP
    print(f'📧 Email enviado a {emails}: {alerta["mensaje"]}')
    pass


def obtener_alertas_activas():
    """
    Obtiene todas las alertas activas del sistema.
    
    Returns:
        dict: Alertas agrupadas por tipo
    """
    conductores = Conductor.query.filter_by(activo=True).all()
    
    alertas_por_tipo = {
        'DESCANSO_DISPONIBLE': [],
        'DEFICIT_COMPENSAR': []
    }
    
    for conductor in conductores:
        banco = BancoHoras.query.filter_by(conductor_id=conductor.id).first()
        
        if not banco:
            continue
        
        # Verificar descanso disponible
        if banco.balance_acumulado >= 8 and not banco.descanso_compensatorio_disponible:
            alertas_por_tipo['DESCANSO_DISPONIBLE'].append({
                'conductor_id': conductor.id,
                'conductor_nombre': conductor.nombre,
                'balance': banco.balance_acumulado
            })
        
        # Verificar déficit
        if banco.balance_acumulado <= -2:
            alertas_por_tipo['DEFICIT_COMPENSAR'].append({
                'conductor_id': conductor.id,
                'conductor_nombre': conductor.nombre,
                'balance': banco.balance_acumulado
            })
    
    return alertas_por_tipo
