from datetime import datetime, time

def calcular_horas_trabajadas(hora_entrada, hora_salida):
    """
    Calcula las horas trabajadas entre dos horarios
    
    Args:
        hora_entrada: String en formato HH:MM
        hora_salida: String en formato HH:MM
    
    Returns:
        Float con las horas trabajadas
    """
    try:
        entrada = datetime.strptime(hora_entrada, '%H:%M')
        salida = datetime.strptime(hora_salida, '%H:%M')
        
        # Si la salida es menor que la entrada, asumimos que es del día siguiente
        if salida < entrada:
            salida = salida.replace(day=salida.day + 1)
        
        diferencia = salida - entrada
        horas = diferencia.total_seconds() / 3600
        
        return round(horas, 2)
    except Exception as e:
        print(f"Error calculando horas: {e}")
        return 0

def calcular_balance_acumulado(registros):
    """
    Calcula el balance acumulado (horas extra - horas déficit)
    
    Args:
        registros: Lista de RegistroHoras
    
    Returns:
        Float con el balance acumulado
    """
    if not registros:
        return 0
    
    balance = 0
    for registro in registros:
        # Balance = horas trabajadas - 8 horas base
        balance += (registro.total_horas - 8)
    
    return round(balance, 2)

def obtener_estado_balance(balance):
    """
    Retorna un estado textual basado en el balance
    
    Args:
        balance: Float con el balance
    
    Returns:
        String con el estado
    """
    if balance >= 8:
        return f"🎯 Disponible {balance:.1f}h descanso"
    elif balance <= -2:
        return f"⏳ Pendiente trabajar {abs(balance):.1f}h"
    else:
        return f"✅ Balance: {balance:+.1f}h"
