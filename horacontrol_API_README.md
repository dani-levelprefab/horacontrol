# 🚀 HoraControl Backend - API Completa

## 📦 INSTALACIÓN RÁPIDA

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Crear estructura de carpetas
```
horacontrol-backend/
├── app.py
├── config.py
├── models.py
├── requirements.txt
├── routes/
│   ├── __init__.py
│   ├── conductores.py
│   ├── horas.py
│   └── banco_horas.py
├── utils/
│   ├── __init__.py
│   ├── calculos.py
│   └── alertas.py
└── logs/
    └── alertas.log
```

### 3. Ejecutar servidor
```bash
python app.py
```

**Servidor levantado en:** `http://localhost:5000`

---

## 📚 ENDPOINTS API

### 🧑 **CONDUCTORES** (`/api/conductores`)

#### 1️⃣ Crear conductor
```
POST /api/conductores
Content-Type: application/json

{
  "nombre": "Juan Pérez",
  "email": "juan@levelprefabricados.es"
}

Respuesta 201:
{
  "mensaje": "Conductor creado exitosamente",
  "conductor": {
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@levelprefabricados.es",
    "activo": true,
    "fecha_alta": "2026-08-03T10:30:00"
  }
}
```

#### 2️⃣ Obtener todos los conductores
```
GET /api/conductores
GET /api/conductores?activo=true

Respuesta 200:
{
  "total": 3,
  "conductores": [
    {
      "id": 1,
      "nombre": "Juan Pérez",
      "email": "juan@levelprefabricados.es",
      "activo": true,
      "fecha_alta": "2026-08-03T10:30:00"
    },
    ...
  ]
}
```

#### 3️⃣ Obtener conductor por ID
```
GET /api/conductores/1

Respuesta 200:
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@levelprefabricados.es",
  "activo": true,
  "fecha_alta": "2026-08-03T10:30:00"
}
```

#### 4️⃣ Actualizar conductor
```
PUT /api/conductores/1
Content-Type: application/json

{
  "nombre": "Juan Carlos Pérez",
  "email": "juancarlos@levelprefabricados.es",
  "activo": true
}

Respuesta 200:
{
  "mensaje": "Conductor actualizado exitosamente",
  "conductor": { ... }
}
```

#### 5️⃣ Eliminar conductor
```
DELETE /api/conductores/1

Respuesta 200:
{
  "mensaje": "Conductor Juan Pérez eliminado exitosamente"
}
```

---

### ⏰ **REGISTROS DE HORAS** (`/api/horas`)

#### 1️⃣ Registrar horas del día (CORE)
```
POST /api/horas
Content-Type: application/json

{
  "conductor_id": 1,
  "fecha": "2026-08-03",
  "hora_entrada": "07:30",
  "hora_salida": "17:45",
  "notas": "Entrega urgente a cliente X"
}

Respuesta 201:
{
  "mensaje": "Horas registradas exitosamente",
  "registro": {
    "id": 1,
    "conductor_id": 1,
    "fecha": "2026-08-03",
    "hora_entrada": "07:30",
    "hora_salida": "17:45",
    "total_horas": 10.25,
    "horas_extra": 2.25,
    "horas_deficit": 0,
    "notas": "Entrega urgente a cliente X"
  },
  "alertas": [
    {
      "tipo": "DESCANSO_DISPONIBLE",
      "conductor_id": 1,
      "conductor_nombre": "Juan Pérez",
      "email": "juan@levelprefabricados.es",
      "mensaje": "✅ ALERTA: Juan Pérez ha acumulado 2.25h de descanso compensatorio...",
      "severidad": "ALTA"
    }
  ]
}
```

#### 2️⃣ Obtener horas de un conductor
```
GET /api/horas/conductor/1
GET /api/horas/conductor/1?fecha_inicio=2026-08-01&fecha_fin=2026-08-31

Respuesta 200:
{
  "conductor": {
    "id": 1,
    "nombre": "Juan Pérez",
    ...
  },
  "registros": [
    {
      "id": 1,
      "conductor_id": 1,
      "fecha": "2026-08-03",
      "total_horas": 10.25,
      "horas_extra": 2.25,
      ...
    }
  ],
  "resumen": {
    "total_registros": 5,
    "total_horas_trabajadas": 42.5,
    "total_horas_extra": 2.5,
    "total_horas_deficit": 0
  }
}
```

