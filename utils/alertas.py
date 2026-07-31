from models import db, RegistroHoras, BancoHoras
from utils.calculos import calcular_balance_acumulado

def actualizar_banco_horas(conductor_id):
    """
    Actualiza el banco de horas para un conductor
    
    Args:
        conductor_id: ID del conductor
    """
    try:
        # Obtener todos los registros del conductor
        registros = RegistroHoras.query.filter_by(conductor_id=conductor_id).all()
        
        # Calcular balance acumulado
        balance = calcular_balance_acumulado(registros)
        
        # Buscar o crear registro en banco_horas
        banco = BancoHoras.query.filter_by(conductor_id=conductor_id).first()
        
        if banco:
            banco.balance_acumulado = balance
        else:
            banco = BancoHoras(conductor_id=conductor_id, balance_acumulado=balance)
            db.session.add(banco)
        
        db.session.commit()
    except Exception as e:
        print(f"Error actualizando banco de horas: {e}")
        db.session.rollback()

def generar_alertas(conductor_id):
    """
    Genera alertas basadas en el balance del conductor
    
    Args:
        conductor_id: ID del conductor
    
    Returns:
        Lista de diccionarios con alertas
    """
    alertas = []
    
    try:
        registros = RegistroHoras.query.filter_by(conductor_id=conductor_id).all()
        balance = calcular_balance_acumulado(registros)
        
        # Alerta: +8h disponible para descanso
        if balance >= 8:
            alertas.append({
                'tipo': 'descanso',
                'mensaje': f'Conductor {conductor_id} tiene {balance:.1f}h disponibles para descanso'
            })
        
        # Alerta: -2h o más de déficit
        if balance <= -2:
            alertas.append({
                'tipo': 'deficit',
                'mensaje': f'Conductor {conductor_id} tiene {abs(balance):.1f}h de déficit'
            })
    except Exception as e:
        print(f"Error generando alertas: {e}")
    
    return alertas
