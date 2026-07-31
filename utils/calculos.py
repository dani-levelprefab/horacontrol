# utils/calculos.py

from datetime import datetime, timedelta

def calcular_horas_trabajadas(hora_entrada, hora_salida):
    """
    Calcula las horas totales trabajadas entre dos horarios.
    
    Args:
        hora_entrada (str): Formato HH:MM (ej: "07:30")
        hora_salida (str): Formato HH:MM (ej: "17:45")
    
    Returns:
        float: Total de horas (ej: 10.25)
    """
    try:
        entrada = datetime.strptime(hora_entrada, '%H:%M').time()
        salida = datetime.strptime(hora_salida, '%H:%M').time()
        
        # Convertir a datetime para cálculo (mismo día para simplificar)
        fecha = datetime(2000, 1, 1)
        dt_entrada = datetime.combine(fecha, entrada)
        dt_salida = datetime.combine(fecha, salida)
        
        # Si salida es antes que entrada, asumir que fue día siguiente
        if dt_salida < dt_entrada:
            dt_salida += timedelta(days=1)
        
        diferencia = dt_salida - dt_entrada
        horas = diferencia.total_seconds() / 3600
        
        return round(horas, 2)
    
    except ValueError as e:
        raise ValueError(f'Formato de hora inválido: {str(e)}')


def calcular_balance_acumulado(horas_extra, horas_deficit):
    """
    Calcula el balance neto de horas.
    
    Args:
        horas_extra (float): Horas trabajadas por encima de 8h
        horas_deficit (float): Horas por debajo de 8h
    
    Returns:
        float: Balance neto (+: crédito, -: deuda)
    """
    return round(horas_extra - horas_deficit, 2)


def verificar_alerta_descanso(balance_acumulado):
    """
    Verifica si se debe activar alerta de descanso compensatorio.
    
    Args:
        balance_acumulado (float): Balance actual del conductor
    
    Returns:
        bool: True si balance >= 8
    """
    return balance_acumulado >= 8


def verificar_alerta_deficit(balance_acumulado):
    """
    Verifica si se debe activar alerta de déficit de horas.
    
    Args:
        balance_acumulado (float): Balance actual del conductor
    
    Returns:
        bool: True si balance <= -2
    """
    return balance_acumulado <= -2


def calcular_dias_laborables(fecha_inicio, fecha_fin):
    """
    Calcula días laborables (lunes-viernes) entre dos fechas.
    
    Args:
        fecha_inicio (date): Fecha inicial
        fecha_fin (date): Fecha final
    
    Returns:
        int: Número de días laborables
    """
    from datetime import timedelta
    
    dias = 0
    fecha_actual = fecha_inicio
    
    while fecha_actual <= fecha_fin:
        # 0=lunes, 4=viernes
        if fecha_actual.weekday() < 5:
            dias += 1
        fecha_actual += timedelta(days=1)
    
    return dias


def calcular_promedio_horas_diarias(total_horas, num_registros):
    """
    Calcula promedio de horas por día trabajado.
    
    Args:
        total_horas (float): Total de horas trabajadas
        num_registros (int): Cantidad de registros
    
    Returns:
        float: Promedio de horas/día
    """
    if num_registros == 0:
        return 0
    return round(total_horas / num_registros, 2)