#### 3️⃣ Obtener todos los registros (DASHBOARD)
```
GET /api/horas
GET /api/horas?fecha=2026-08-03

Respuesta 200:
{
  "total_registros": 3,
  "por_conductor": {
    "Juan Pérez": {
      "conductor_id": 1,
      "email": "juan@levelprefabricados.es",
      "registros": [
        {
          "id": 1,
          "fecha": "2026-08-03",
          "total_horas": 10.25,
          ...
        }
      ]
    },
    ...
  }
}
```

#### 4️⃣ Actualizar registro de horas
```
PUT /api/horas/1
Content-Type: application/json

{
  "hora_entrada": "08:00",
  "hora_salida": "17:30",
  "notas": "Ajustado manualmente"
}

Respuesta 200:
{
  "mensaje": "Registro actualizado exitosamente",
  "registro": { ... }
}
```

#### 5️⃣ Eliminar registro
```
DELETE /api/horas/1

Respuesta 200:
{
  "mensaje": "Registro eliminado exitosamente"
}
```

---

### 🏦 **BANCO DE HORAS** (`/api/banco-horas`)

#### 1️⃣ Obtener banco de un conductor
```
GET /api/banco-horas/conductor/1

Respuesta 200:
{
  "conductor": { ... },
  "banco": {
    "id": 1,
    "conductor_id": 1,
    "balance_acumulado": 2.25,
    "horas_extra_acumuladas": 2.25,
    "horas_deficit_acumuladas": 0,
    "descanso_compensatorio_disponible": false,
    "fecha_descanso_tomado": null,
    "estado": "Pendiente"
  }
}
```

#### 2️⃣ Obtener banco de TODOS (SUPERVISIÓN)
```
GET /api/banco-horas

Respuesta 200:
{
  "total_conductores": 3,
  "conductores": [
    {
      "conductor": { "id": 1, "nombre": "Juan Pérez", ... },
      "banco": {
        "balance_acumulado": 2.25,
        "descanso_compensatorio_disponible": false,
        "estado": "Pendiente"
      }
    },
    ...
  ]
}
```

#### 3️⃣ Registrar descanso compensatorio
```
POST /api/banco-horas/1/descanso
Content-Type: application/json

{
  "fecha_descanso": "2026-08-10"
}

Respuesta 200:
{
  "mensaje": "Descanso compensatorio registrado para 2026-08-10",
  "banco": {
    "id": 1,
    "balance_acumulado": -5.75,  # -8 + 2.25 previas
    "descanso_compensatorio_disponible": false,
    "fecha_descanso_tomado": "2026-08-10",
    "estado": "Descansado"
  }
}
```

#### 4️⃣ Obtener ALERTAS activas
```
GET /api/banco-horas/alertas/

Respuesta 200:
{
  "total_alertas": 2,
  "alertas": [
    {
      "tipo": "DESCANSO_DISPONIBLE",
      "conductor_id": 1,
      "conductor_nombre": "Juan Pérez",
      "email": "juan@levelprefabricados.es",
      "mensaje": "Juan Pérez ha acumulado 2.25h - Planificar descanso",
      "severidad": "ALTA",
      "fecha": "2026-08-03T15:30:00"
    },
    {
      "tipo": "DEFICIT_COMPENSAR",
      "conductor_id": 2,
      "conductor_nombre": "María García",
      "email": "maria@levelprefabricados.es",
      "mensaje": "María García tiene 3h pendientes de compensar",
      "severidad": "MEDIA",
      "fecha": "2026-08-03T14:45:00"
    }
  ]
}
```

