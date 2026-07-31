from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Conductor(db.Model):
    """Modelo Conductor"""
    __tablename__ = 'conductores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120))
    activo = db.Column(db.Boolean, default=True)
    fecha_alta = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    registros_horas = db.relationship('RegistroHoras', backref='conductor', lazy=True, cascade='all, delete-orphan')
    banco_horas = db.relationship('BancoHoras', backref='conductor', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'activo': self.activo,
            'fecha_alta': self.fecha_alta.isoformat()
        }


class RegistroHoras(db.Model):
    """Modelo Registro Diario de Horas"""
    __tablename__ = 'registros_horas'
    
    id = db.Column(db.Integer, primary_key=True)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.String(5))  # HH:MM
    hora_salida = db.Column(db.String(5))   # HH:MM
    total_horas = db.Column(db.Float)       # Calculado
    horas_extra = db.Column(db.Float, default=0)
    horas_deficit = db.Column(db.Float, default=0)
    notas = db.Column(db.Text)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conductor_id': self.conductor_id,
            'fecha': self.fecha.isoformat(),
            'hora_entrada': self.hora_entrada,
            'hora_salida': self.hora_salida,
            'total_horas': self.total_horas,
            'horas_extra': self.horas_extra,
            'horas_deficit': self.horas_deficit,
            'notas': self.notas
        }


class BancoHoras(db.Model):
    """Modelo Banco de Horas Compensatorio"""
    __tablename__ = 'banco_horas'
    
    id = db.Column(db.Integer, primary_key=True)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    balance_acumulado = db.Column(db.Float, default=0)  # +/- horas
    horas_extra_acumuladas = db.Column(db.Float, default=0)
    horas_deficit_acumuladas = db.Column(db.Float, default=0)
    descanso_compensatorio_disponible = db.Column(db.Boolean, default=False)
    fecha_descanso_tomado = db.Column(db.Date)
    estado = db.Column(db.String(20), default='Pendiente')  # Pendiente, Compensado, Descansado
    
    def to_dict(self):
        return {
            'id': self.id,
            'conductor_id': self.conductor_id,
            'balance_acumulado': self.balance_acumulado,
            'horas_extra_acumuladas': self.horas_extra_acumuladas,
            'horas_deficit_acumuladas': self.horas_deficit_acumuladas,
            'descanso_compensatorio_disponible': self.descanso_compensatorio_disponible,
            'fecha_descanso_tomado': self.fecha_descanso_tomado.isoformat() if self.fecha_descanso_tomado else None,
            'estado': self.estado
        }


def init_db():
    """Inicializar BD"""
    db.create_all()
