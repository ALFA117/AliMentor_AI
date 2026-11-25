# AliMentor AI - Frontend Documentation

## 🍽️ Sistema de Análisis Alimentario Inteligente

### Descripción General

AliMentor AI es una aplicación web moderna que utiliza inteligencia artificial para analizar menús y proporcionar recomendaciones alimentarias personalizadas. El frontend está construido con HTML5, CSS3 y JavaScript vanilla, siguiendo principios de diseño moderno y experiencia de usuario optimizada.

## 🎨 Diseño y UX/UI

### Paleta de Colores Gastronómica
- **Verde menta** (#00B894) - Color principal
- **Blanco crema** (#FAFAFA) - Fondo suave
- **Amarillo mostaza** (#FDCB6E) - Acentos cálidos
- **Gris suave** (#DFE6E9) - Elementos neutros
- **Rojo coral** (#FF7675) - Alertas e incompatibilidades

### Tipografía
- **Poppins** - Fuente principal (moderna y redondeada)
- **Nunito Sans** - Fuente secundaria (legible y amigable)
- Pesos: 300, 400, 500, 600, 700

### Características Visuales
- **Animaciones suaves** con CSS transitions
- **Diseño responsive** para todos los dispositivos
- **Íconos de comida** y salud (FontAwesome)
- **Tarjetas glassmorphism** con efectos de blur
- **Gradientes suaves** y sombras dinámicas

## 🏗️ Arquitectura del Frontend

### Estructura de Componentes

```
static/
├── components/
│   ├── login.js              # Autenticación de usuarios
│   ├── navbar.js             # Navegación principal
│   ├── uploadMenu.js         # Carga de menús
│   ├── analysisResult.js     # Resultados de análisis
│   ├── feedbackForm.js       # Formulario de feedback
│   ├── metricsDashboard.js   # Panel de métricas
│   ├── profile.js            # Perfil de usuario
│   ├── userManagement.js     # Gestión de usuarios
│   ├── jsonFieldHandler.js   # Manejo de campos JSON
│   ├── userProfile.js        # Perfil editable
│   ├── dishesListing.js      # Listado de platos
│   ├── dishDetail.js         # Detalle de plato
│   ├── feedbackPanel.js      # Panel de feedback
│   ├── aiHistoryView.js      # Historial de IA
│   ├── dataTable.js          # Tablas de datos
│   ├── validationHandler.js  # Validaciones
│   └── securityManager.js    # Seguridad y sesiones
├── styles.css                # Estilos principales
└── main.js                   # Inicialización
```

## 🔗 Mapeo de Endpoints API

### Autenticación y Usuarios

#### POST /login
**Descripción**: Autenticación de usuarios
**Tabla**: usuarios
**Campos**:
- `nombre` (string): Nombre del usuario
- `email` (string, opcional): Email del usuario
- `password` (string, opcional): Contraseña

**Respuesta**:
```json
{
  "success": true,
  "user": {
    "id_usuario": 1,
    "nombre": "Ana López",
    "edad": 28,
    "genero": "Femenino",
    "restricciones": ["vegetariano"],
    "alergias": ["lactosa"],
    "enfermedades": ["diabetes"]
  },
  "token": "abc123..."
}
```

#### GET /usuarios/<id_usuario>
**Descripción**: Obtener usuario por ID
**Tabla**: usuarios
**Campos devueltos**:
- `id_usuario` (int): ID único del usuario
- `nombre` (string): Nombre completo
- `edad` (int): Edad del usuario
- `genero` (string): Género
- `restricciones` (JSON array): Restricciones alimentarias
- `alergias` (JSON array): Alergias conocidas
- `enfermedades` (JSON array): Enfermedades crónicas
- `fecha_creacion` (datetime): Fecha de registro

#### PUT /usuarios/<id_usuario>
**Descripción**: Actualizar usuario
**Tabla**: usuarios
**Campos actualizables**:
- `edad` (int): Nueva edad
- `genero` (string): Género
- `restricciones` (JSON array): Restricciones alimentarias
- `alergias` (JSON array): Alergias
- `enfermedades` (JSON array): Enfermedades

### Platos

#### GET /platos
**Descripción**: Listar platos con filtros
**Tabla**: platos
**Parámetros de consulta**:
- `categoria` (string): Filtrar por categoría
- `fuente` (string): Filtrar por fuente
- `alergeno` (string): Filtrar por alérgeno

**Campos devueltos**:
- `id_plato` (int): ID único del plato
- `nombre` (string): Nombre del plato
- `descripcion` (string): Descripción detallada
- `categoria` (string): Categoría del plato
- `ingredientes` (JSON array): Lista de ingredientes
- `alergenos_detectados` (JSON array): Alérgenos identificados
- `precio` (float): Precio del plato
- `fuente` (string): Fuente del plato
- `fecha_registro` (datetime): Fecha de registro

#### GET /platos/<id_plato>
**Descripción**: Obtener plato por ID
**Tabla**: platos
**Campos**: Mismos que GET /platos

#### POST /platos
**Descripción**: Crear nuevo plato
**Tabla**: platos
**Campos requeridos**:
- `nombre` (string): Nombre del plato
- `descripcion` (string): Descripción
- `categoria` (string): Categoría
- `ingredientes` (JSON array): Ingredientes
- `alergenos_detectados` (JSON array): Alérgenos
- `precio` (float): Precio
- `fuente` (string): Fuente

### Feedback

#### GET /feedback
**Descripción**: Obtener feedbacks con filtros
**Tabla**: feedback
**Parámetros de consulta**:
- `usuario_id` (int): Filtrar por usuario
- `plato_id` (int): Filtrar por plato

**Campos devueltos**:
- `id_feedback` (int): ID único del feedback
- `usuario_id` (int): ID del usuario
- `plato_id` (int): ID del plato
- `comentario` (string): Comentario del usuario
- `calificacion` (int): Calificación (1-5)
- `tipo_feedback` (string): Tipo de feedback
- `fecha` (datetime): Fecha del feedback

#### POST /feedback
**Descripción**: Crear nuevo feedback
**Tabla**: feedback
**Campos requeridos**:
- `usuario_id` (int): ID del usuario
- `plato_id` (int): ID del plato
- `comentario` (string): Comentario
- `calificacion` (int): Calificación (1-5)
- `tipo_feedback` (string): Tipo de feedback

### Acciones IA

#### GET /acciones_ia
**Descripción**: Obtener historial de acciones IA
**Tabla**: acciones_IA
**Parámetros de consulta**:
- `usuario_id` (int): Filtrar por usuario
- `plato_id` (int): Filtrar por plato

**Campos devueltos**:
- `id_accion` (int): ID único de la acción
- `usuario_id` (int): ID del usuario
- `plato_id` (int): ID del plato
- `tipo_accion` (string): Tipo de acción
- `entrada_prompt` (string): Prompt de entrada
- `salida_resumen` (string): Resumen de salida
- `exito` (boolean): Si la acción fue exitosa
- `fecha` (datetime): Fecha de la acción

#### POST /acciones_ia
**Descripción**: Registrar nueva acción IA
**Tabla**: acciones_IA
**Campos requeridos**:
- `usuario_id` (int): ID del usuario
- `plato_id` (int): ID del plato
- `tipo_accion` (string): Tipo de acción
- `entrada_prompt` (string): Prompt de entrada
- `salida_resumen` (string): Resumen de salida
- `exito` (boolean): Si fue exitosa

### Mejoras IA

#### GET /mejora_ia
**Descripción**: Obtener mejoras IA
**Tabla**: mejora_ia
**Parámetros de consulta**:
- `accion_id` (int): Filtrar por acción

**Campos devueltos**:
- `id_mejora` (int): ID único de la mejora
- `id_accion` (int): ID de la acción relacionada
- `ajuste_prompt` (string): Ajuste del prompt
- `observacion` (string): Observación
- `confianza` (float): Nivel de confianza (0-1)
- `fecha` (datetime): Fecha de la mejora

#### POST /mejora_ia
**Descripción**: Crear nueva mejora IA
**Tabla**: mejora_ia
**Campos requeridos**:
- `id_accion` (int): ID de la acción
- `ajuste_prompt` (string): Ajuste del prompt
- `observacion` (string): Observación
- `confianza` (float): Nivel de confianza

## 🔧 Configuración

### API Base URL
```javascript
// En main.js
window.API_BASE_URL = "http://127.0.0.1:5000";

// Para producción (Railway)
window.API_BASE_URL = "https://tu-app.railway.app";
```

### Variables de Entorno
```javascript
// Configuración de sesión
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutos

// Configuración de validación
const VALIDATION_RULES = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^[\+]?[1-9][\d]{0,15}$/,
  password: {
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true
  }
};
```

## 🎯 Funcionalidades Implementadas

### 1. Autenticación y Sesiones
- ✅ Login/Logout con tokens
- ✅ Gestión de sesiones persistentes
- ✅ Timeout automático de sesión
- ✅ Protección de rutas
- ✅ Manejo de permisos

### 2. Gestión de Usuarios
- ✅ Perfil de usuario editable
- ✅ Campos JSON como chips/pills
- ✅ Validaciones en tiempo real
- ✅ Actualización de datos

### 3. Catálogo de Platos
- ✅ Listado con filtros y paginación
- ✅ Vista de detalle de plato
- ✅ Búsqueda en tiempo real
- ✅ Filtros por categoría, fuente y alérgenos

### 4. Sistema de Feedback
- ✅ Modal de feedback con estrellas
- ✅ Tipos de feedback (positivo, negativo, corrección)
- ✅ Validaciones de calificación
- ✅ Animaciones de éxito

### 5. Historial de IA
- ✅ Vista de acciones IA
- ✅ Filtros por tipo y usuario
- ✅ Modal de mejoras IA
- ✅ Paginación y búsqueda

### 6. Tablas de Datos
- ✅ Componente reutilizable
- ✅ Búsqueda y ordenamiento
- ✅ Paginación
- ✅ Acciones personalizables
- ✅ Exportación a CSV

### 7. Validaciones y Errores
- ✅ Validaciones en tiempo real
- ✅ Notificaciones toast
- ✅ Manejo de errores de API
- ✅ Sanitización de entrada

### 8. Seguridad
- ✅ Tokens de autenticación
- ✅ Headers de autorización
- ✅ Sanitización XSS
- ✅ Timeout de sesión

## 📱 Responsive Design

### Breakpoints
- **Desktop**: > 768px
- **Tablet**: 768px
- **Mobile**: < 480px

### Características Responsive
- ✅ Grid adaptativo
- ✅ Navegación móvil
- ✅ Modales responsive
- ✅ Tablas con scroll horizontal
- ✅ Botones touch-friendly

## 🎨 Animaciones y Transiciones

### Tipos de Animaciones
- **Entrada**: slideUp, fadeIn
- **Hover**: transform, shadow
- **Loading**: pulse, spin
- **Modal**: slideUp, fadeIn
- **Notificaciones**: slideIn, bounce

### CSS Transitions
```css
--transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
--transition-fast: all 0.15s ease-out;
--transition-slow: all 0.5s ease-out;
```

## 🔍 Campos JSON y Chips

### Tipos de Chips
- **Ingredientes**: Verde (success)
- **Alérgenos**: Amarillo (warning)
- **Restricciones**: Azul (info)
- **Enfermedades**: Rojo (danger)

### Funcionalidades
- ✅ Edición inline
- ✅ Validación de longitud
- ✅ Animaciones de entrada/salida
- ✅ Contador de elementos
- ✅ Responsive design

## 🚀 Instalación y Uso

### Requisitos
- Navegador moderno (Chrome, Firefox, Safari, Edge)
- JavaScript habilitado
- Conexión a internet para fuentes y íconos

### Instalación
1. Clonar el repositorio
2. Configurar `API_BASE_URL` en `main.js`
3. Abrir `index.html` en el navegador
4. Iniciar el servidor backend

### Desarrollo
```bash
# Instalar dependencias (si es necesario)
npm install

# Ejecutar servidor de desarrollo
python app.py

# Abrir en navegador
http://127.0.0.1:5000
```

## 🧪 Pruebas

### Datos de Ejemplo
```javascript
// Usuario de prueba
{
  "nombre": "Ana López",
  "edad": 28,
  "genero": "Femenino",
  "restricciones": ["vegetariano"],
  "alergias": ["lactosa"],
  "enfermedades": ["diabetes"]
}

// Plato de prueba
{
  "nombre": "Enchiladas Suizas",
  "descripcion": "Tortillas rellenas de pollo con salsa verde",
  "categoria": "Mexicana",
  "ingredientes": ["tortilla", "pollo", "salsa verde", "queso"],
  "alergenos_detectados": ["gluten", "lactosa"],
  "precio": 15.99,
  "fuente": "Restaurante Mexicano"
}
```

## 📊 Métricas y Rendimiento

### Optimizaciones
- ✅ Lazy loading de componentes
- ✅ Debounce en búsquedas
- ✅ Caché de sesión
- ✅ Compresión de imágenes
- ✅ Minificación de CSS/JS

### Monitoreo
- ✅ Console logging
- ✅ Error tracking
- ✅ Performance metrics
- ✅ User analytics

## 🔮 Próximas Mejoras

### Funcionalidades Planificadas
- [ ] Gráficos con Chart.js
- [ ] Comparación Run 1 vs Run 2
- [ ] Modo oscuro
- [ ] PWA (Progressive Web App)
- [ ] Notificaciones push
- [ ] Exportación de reportes

### Mejoras Técnicas
- [ ] Service Workers
- [ ] IndexedDB para caché
- [ ] WebSocket para tiempo real
- [ ] Internacionalización (i18n)
- [ ] Testing automatizado

## 📞 Soporte

### Contacto
- **Email**: soporte@alimentor-ai.com
- **Documentación**: [docs.alimentor-ai.com](https://docs.alimentor-ai.com)
- **Issues**: [GitHub Issues](https://github.com/alimentor-ai/issues)

### Licencia
MIT License - Ver archivo LICENSE para más detalles.

---

**AliMentor AI** - Transformando la nutrición con inteligencia artificial 🍽️✨