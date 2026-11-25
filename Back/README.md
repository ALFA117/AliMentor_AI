# AliMentor AI - Analizador Inteligente de Menús

## 🧩 Descripción General

AliMentor AI es un sistema backend inteligente que utiliza OpenAI GPT-4o-mini para analizar menús de restaurantes, detectar ingredientes, identificar alérgenos y proporcionar recomendaciones personalizadas basadas en las restricciones dietéticas de los usuarios. El sistema incluye capacidades de auto-mejora que aprenden del feedback de los usuarios para optimizar continuamente su precisión.

## ✨ Características Principales

- **Análisis Inteligente de Menús**: Procesa texto de menús y extrae información detallada
- **Detección de Alérgenos**: Identifica automáticamente alérgenos comunes y restricciones dietéticas
- **Recomendaciones Personalizadas**: Sugiere platos seguros basándose en el perfil del usuario
- **Sistema de Feedback**: Permite a los usuarios corregir y mejorar el análisis
- **Auto-mejora de IA**: Aprende del feedback para mejorar continuamente su precisión
- **Métricas en Tiempo Real**: Monitorea el rendimiento y la satisfacción del sistema
- **API REST Completa**: Endpoints documentados para integración con frontend

## 🏗️ Arquitectura del Sistema

```
alimentor_ai/
├── app.py                 # Aplicación principal Flask
├── config.py             # Configuración del sistema
├── requirements.txt      # Dependencias Python
│
├── routes/               # Endpoints REST
│   ├── analyze_routes.py    # Análisis de menús
│   ├── recommend_routes.py  # Recomendaciones
│   ├── feedback_routes.py   # Gestión de feedback
│   ├── improve_routes.py    # Mejoras de IA
│   └── metrics_routes.py    # Métricas del sistema
│
├── services/             # Lógica de negocio
│   ├── db_service.py        # Operaciones de base de datos
│   ├── ai_service.py        # Integración con OpenAI
│   ├── feedback_analyzer.py # Análisis de feedback
│   └── metrics_service.py   # Cálculo de métricas
│
├── models/               # Modelos SQLAlchemy
│   ├── usuarios.py          # Modelo de usuarios
│   ├── platos.py            # Modelo de platos
│   ├── feedback.py          # Modelo de feedback
│   ├── acciones_ia.py       # Modelo de acciones de IA
│   └── mejora_ia.py         # Modelo de mejoras
│
├── utils/                # Utilidades
│   ├── prompt_templates.py  # Templates de prompts
│   └── data_cleaner.py      # Limpieza de datos
│
└── tests/                # Tests y datos de prueba
    ├── test_run1.json       # Test inicial
    ├── test_run2.json       # Test con mejoras
    └── test_endpoints.py    # Tests unitarios
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- MySQL 5.7+
- Cuenta de OpenAI con API key

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd alimentor_ai
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos MySQL

```sql
CREATE DATABASE alimentor_ai;
CREATE USER 'alimentor_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON alimentor_ai.* TO 'alimentor_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configurar Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:

```env
# Configuración de base de datos MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=alimentor_user
DB_PASSWORD=tu_password_mysql
DB_NAME=alimentor_ai

# Configuración de OpenAI
OPENAI_API_KEY=tu_api_key_de_openai

# Configuración de Flask
SECRET_KEY=tu_secret_key_super_segura
DEBUG=True

# Configuración de CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Configuración de métricas
MIN_FEEDBACK_FOR_IMPROVEMENT=5
CONFIDENCE_THRESHOLD=0.7
```

### 6. Ejecutar la Aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📚 Uso de la API

### Endpoints Principales

#### 1. Análisis de Menús

**POST** `/analyze`

Analiza un menú de texto y extrae información detallada.

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "menu_text": "MENÚ DEL DÍA\n\n1. Ensalada César - Lechuga, crutones, parmesano - $8.50\n2. Pollo a la parrilla - Con arroz y vegetales - $15.00",
    "user_id": 1
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "analisis": {
      "platos_detectados": [
        {
          "nombre": "Ensalada César",
          "categoria": "entrada",
          "ingredientes": ["lechuga", "crutones", "parmesano"],
          "alergenos_detectados": ["gluten", "lactosa"],
          "precio": 8.50
        }
      ],
      "ingredientes_totales": ["lechuga", "crutones", "parmesano"],
      "alergenos_detectados": ["gluten", "lactosa"],
      "recomendaciones": ["Recomendación nutricional"]
    },
    "platos_guardados": [...],
    "total_platos": 1
  }
}
```

#### 2. Recomendaciones Personalizadas

**GET** `/recommend?user_id=1`

Obtiene recomendaciones personalizadas para un usuario.

```bash
curl "http://localhost:5000/recommend?user_id=1&limit=10"
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "recomendaciones": [
      {
        "nombre": "Pollo a la parrilla",
        "nivel_riesgo": "bajo",
        "recomendacion": "Plato seguro para tu perfil dietético"
      }
    ],
    "usuario": {...},
    "total_encontrados": 5
  }
}
```

#### 3. Gestión de Feedback

**POST** `/feedback`

Envía feedback sobre el análisis de un plato.

```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 1,
    "plato_id": 2,
    "comentario": "El análisis fue muy preciso",
    "calificacion": 5,
    "tipo_feedback": "positivo"
  }'
```

#### 4. Mejora de IA

**POST** `/improve`

Genera mejoras automáticas basadas en el feedback acumulado.

```bash
curl -X POST http://localhost:5000/improve \
  -H "Content-Type: application/json" \
  -d '{
    "force_improvement": false,
    "min_feedback_count": 5
  }'
