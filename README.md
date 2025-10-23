# AliMentor AI - Sistema de Análisis Alimentario Inteligente

## 🍽️ Descripción del Proyecto

AliMentor AI es un sistema inteligente de análisis alimentario que utiliza inteligencia artificial para analizar menús y proporcionar recomendaciones personalizadas basadas en las restricciones alimentarias, alergias y preferencias de los usuarios.

## ✨ Características Principales

- **Análisis Inteligente de Menús**: Procesa texto e imágenes de menús para extraer información de platos
- **Recomendaciones Personalizadas**: Sugiere platos seguros basados en el perfil del usuario
- **Sistema de Feedback**: Permite a los usuarios calificar y comentar sobre las recomendaciones
- **Mejora Continua**: El sistema aprende y mejora automáticamente basándose en el feedback
- **Dashboard Interactivo**: Interfaz moderna y responsive para gestión completa
- **API RESTful**: Backend robusto con documentación Swagger

## 🏗️ Arquitectura del Sistema

```
AliMentor_AI/
├── Back/                    # Backend Flask
│   ├── app.py              # Aplicación principal
│   ├── config.py           # Configuración
│   ├── models/             # Modelos de base de datos
│   ├── routes/             # Rutas de la API
│   ├── services/           # Servicios de negocio
│   ├── utils/              # Utilidades
│   └── tests/              # Pruebas unitarias
├── Frond/                  # Frontend
│   ├── app.py              # Servidor de desarrollo
│   ├── templates/          # Plantillas HTML
│   ├── static/             # Archivos estáticos
│   └── data/               # Datos de prueba
└── README.md               # Este archivo
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- Node.js 14+ (para el frontend)
- MySQL 8.0+ (opcional, usa SQLite por defecto)
- Git

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd AliMentor_AI
```

### 2. Configurar el Backend

```bash
cd Back

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env_example.txt .env
# Editar .env con tus configuraciones
```

### 3. Configurar el Frontend

```bash
cd ../Frond

# Instalar dependencias (si es necesario)
npm install  # Solo si hay package.json

# El frontend está listo para usar
```

### 4. Ejecutar la Aplicación

#### Backend
```bash
cd Back
python app.py
```

#### Frontend
```bash
cd Frond
python app.py
```

La aplicación estará disponible en:
- **Frontend**: http://127.0.0.1:5000
- **API Backend**: http://127.0.0.1:5000/api
- **Documentación Swagger**: http://127.0.0.1:5000/api/docs

## 📚 Uso del Sistema

### 1. Inicio de Sesión
- Ingresa tu nombre de usuario
- El sistema creará automáticamente tu perfil si no existe

### 2. Configuración de Perfil
- Completa tu información personal (edad, género)
- Agrega tus restricciones alimentarias
- Especifica alergias conocidas
- Indica enfermedades relacionadas con la alimentación

### 3. Análisis de Menús
- Sube texto de menús o imágenes
- El sistema analizará automáticamente los platos
- Recibe recomendaciones personalizadas

### 4. Sistema de Feedback
- Califica las recomendaciones recibidas
- Proporciona comentarios detallados
- Ayuda al sistema a mejorar continuamente

## 🔧 API Endpoints

### Autenticación
- `POST /login` - Iniciar sesión
- `GET /users` - Listar usuarios
- `POST /users` - Crear usuario

### Gestión de Usuarios
- `GET /usuarios/{id}` - Obtener usuario
- `PUT /usuarios/{id}` - Actualizar usuario

### Gestión de Platos
- `GET /platos` - Listar platos
- `GET /platos/{id}` - Obtener plato
- `POST /platos` - Crear plato

### Análisis y Recomendaciones
- `POST /analyze` - Analizar menú
- `GET /recommend` - Obtener recomendaciones

### Feedback
- `GET /feedback` - Obtener feedbacks
- `POST /feedback` - Crear feedback
- `PUT /feedback/{id}` - Actualizar feedback

### Métricas
- `GET /metrics` - Obtener métricas del sistema

## 🧪 Pruebas

### Ejecutar Pruebas del Backend
```bash
cd Back
python -m pytest tests/
```

### Pruebas de Integración
```bash
# Ejecutar pruebas de endpoints
python tests/test_endpoints.py

# Ejecutar pruebas de perfiles
python tests/test_perfiles.py
```

## 📊 Base de Datos

### Modelos Principales

- **Usuario**: Información del usuario y perfil
- **Plato**: Información de platos y menús
- **Feedback**: Comentarios y calificaciones
- **AccionIA**: Registro de acciones de IA
- **MejoraPrompt**: Mejoras aplicadas al sistema

### Esquema de Base de Datos

El sistema utiliza una arquitectura 4NF (Cuarta Forma Normal) para optimizar el rendimiento y mantener la integridad de los datos.

## 🔐 Seguridad

- Validación de entrada en todos los endpoints
- Sanitización de datos de usuario
- Manejo seguro de errores
- Logging de actividades importantes

## 🚀 Despliegue

### Variables de Entorno Requeridas

```env
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=alimentor_ai

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

# Flask
SECRET_KEY=your_secret_key
DEBUG=False
```

### Despliegue en Producción

1. Configurar base de datos MySQL
2. Establecer variables de entorno
3. Configurar servidor web (Nginx/Apache)
4. Usar WSGI server (Gunicorn/uWSGI)

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Equipo de Desarrollo

- **Desarrollador Principal**: [Tu Nombre]
- **Fecha de Creación**: 2024
- **Versión Actual**: 1.0.0

## 📞 Soporte

Para soporte técnico o preguntas:
- Email: soporte@alimentor-ai.com
- Issues: [GitHub Issues](link-to-issues)
- Documentación: [Wiki del Proyecto](link-to-wiki)

## 🔄 Changelog

### v1.0.0 (2024-01-XX)
- ✅ Sistema de autenticación completo
- ✅ Análisis inteligente de menús
- ✅ Sistema de recomendaciones personalizadas
- ✅ Dashboard interactivo
- ✅ API RESTful con documentación Swagger
- ✅ Sistema de feedback y mejora continua
- ✅ Métricas y analytics
- ✅ Pruebas unitarias y de integración

## 🎯 Roadmap

### Próximas Características
- [ ] Integración con más proveedores de IA
- [ ] Aplicación móvil
- [ ] Sistema de notificaciones push
- [ ] Integración con redes sociales
- [ ] Análisis nutricional avanzado
- [ ] Sistema de recomendaciones colaborativas

---

**AliMentor AI** - Tu asistente inteligente de nutrición 🍽️🤖
