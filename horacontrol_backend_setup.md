# 🚀 HoraControl Backend - Setup Completo

## ESTRUCTURA DEL PROYECTO

```
horacontrol-backend/
├── app.py                 # App principal Flask
├── config.py              # Configuración
├── requirements.txt       # Dependencias
├── models.py              # Modelos SQLAlchemy
├── routes/
│   ├── __init__.py
│   ├── conductores.py     # CRUD Conductores
│   ├── horas.py           # CRUD Registros de Horas
│   ├── banco_horas.py     # Lógica Banco de Horas + Alertas
├── utils/
│   ├── __init__.py
│   ├── calculos.py        # Funciones de cálculo
│   ├── alertas.py         # Sistema de alertas
├── database.db            # BD SQLite (se crea automático)
└── logs/
    └── alertas.log        # Log de alertas
```

---

## PASO 1: INSTALAR DEPENDENCIAS

```bash
pip install flask flask-sqlalchemy python-dateutil flask-cors
```

**requirements.txt:**
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
python-dateutil==2.8.2
Flask-CORS==4.0.0
```

---

## PASO 2: CREAR app.py

```python
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db, init_db
from routes import conductores_bp, horas_bp, banco_horas_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Inicializar BD
db.init_app(app)

# Registrar blueprints
app.register_blueprint(conductores_bp)
app.register_blueprint(horas_bp)
app.register_blueprint(banco_horas_bp)

# Crear tablas si no existen
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

---

## PASO 3: CREAR config.py

```python
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
```

---

## PASO 4: CREAR models.py

```python
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
```

---

**Próximo paso: Crear las rutas CRUD. ¿Voy?**