```

#### 5. Métricas del Sistema

**GET** `/metrics`

Obtiene métricas generales del sistema.

```bash
curl "http://localhost:5000/metrics?period=30&detailed=true"
```

### Endpoints Adicionales

- **GET** `/health` - Health check del sistema
- **GET** `/status` - Estado detallado del sistema
- **GET** `/recommend/safe?user_id=1` - Platos seguros para el usuario
- **GET** `/recommend/by-category?user_id=1` - Recomendaciones por categoría
- **GET** `/feedback/user/1` - Feedback de un usuario específico
- **GET** `/metrics/dashboard` - Datos para dashboard en tiempo real

## 🧪 Testing

### Ejecutar Tests Unitarios

```bash
pytest tests/test_endpoints.py -v
```

### Tests de Integración

Los archivos `test_run1.json` y `test_run2.json` contienen tests de integración que simulan:

1. **Run 1**: Análisis inicial sin mejoras aplicadas
2. **Run 2**: Análisis con mejoras aplicadas basadas en feedback

### Ejecutar Tests de Integración

```bash
# Simular Run 1
python -c "
import requests
import json

with open('tests/test_run1.json') as f:
    test_data = json.load(f)

# Ejecutar análisis inicial
response = requests.post('http://localhost:5000/analyze', 
                        json=test_data['test_data'])
print('Run 1 - Análisis inicial:', response.json())
"

# Simular Run 2 (después de acumular feedback)
python -c "
import requests
import json

with open('tests/test_run2.json') as f:
    test_data = json.load(f)

# Ejecutar análisis mejorado
response = requests.post('http://localhost:5000/analyze', 
                        json=test_data['test_data'])
print('Run 2 - Análisis mejorado:', response.json())
"
```

## 📊 Monitoreo y Métricas

### Métricas Disponibles

1. **Precisión de IA**: Porcentaje de análisis correctos
2. **Satisfacción del Usuario**: Calificación promedio del feedback
3. **Tasa de Mejora**: Frecuencia de mejoras aplicadas
4. **Rendimiento del Sistema**: Tiempo de respuesta y disponibilidad

### Dashboard en Tiempo Real

Accede a `/metrics/dashboard` para obtener datos actualizados para visualización:

```bash
curl "http://localhost:5000/metrics/dashboard"
```

### Alertas Automáticas

El sistema genera alertas automáticas cuando:
- La precisión de IA cae por debajo del 70%
- La satisfacción del usuario es menor a 3.0
- La tasa de mejora es menor al 50%

## 🔧 Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DB_HOST` | Host de MySQL | localhost |
| `DB_PORT` | Puerto de MySQL | 3306 |
| `DB_USER` | Usuario de MySQL | root |
| `DB_PASSWORD` | Contraseña de MySQL | (vacío) |
| `DB_NAME` | Nombre de la base de datos | alimentor_ai |
| `OPENAI_API_KEY` | Clave API de OpenAI | (requerido) |
| `OPENAI_MODEL` | Modelo de OpenAI | gpt-4o-mini |
| `SECRET_KEY` | Clave secreta de Flask | (generada) |
| `DEBUG` | Modo debug | False |
| `MIN_FEEDBACK_FOR_IMPROVEMENT` | Mínimo feedback para mejora | 5 |
| `CONFIDENCE_THRESHOLD` | Umbral de confianza | 0.7 |

### Configuración de Producción

Para producción, asegúrate de:

1. Configurar `DEBUG=False`
2. Usar una base de datos MySQL robusta
3. Configurar HTTPS
4. Implementar rate limiting
5. Configurar logging apropiado
6. Usar un servidor WSGI como Gunicorn

```bash
# Ejemplo con Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Error de conexión a MySQL**
   - Verificar que MySQL esté ejecutándose
   - Confirmar credenciales en `.env`
   - Verificar que la base de datos existe

2. **Error de OpenAI API**
   - Verificar que `OPENAI_API_KEY` esté configurada
   - Confirmar que la API key es válida
   - Verificar límites de uso de la API

3. **Error de importación de módulos**
   - Verificar que todas las dependencias estén instaladas
   - Confirmar que el entorno virtual esté activado

4. **Error de permisos de base de datos**
   - Verificar que el usuario tenga permisos adecuados
   - Confirmar que las tablas se crearon correctamente

### Logs del Sistema

Los logs se guardan en `alimentor_ai.log` y incluyen:
- Información de requests y responses
- Errores de la aplicación
- Métricas de rendimiento
- Actividad de la base de datos

### Health Check

Usa el endpoint `/health` para verificar el estado del sistema:

```bash
curl http://localhost:5000/health
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:

- Crear un issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar la documentación de la API

## 🔮 Roadmap

### Próximas Características

- [ ] Análisis de imágenes de menús (OCR)
- [ ] Integración con más proveedores de IA
- [ ] API de webhooks para notificaciones
- [ ] Cache inteligente para mejorar rendimiento
- [ ] Análisis de sentimientos en feedback
- [ ] Integración con sistemas de POS
- [ ] App móvil nativa
- [ ] Dashboard web administrativo

### Mejoras Planificadas

- [ ] Optimización de prompts dinámicos
- [ ] Machine learning local para mejoras
- [ ] Análisis predictivo de tendencias
- [ ] Integración con bases de datos nutricionales
- [ ] Soporte para múltiples idiomas
- [ ] Análisis de costos y precios de mercado

---

**AliMentor AI** - Transformando la experiencia culinaria con inteligencia artificial 🍽️🤖
