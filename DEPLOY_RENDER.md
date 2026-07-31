# ☁️ GUÍA DEPLOY EN RENDER (GRATIS)

## 📋 RESUMEN RÁPIDO

```
1. Crear cuenta GitHub (gratis)
2. Subir código a GitHub
3. Conectar GitHub a Render
4. Deploy automático
5. Compartir URL con Gustavo
6. ¡Funciona desde cualquier lado!
```

**Tiempo total:** ~15 minutos
**Costo:** $0 (gratis)
**URL resultante:** `https://horacontrol-dani.onrender.com`

---

## 🚀 PASO 1: CREAR CUENTA GITHUB (2 minutos)

### Si NO tienes GitHub:

1. Entra a: https://github.com
2. Click en "Sign up"
3. Email: (la que uses)
4. Password: (segura)
5. Username: `horacontrol-dani` (o el que quieras)
6. Confirma email
7. ✅ Cuenta lista

### Si YA tienes GitHub:
Ve al Paso 2 directo.

---

## 📦 PASO 2: CREAR REPOSITORIO EN GITHUB (3 minutos)

1. Entra a: https://github.com/new
2. Rellena:
   - **Repository name:** `horacontrol`
   - **Description:** `Gestión de horas y descanso para conductores`
   - **Public** ✅ (importante para Render)
   - **.gitignore:** Python
3. Click en "Create repository"
4. ✅ Repo creado

---

## 💾 PASO 3: SUBIR TU CÓDIGO A GITHUB (5 minutos)

### Opción A: Git por línea de comandos (recomendado)

En PowerShell en la carpeta `horacontrol-backend`:

```powershell
# Inicializar git
git init

# Añadir todos los archivos
git add .

# Crear commit inicial
git commit -m "Initial commit - HoraControl App"

# Agregar el repositorio remoto
git remote add origin https://github.com/TU_USERNAME/horacontrol.git

# Subir a GitHub (cambia main si es master)
git branch -M main
git push -u origin main
```

### Opción B: Interfaz web GitHub (más fácil si no sabes git)

1. En https://github.com/TU_USERNAME/horacontrol
2. Click en "uploading an existing file"
3. Sube todos los archivos:
   - app.py
   - config.py
   - models.py
   - requirements.txt
   - Procfile
   - runtime.txt
   - .gitignore
   - index.html
   - logo.png
   - Carpetas: routes/ y utils/

4. Commit y listo

---

## 🌐 PASO 4: CONECTAR A RENDER (5 minutos)

1. Entra a: https://render.com
2. Click "Sign up"
3. Elige: "GitHub"
4. Autoriza Render a acceder a GitHub
5. ✅ Cuenta lista

---

## 🚀 PASO 5: CREAR NUEVA APP EN RENDER

1. En dashboard Render, click en "New +" en la esquina
2. Elige: "Web Service"
3. Conecta repositorio:
   - Click en "Connect account" (GitHub)
   - Busca: `horacontrol`
   - Click "Connect"
4. Rellena:
   - **Name:** `horacontrol` (o `horacontrol-dani`)
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python app.py`
   - **Instance Type:** Free
5. Click "Deploy"
6. ⏳ Espera 2-3 minutos (verás logs)
7. ✅ Deploy completado

---

## 🎉 PASO 6: YA FUNCIONA

Render te dará una URL tipo:
```
https://horacontrol.onrender.com
```

**Esa es tu URL para:**
- ✅ Tú (Dani): Accede desde cualquier lado
- ✅ Gustavo: Accede desde la otra fábrica
- ✅ Cualquiera con el enlace

---

## ⚙️ CONFIGURACIÓN IMPORTANTE

### Puerto

La app usa puerto 5000. En Render, cambia `app.py`:

**Línea final:**
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
```

**Pero espera,** ya está hecho en el `app.py` que proporcioné? No, necesita ajuste. Te lo digo abajo.

### Base de datos SQLite en Render

**Problema:** SQLite en Render es temporal (se borra si se reinicia)

**Solución (fácil):** Usar PostgreSQL gratuito de Render

1. En dashboard Render, "New PostgreSQL Database"
2. Copia URL de conexión
3. En `config.py`, cambia:
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://usuario:password@host/nombre'
```

**MÁS FÁCIL:** Por ahora, SQLite funciona temporalmente. Los datos se guardan mientras Render esté activo.

---

## 📝 ARCHIVOS NECESARIOS EN GITHUB

```
horacontrol/
├── app.py                    ✅
├── config.py                 ✅
├── models.py                 ✅
├── requirements.txt          ✅
├── Procfile                  ✅ (descarga)
├── runtime.txt               ✅ (descarga)
├── .gitignore                ✅ (descarga)
├── index.html                ✅
├── logo.png                  ✅
├── routes/                   ✅
│   ├── __init__.py
│   ├── conductores.py
│   ├── horas.py
│   └── banco_horas.py
└── utils/                    ✅
    ├── __init__.py
    ├── calculos.py
    └── alertas.py
```

---

## 🆘 TROUBLESHOOTING

### Problema: "Build failed"
**Solución:** 
- Ve a Logs en Render
- Lee el error
- Generalmente es que falta algún archivo
- Sube de nuevo a GitHub
- Render redeploy automático

### Problema: "Port already in use"
**Solución:** `app.py` debe tener:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Problema: "Module not found"
**Solución:** 
- Verifica `requirements.txt` tiene todas las librerías
- Ejecuta en Render "Redeploy"

### Problema: La app es lenta
**Solución:**
- Render free se "duerme" 15 min sin uso
- Primer acceso tarda 30 seg
- Después es rápido
- Upgrade a $7/mes si quieres siempre rápido

---

## ✅ CHECKLIST FINAL

- [ ] Cuenta GitHub creada
- [ ] Repositorio creado
- [ ] Código subido a GitHub
- [ ] Cuenta Render creada
- [ ] App conectada en Render
- [ ] Deploy completado
- [ ] URL funciona: `https://horacontrol-xxx.onrender.com`
- [ ] Gustavo accede desde su PC
- [ ] ¡Funciona!

---

## 🎯 RESUMEN

**PARA DANI (tú):**
- Entra a: `https://horacontrol-xxx.onrender.com`
- Ves Dashboard + Historial + Todo

**PARA GUSTAVO (fábrica):**
- Entra a: `https://horacontrol-xxx.onrender.com`
- Registra horas
- Tú ves todo en tiempo real

**SIEMPRE ONLINE:**
- No necesitas PC encendida
- No necesitas permisos de admin
- Acceso desde cualquier lado
- Datos persistentes

---

## 💰 COSTO

- **Render Free:** $0 (se duerme 15 min sin uso)
- **Render Pro:** $7/mes (siempre activo)
- **Recomendación:** Empieza free, upgrade si necesitas

---

**¿LISTO? EMPEZAMOS POR EL PASO 1**

Dime cuando hayas hecho la cuenta GitHub y te guío con lo demás. 🚀