#### 5️⃣ Dashboard completo (GUSTAVO + DANI)
```
GET /api/banco-horas/dashboard/

Respuesta 200:
{
  "fecha_consulta": "2026-08-03T15:45:00",
  "total_conductores": 3,
  "conductores": [
    {
      "conductor_id": 1,
      "conductor_nombre": "Juan Pérez",
      "email": "juan@levelprefabricados.es",
      "balance_horas": 2.25,
      "estado": "✅ NORMAL",
      "alerta": null,
      "descanso_tomado": null
    },
    {
      "conductor_id": 2,
      "conductor_nombre": "María García",
      "email": "maria@levelprefabricados.es",
      "balance_horas": -3,
      "estado": "⚠️ COMPENSAR HORAS",
      "alerta": "DEFICIT",
      "descanso_tomado": null
    },
    {
      "conductor_id": 3,
      "conductor_nombre": "Pedro López",
      "email": "pedro@levelprefabricados.es",
      "balance_horas": 8.5,
      "estado": "⚠️ DESCANSO DISPONIBLE",
      "alerta": "DESCANSO",
      "descanso_tomado": null
    }
  ]
}
```

#### 6️⃣ Resetear banco (administrativo)
```
POST /api/banco-horas/1/resetear

Respuesta 200:
{
  "mensaje": "Banco de horas de Juan Pérez reseteado",
  "banco": {
    "balance_acumulado": 0,
    "estado": "Pendiente"
  }
}
```

---

## 🔄 **FLUJO OPERATIVO COMPLETO**

### Día 3 de agosto - Mañana
Gustavo recibe partes diarios de los 10-12 conductores.

### Día 3 de agosto - Tarde (16:00)
Gustavo ingresa las horas:

```bash
# 1. Crear conductores (si es primera vez)
curl -X POST http://localhost:5000/api/conductores \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Juan Pérez", "email": "juan@levelprefabricados.es"}'

# 2. Registrar horas Juan
curl -X POST http://localhost:5000/api/horas \
  -H "Content-Type: application/json" \
  -d '{
    "conductor_id": 1,
    "fecha": "2026-08-03",
    "hora_entrada": "07:30",
    "hora_salida": "17:45",
    "notas": "Normal"
  }'

# 3. Ver banco de horas
curl -X GET http://localhost:5000/api/banco-horas/dashboard/
```

### Día 4 de agosto - Mañana
Dani abre el dashboard y ve:
```bash
GET /api/banco-horas/dashboard/
# Ver balance de cada conductor, alertas activas
```

Si Juan tiene +8h, Gustavo registra el descanso:
```bash
POST /api/banco-horas/1/descanso \
  -H "Content-Type: application/json" \
  -d '{"fecha_descanso": "2026-08-09"}'
```

---

## 🧪 TESTING CON CURL

**Script batch para crear datos de prueba:**

```bash
#!/bin/bash

# Crear conductores
curl -X POST http://localhost:5000/api/conductores \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Juan Pérez", "email": "juan@example.com"}'

curl -X POST http://localhost:5000/api/conductores \
  -H "Content-Type: application/json" \
  -d '{"nombre": "María García", "email": "maria@example.com"}'

# Registrar horas - Juan (10h = +2h extra)
curl -X POST http://localhost:5000/api/horas \
  -H "Content-Type: application/json" \
  -d '{
    "conductor_id": 1,
    "fecha": "2026-08-03",
    "hora_entrada": "07:30",
    "hora_salida": "17:30",
    "notas": "Jornada normal"
  }'

# Ver dashboard
curl -X GET http://localhost:5000/api/banco-horas/dashboard/

# Ver alertas
curl -X GET http://localhost:5000/api/banco-horas/alertas/
```

---

## 📋 PRÓXIMAS FEATURES

- [ ] Frontend React/Vue
- [ ] Autenticación JWT
- [ ] Notificaciones por email (SMTP)
- [ ] Exportar Excel/PDF
- [ ] Integración Sage ERP
- [ ] Integración Traccar GPS
- [ ] Deploy en cloud (Render, Railway)

---

**¿Empezamos con el frontend?**
