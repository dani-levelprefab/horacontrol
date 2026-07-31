import os

class Config:
    """Configuración de la app"""
    
    # BD SQLite
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Emails alertas (provisional)
    ALERT_EMAILS = [
        'gustavo@levelprefabricados.es',
        'dani@levelprefabricados.es'
    ]
    
    # Límites
    HORAS_JORNADA_BASE = 8
    HORAS_COMPENSACION = 8  # Cuando acumula 8h extra → alerta descanso
    HORAS_DEFICIT = 2        # Cuando falta 2h → alerta compensar
