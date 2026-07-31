from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def init_db(app):
    """Inicializar base de datos"""
    db.init_app(app)
    with app.app_context():
        db.create_all()

class Conductor(db.Model):
    """Modelo para Conductores"""
    __tablename__ = 'conductores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    registros = db.relationship('RegistroHoras', backref='conductor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Conductor {self.nombre}>'

class RegistroHoras(db.Model):
    """Modelo para Registros de Horas Diarias"""
    __tablename__ = 'registros_horas'
    
    id = db.Column(db.Integer, primary_key=True)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_entrada = db.Column(db.String(5), nullable=False)  # HH:MM
    hora_salida = db.Column(db.String(5), nullable=False)   # HH:MM
    total_horas = db.Column(db.Float, nullable=False)
    notas = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RegistroHoras {self.conductor_id} - {self.fecha}>'

class BancoHoras(db.Model):
    """Modelo para Banco de Horas Compensatorio"""
    __tablename__ = 'banco_horas'
    
    id = db.Column(db.Integer, primary_key=True)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    balance_acumulado = db.Column(db.Float, default=0)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BancoHoras {self.conductor_id} - {self.balance_acumulado}>'
