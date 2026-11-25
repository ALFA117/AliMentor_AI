"""
AliMentor AI - Backend Flask Principal
Sistema de análisis de compatibilidad alimentaria
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import random
from datetime import datetime
import os
import hashlib
import time

app = Flask(__name__)
CORS(app)  # Habilitar CORS para el frontend

# Variables globales para simular estado
current_run = 1
feedback_data = [
    {
        'id_feedback': 1,
        'usuario_id': 3,  # Baeza
        'plato_id': 4,    # Enchiladas Suizas
        'plato_nombre': 'Enchiladas Suizas',
        'comentario': 'Muy sabroso, pero contiene lactosa',
        'calificacion': 3,
        'tipo_feedback': 'alergia',
        'fecha_creacion': '2024-01-15T10:30:00Z'
    },
    {
        'id_feedback': 2,
        'usuario_id': 3,  # Baeza
        'plato_id': 5,    # Camarones al Ajillo
        'plato_nombre': 'Camarones al Ajillo',
        'comentario': 'Excelente sabor, pero no puedo comerlo por alergia a mariscos',
        'calificacion': 2,
        'tipo_feedback': 'alergia',
        'fecha_creacion': '2024-01-16T14:20:00Z'
    }
]

# Base de datos de usuarios (en memoria para pruebas)
usuarios_db = {
    'Ana López': {
        'id_usuario': 1,
        'nombre': 'Ana López',
        'edad': 28,
        'genero': 'Femenino',
        'restricciones': ['sin gluten'],
        'alergias': ['nuez'],
        'enfermedades': []
    },
    'Carlos García': {
        'id_usuario': 2,
        'nombre': 'Carlos García',
        'edad': 35,
        'genero': 'Masculino',
        'restricciones': ['sin lactosa'],
        'alergias': ['mariscos'],
        'enfermedades': []
    },
    'Baeza': {
        'id_usuario': 3,
        'nombre': 'Baeza',
        'edad': 25,
        'genero': 'Masculino',
        'restricciones': ['sin lactosa'],
        'alergias': ['mariscos'],
        'enfermedades': []
    },
    'María Rodríguez': {
        'id_usuario': 3,
        'nombre': 'María Rodríguez',
        'edad': 42,
        'genero': 'Femenino',
        'restricciones': ['vegetariano'],
        'alergias': ['soja'],
        'enfermedades': []
    },
    'Juan Pérez': {
        'id_usuario': 4,
        'nombre': 'Juan Pérez',
        'edad': 31,
        'genero': 'Masculino',
        'restricciones': [],
        'alergias': ['gluten'],
        'enfermedades': ['celiaquía']
    }
}

def load_test_data():
    """Cargar datos de prueba desde archivos JSON"""
    try:
        run1_data = None
        run2_data = None
        metrics_data = None
        
        if os.path.exists('data/test_run1.json'):
            with open('data/test_run1.json', 'r', encoding='utf-8') as f:
                run1_data = json.load(f)
        
        if os.path.exists('data/test_run2.json'):
            with open('data/test_run2.json', 'r', encoding='utf-8') as f:
                run2_data = json.load(f)
        
        if os.path.exists('data/metrics.json'):
            with open('data/metrics.json', 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
        
        return run1_data, run2_data, metrics_data
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return None, None, None

@app.route('/')
def index():
    """Página principal - sirve el frontend"""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Endpoint de login para autenticación de usuarios"""
    try:
        data = request.get_json()
        nombre = data.get('username', data.get('nombre', '')).strip()
        
        if not nombre:
            return jsonify({'error': 'Nombre de usuario requerido'}), 400
        
        print(f"🔐 Intentando login para: '{nombre}'")
        
        # Buscar usuario existente
        if nombre in usuarios_db:
            usuario = usuarios_db[nombre]
            token = hashlib.md5(f"{nombre}{time.time()}".encode()).hexdigest()
            
            response = {
                'success': True,
                'id_usuario': usuario['id_usuario'],
                'nombre': usuario['nombre'],
                'token': token,
                'perfil': {
                    'edad': usuario['edad'],
                    'genero': usuario['genero'],
                    'restricciones': usuario['restricciones'],
                    'alergias': usuario['alergias'],
                    'enfermedades': usuario['enfermedades']
                }
            }
            
            print(f"✅ Login exitoso para: {nombre} (ID: {usuario['id_usuario']})")
            return jsonify(response)
        else:
            # Crear usuario nuevo
            nuevo_id = max([u['id_usuario'] for u in usuarios_db.values()]) + 1
            token = hashlib.md5(f"{nombre}{time.time()}".encode()).hexdigest()
            
            # Agregar a la base de datos
            usuarios_db[nombre] = {
                'id_usuario': nuevo_id,
                'nombre': nombre,
                'edad': 25,
                'genero': 'No especificado',
                'restricciones': [],
                'alergias': [],
                'enfermedades': []
            }
            
            response = {
                'success': True,
                'id_usuario': nuevo_id,
                'nombre': nombre,
                'token': token,
                'perfil': {
                    'edad': 25,
                    'genero': 'No especificado',
                    'restricciones': [],
                    'alergias': [],
                    'enfermedades': []
                }
            }
            
            print(f"🆕 Usuario nuevo creado: {nombre} (ID: {nuevo_id})")
            return jsonify(response)
            
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    """Obtener lista de usuarios"""
    try:
        usuarios_lista = []
        for nombre, datos in usuarios_db.items():
            usuarios_lista.append({
                'id_usuario': datos['id_usuario'],
                'nombre': datos['nombre'],
                'edad': datos['edad'],
                'genero': datos['genero']
            })
        
        return jsonify({
            'success': True,
            'usuarios': usuarios_lista,
            'total': len(usuarios_lista)
        })
    except Exception as e:
        print(f"❌ Error obteniendo usuarios: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['POST'])
def add_user():
    """Agregar nuevo usuario"""
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()
        edad = data.get('edad', 25)
        genero = data.get('genero', 'No especificado')
        restricciones = data.get('restricciones', [])
        alergias = data.get('alergias', [])
        enfermedades = data.get('enfermedades', [])
        
        if not nombre:
            return jsonify({'error': 'Nombre de usuario requerido'}), 400
        
        if nombre in usuarios_db:
            return jsonify({'error': 'El usuario ya existe'}), 400
        
        # Crear nuevo usuario
        nuevo_id = max([u['id_usuario'] for u in usuarios_db.values()]) + 1
        usuarios_db[nombre] = {
            'id_usuario': nuevo_id,
            'nombre': nombre,
            'edad': edad,
            'genero': genero,
            'restricciones': restricciones,
            'alergias': alergias,
            'enfermedades': enfermedades
        }
        
        print(f"🆕 Usuario agregado: {nombre} (ID: {nuevo_id})")
        
        return jsonify({
            'success': True,
            'message': 'Usuario agregado correctamente',
            'usuario': {
                'id_usuario': nuevo_id,
                'nombre': nombre,
                'edad': edad,
                'genero': genero
            }
        })
        
    except Exception as e:
        print(f"❌ Error agregando usuario: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):
    """Obtener usuario por ID"""
    try:
        # Buscar usuario en la base de datos simulada
        usuario = None
        for nombre, datos in usuarios_db.items():
            if datos['id_usuario'] == usuario_id:
                usuario = datos
                break
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'usuario': {
                'id_usuario': usuario['id_usuario'],
                'nombre': usuario['nombre'],
                'edad': usuario['edad'],
                'genero': usuario['genero'],
                'restricciones': usuario['restricciones'],
                'alergias': usuario['alergias'],
                'enfermedades': usuario['enfermedades'],
                'fecha_creacion': '2024-01-01T00:00:00Z'
            }
        })
    except Exception as e:
        print(f"❌ Error obteniendo usuario: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def update_usuario(usuario_id):
    """Actualizar usuario"""
    try:
        data = request.get_json()
        
        # Buscar usuario
        usuario = None
        for nombre, datos in usuarios_db.items():
            if datos['id_usuario'] == usuario_id:
                usuario = datos
                break
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Actualizar campos permitidos
        if 'edad' in data:
            usuario['edad'] = data['edad']
        if 'genero' in data:
            usuario['genero'] = data['genero']
        if 'restricciones' in data:
            usuario['restricciones'] = data['restricciones']
        if 'alergias' in data:
            usuario['alergias'] = data['alergias']
        if 'enfermedades' in data:
            usuario['enfermedades'] = data['enfermedades']
        
        print(f"✅ Usuario {usuario_id} actualizado")
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado correctamente',
            'usuario': usuario
        })
    except Exception as e:
        print(f"❌ Error actualizando usuario: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/platos', methods=['GET'])
def get_platos():
    """Obtener lista de platos"""
    try:
        # Simular base de datos de platos
        platos_db = [
            {
                'id_plato': 1,
                'nombre': 'Pizza Margherita',
                'descripcion': 'Pizza clásica con tomate, mozzarella y albahaca',
                'categoria': 'Italiana',
                'ingredientes': ['masa de trigo', 'salsa de tomate', 'mozzarella', 'albahaca'],
                'alergenos_detectados': ['gluten', 'lactosa'],
                'precio': 12.99,
                'fuente': 'Restaurante Italiano',
                'fecha_registro': '2024-01-01T00:00:00Z'
            },
            {
                'id_plato': 2,
                'nombre': 'Ensalada César',
                'descripcion': 'Ensalada fresca con lechuga, pollo, crutones y aderezo césar',
                'categoria': 'Ensaladas',
                'ingredientes': ['lechuga', 'pollo', 'crutones', 'queso parmesano', 'aderezo césar'],
                'alergenos_detectados': ['gluten', 'lactosa', 'huevo'],
                'precio': 8.99,
                'fuente': 'Restaurante Saludable',
                'fecha_registro': '2024-01-02T00:00:00Z'
            },
            {
                'id_plato': 3,
                'nombre': 'Salmón a la parrilla',
                'descripcion': 'Salmón fresco cocinado a la parrilla con vegetales',
                'categoria': 'Pescados',
                'ingredientes': ['salmón', 'limón', 'hierbas', 'aceite de oliva'],
                'alergenos_detectados': ['pescado'],
                'precio': 18.99,
                'fuente': 'Marisquería',
                'fecha_registro': '2024-01-03T00:00:00Z'
            },
            {
                'id_plato': 4,
                'nombre': 'Enchiladas Suizas',
                'descripcion': 'Tortillas rellenas de pollo con salsa verde y queso suizo',
                'categoria': 'Mexicana',
                'ingredientes': ['tortillas', 'pollo', 'queso suizo', 'crema', 'salsa verde'],
                'alergenos_detectados': ['lactosa', 'gluten'],
                'precio': 14.99,
                'fuente': 'Restaurante Mexicano',
                'fecha_registro': '2024-01-04T00:00:00Z'
            },
            {
                'id_plato': 5,
                'nombre': 'Camarones al Ajillo',
                'descripcion': 'Camarones frescos cocinados con ajo y aceite de oliva',
                'categoria': 'Mariscos',
                'ingredientes': ['camarones', 'ajo', 'aceite de oliva', 'perejil'],
                'alergenos_detectados': ['mariscos'],
                'precio': 16.99,
                'fuente': 'Marisquería',
                'fecha_registro': '2024-01-05T00:00:00Z'
            }
        ]
        
        # Filtros opcionales
        categoria = request.args.get('categoria')
        fuente = request.args.get('fuente')
        alergeno = request.args.get('alergeno')
        
        platos_filtrados = platos_db
        
        if categoria:
            platos_filtrados = [p for p in platos_filtrados if categoria.lower() in p['categoria'].lower()]
        
        if fuente:
            platos_filtrados = [p for p in platos_filtrados if fuente.lower() in p['fuente'].lower()]
        
        if alergeno:
            platos_filtrados = [p for p in platos_filtrados if alergeno.lower() in [a.lower() for a in p['alergenos_detectados']]]
        
        return jsonify({
            'success': True,
            'platos': platos_filtrados,
            'total': len(platos_filtrados)
        })
    except Exception as e:
        print(f"❌ Error obteniendo platos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/platos/<int:plato_id>', methods=['GET'])
def get_plato(plato_id):
    """Obtener plato por ID"""
    try:
        # Simular búsqueda de plato
        platos_db = [
            {
                'id_plato': 1,
                'nombre': 'Pizza Margherita',
                'descripcion': 'Pizza clásica con tomate, mozzarella y albahaca',
                'categoria': 'Italiana',
                'ingredientes': ['masa de trigo', 'salsa de tomate', 'mozzarella', 'albahaca'],
                'alergenos_detectados': ['gluten', 'lactosa'],
                'precio': 12.99,
                'fuente': 'Restaurante Italiano',
                'fecha_registro': '2024-01-01T00:00:00Z'
            }
        ]
        
        plato = next((p for p in platos_db if p['id_plato'] == plato_id), None)
        
        if not plato:
            return jsonify({'error': 'Plato no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'plato': plato
        })
    except Exception as e:
        print(f"❌ Error obteniendo plato: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/platos', methods=['POST'])
def create_plato():
    """Crear nuevo plato"""
    try:
        data = request.get_json()
        
        nuevo_plato = {
            'id_plato': len(platos_db) + 1,
            'nombre': data.get('nombre'),
            'descripcion': data.get('descripcion'),
            'categoria': data.get('categoria'),
            'ingredientes': data.get('ingredientes', []),
            'alergenos_detectados': data.get('alergenos_detectados', []),
            'precio': data.get('precio', 0),
            'fuente': data.get('fuente'),
            'fecha_registro': datetime.now().isoformat()
        }
        
        # En un sistema real, aquí se guardaría en la base de datos
        print(f"✅ Plato creado: {nuevo_plato['nombre']}")
        
        return jsonify({
            'success': True,
            'message': 'Plato creado correctamente',
            'plato': nuevo_plato
        })
    except Exception as e:
        print(f"❌ Error creando plato: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['GET'])
def get_feedback():
    """Obtener lista de feedbacks"""
    try:
        usuario_id = request.args.get('usuario_id')
        plato_id = request.args.get('plato_id')
        
        # Simular base de datos de feedback
        feedback_db = [
            {
                'id_feedback': 1,
                'usuario_id': 1,
                'plato_id': 1,
                'comentario': 'Excelente pizza, muy sabrosa',
                'calificacion': 5,
                'tipo_feedback': 'positivo',
                'fecha': '2024-01-15T10:30:00Z'
            },
            {
                'id_feedback': 2,
                'usuario_id': 2,
                'plato_id': 2,
                'comentario': 'La ensalada estaba un poco seca',
                'calificacion': 3,
                'tipo_feedback': 'negativo',
                'fecha': '2024-01-16T14:20:00Z'
            }
        ]
        
        # Aplicar filtros
        feedback_filtrado = feedback_db
        if usuario_id:
            feedback_filtrado = [f for f in feedback_filtrado if f['usuario_id'] == int(usuario_id)]
        if plato_id:
            feedback_filtrado = [f for f in feedback_filtrado if f['plato_id'] == int(plato_id)]
        
        return jsonify({
            'success': True,
            'feedback': feedback_filtrado,
            'total': len(feedback_filtrado)
        })
    except Exception as e:
        print(f"❌ Error obteniendo feedback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def create_feedback():
    """Crear nuevo feedback"""
    try:
        data = request.get_json()
        
        nuevo_feedback = {
            'id_feedback': len(feedback_data) + 1,
            'usuario_id': data.get('usuario_id'),
            'plato_id': data.get('plato_id'),
            'comentario': data.get('comentario'),
            'calificacion': data.get('calificacion'),
            'tipo_feedback': data.get('tipo_feedback'),
            'fecha': datetime.now().isoformat()
        }
        
        feedback_data.append(nuevo_feedback)
        
        print(f"✅ Feedback creado: {nuevo_feedback['comentario'][:50]}...")
        
        return jsonify({
            'success': True,
            'message': 'Feedback enviado correctamente',
            'feedback': nuevo_feedback
        })
    except Exception as e:
        print(f"❌ Error creando feedback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/acciones_ia', methods=['GET'])
def get_acciones_ia():
    """Obtener historial de acciones IA"""
    try:
        usuario_id = request.args.get('usuario_id')
        plato_id = request.args.get('plato_id')
        
        # Simular base de datos de acciones IA
        acciones_db = [
            {
                'id_accion': 1,
                'usuario_id': 1,
                'plato_id': 1,
                'tipo_accion': 'analisis',
                'entrada_prompt': 'Analizar pizza margherita para usuario con alergia al gluten',
                'salida_resumen': 'Plato contiene gluten en la masa. No recomendado para celíacos.',
                'exito': True,
                'fecha': '2024-01-15T09:00:00Z'
            },
            {
                'id_accion': 2,
                'usuario_id': 2,
                'plato_id': 2,
                'tipo_accion': 'recomendacion',
                'entrada_prompt': 'Recomendar alternativas para ensalada césar',
                'salida_resumen': 'Sugerir ensalada sin crutones y con aderezo sin huevo',
                'exito': True,
                'fecha': '2024-01-16T11:30:00Z'
            }
        ]
        
        # Aplicar filtros
        acciones_filtradas = acciones_db
        if usuario_id:
            acciones_filtradas = [a for a in acciones_filtradas if a['usuario_id'] == int(usuario_id)]
        if plato_id:
            acciones_filtradas = [a for a in acciones_filtradas if a['plato_id'] == int(plato_id)]
        
        return jsonify({
            'success': True,
            'acciones': acciones_filtradas,
            'total': len(acciones_filtradas)
        })
    except Exception as e:
        print(f"❌ Error obteniendo acciones IA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/acciones_ia', methods=['POST'])
def create_accion_ia():
    """Registrar nueva acción IA"""
    try:
        data = request.get_json()
        
        nueva_accion = {
            'id_accion': 100 + len(feedback_data),  # ID temporal
            'usuario_id': data.get('usuario_id'),
            'plato_id': data.get('plato_id'),
            'tipo_accion': data.get('tipo_accion'),
            'entrada_prompt': data.get('entrada_prompt'),
            'salida_resumen': data.get('salida_resumen'),
            'exito': data.get('exito', True),
            'fecha': datetime.now().isoformat()
        }
        
        print(f"✅ Acción IA registrada: {nueva_accion['tipo_accion']}")
        
        return jsonify({
            'success': True,
            'message': 'Acción IA registrada correctamente',
            'accion': nueva_accion
        })
    except Exception as e:
        print(f"❌ Error creando acción IA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/mejora_ia', methods=['GET'])
def get_mejora_ia():
    """Obtener mejoras IA"""
    try:
        accion_id = request.args.get('accion_id')
        
        # Simular base de datos de mejoras IA
        mejoras_db = [
            {
                'id_mejora': 1,
                'id_accion': 1,
                'ajuste_prompt': 'Mejorar detección de alérgenos en análisis',
                'observacion': 'El sistema mejoró la precisión en 15%',
                'confianza': 0.85,
                'fecha': '2024-01-20T16:00:00Z'
            }
        ]
        
        # Aplicar filtros
        mejoras_filtradas = mejoras_db
        if accion_id:
            mejoras_filtradas = [m for m in mejoras_filtradas if m['id_accion'] == int(accion_id)]
        
        return jsonify({
            'success': True,
            'mejoras': mejoras_filtradas,
            'total': len(mejoras_filtradas)
        })
    except Exception as e:
        print(f"❌ Error obteniendo mejoras IA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/mejora_ia', methods=['POST'])
def create_mejora_ia():
    """Crear nueva mejora IA"""
    try:
        data = request.get_json()
        
        nueva_mejora = {
            'id_mejora': 200 + len(feedback_data),  # ID temporal
            'id_accion': data.get('id_accion'),
            'ajuste_prompt': data.get('ajuste_prompt'),
            'observacion': data.get('observacion'),
            'confianza': data.get('confianza', 0.5),
            'fecha': datetime.now().isoformat()
        }
        
        print(f"✅ Mejora IA creada para acción {nueva_mejora['id_accion']}")
        
        return jsonify({
            'success': True,
            'message': 'Mejora IA aplicada correctamente',
            'mejora': nueva_mejora
        })
    except Exception as e:
        print(f"❌ Error creando mejora IA: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_menu():
    """Analizar menú de texto"""
    try:
        data = request.get_json()
        menu_text = data.get('menu_text', '')
        user_id = data.get('user_id', data.get('usuario_id', 'guest_001'))
        
        if not menu_text:
            return jsonify({'error': 'Texto del menú requerido'}), 400
        
        print(f"Analizando menu para usuario {user_id}")
        print(f"Texto: {menu_text[:100]}...")
        
        # Simular análisis de IA
        dishes = simulate_menu_analysis(menu_text)
        
        response = {
            'success': True,
            'run_id': f'run_{current_run}',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'menu_text': menu_text,
            'dishes': dishes,
            'overall_analysis': {
                'total_dishes': len(dishes),
                'safe_dishes': len([d for d in dishes if d['compatibility_level'] == 'safe']),
                'warning_dishes': len([d for d in dishes if d['compatibility_level'] == 'warning']),
                'danger_dishes': len([d for d in dishes if d['compatibility_level'] == 'danger']),
                'main_concerns': ['gluten', 'lactosa', 'nueces'],
                'recommendations': 'Menú con opciones mixtas. Considerar alternativas sin alérgenos.'
            }
        }
        
        print(f"Analisis completado: {len(dishes)} platillos encontrados")
        return jsonify(response)
        
    except Exception as e:
        print(f"Error en analisis: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['GET'])
def get_recommendations():
    """Obtener recomendaciones de platillos"""
    recommendations = {
        'safe_dishes': [
            'Ensalada verde con pollo',
            'Salmón a la parrilla',
            'Quinoa con vegetales',
            'Sopa de lentejas',
            'Pollo a la plancha'
        ],
        'warning_dishes': [
            'Pizza (contiene gluten y lácteos)',
            'Pasta (contiene gluten)',
            'Helado (contiene lácteos)',
            'Sándwich (puede contener gluten)'
        ],
        'danger_dishes': [
            'Platos con nueces',
            'Mariscos para alérgicos',
            'Platos con soja',
            'Postres con frutos secos'
        ]
    }
    return jsonify(recommendations)

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """Recibir feedback del usuario"""
    try:
        data = request.get_json()
        
        feedback = {
            'id': len(feedback_data) + 1,
            'dish_name': data.get('dish_name'),
            'feedback_type': data.get('feedback_type'),
            'rating': data.get('rating'),
            'comment': data.get('comment'),
            'user_id': data.get('user_id', data.get('usuario_id')),
            'timestamp': datetime.now().isoformat()
        }
        
        feedback_data.append(feedback)
        
        print(f"Feedback recibido: {feedback['dish_name']} - Rating: {feedback['rating']}/5")
        
        return jsonify({
            'success': True,
            'message': 'Feedback recibido correctamente',
            'feedback_id': feedback['id']
        })
        
    except Exception as e:
        print(f"Error recibiendo feedback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/improve', methods=['POST'])
def execute_improvement():
    """Ejecutar mejora del sistema basada en feedback"""
    global current_run
    current_run += 1
    
    print(f"Ejecutando mejora - Run {current_run}")
    print(f"Total feedback recibido: {len(feedback_data)}")
    
    # Simular mejora basada en feedback
    improvements = {
        'run_id': f'run_{current_run}',
        'timestamp': datetime.now().isoformat(),
        'improvements_applied': len(feedback_data),
        'comparisons': generate_comparison_data(),
        'metrics_improved': {
            'accuracy_improvement': random.uniform(0.02, 0.05),
            'satisfaction_improvement': random.uniform(0.1, 0.3)
        }
    }
    
    print(f"Mejora completada - Run {current_run}")
    return jsonify(improvements)

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Obtener métricas del sistema"""
    try:
        _, _, metrics = load_test_data()
        
        if metrics:
            print("Metricas cargadas desde archivo")
            return jsonify(metrics)
        else:
            # Métricas de fallback
            fallback_metrics = {
                'accuracy': 0.89,
                'satisfaction': 4.2,
                'improvement_rate': 0.12,
                'total_analyses': 1000,
                'total_feedback': 50,
                'positive_feedback_percentage': 0.75,
                'trends': {
                    'accuracy_trend': [0.85, 0.87, 0.89, 0.91, 0.92],
                    'satisfaction_trend': [4.0, 4.1, 4.2, 4.2, 4.3],
                    'improvement_trend': [0.10, 0.12, 0.13, 0.14, 0.15]
                }
            }
            print("Metricas de fallback cargadas")
            return jsonify(fallback_metrics)
            
    except Exception as e:
        print(f"Error cargando metricas: {e}")
        return jsonify({'error': str(e)}), 500

def simulate_menu_analysis(menu_text):
    """Simular análisis de IA del menú"""
    dishes = []
    menu_lower = menu_text.lower()
    
    # Detectar platos comunes
    if 'pizza' in menu_lower:
        dishes.append({
            'name': 'Pizza',
            'ingredients': ['masa de trigo', 'salsa de tomate', 'queso', 'ingredientes varios'],
            'compatibility_level': 'warning',
            'analysis': 'Contiene gluten y lácteos. Puede causar problemas para personas con intolerancia a la lactosa o celiaquía.',
            'recommendations': 'Considerar opciones sin gluten y sin lactosa para mayor inclusividad.'
        })
    
    if 'ensalada' in menu_lower or 'salad' in menu_lower:
        dishes.append({
            'name': 'Ensalada',
            'ingredients': ['lechuga', 'vegetales', 'aderezo'],
            'compatibility_level': 'safe',
            'analysis': 'Opción relativamente segura. El pollo es una proteína limpia y la lechuga es bien tolerada.',
            'recommendations': 'Verificar ingredientes del aderezo para alérgenos ocultos.'
        })
    
    if 'pasta' in menu_lower:
        dishes.append({
            'name': 'Pasta',
            'ingredients': ['pasta de trigo', 'salsa', 'ingredientes varios'],
            'compatibility_level': 'warning',
            'analysis': 'Contiene gluten. No recomendado para celíacos.',
            'recommendations': 'Considerar pasta sin gluten como alternativa.'
        })
    
    if 'sándwich' in menu_lower or 'sandwich' in menu_lower:
        dishes.append({
            'name': 'Sándwich',
            'ingredients': ['pan', 'ingredientes varios'],
            'compatibility_level': 'warning',
            'analysis': 'Puede contener gluten y otros alérgenos.',
            'recommendations': 'Verificar ingredientes específicos del pan y rellenos.'
        })
    
    # Si no se detectan platos específicos, crear uno genérico
    if not dishes:
        dishes.append({
            'name': 'Plato Principal',
            'ingredients': ['ingredientes varios'],
            'compatibility_level': 'warning',
            'analysis': 'Análisis general: verificar ingredientes específicos para determinar compatibilidad.',
            'recommendations': 'Consultar ingredientes detallados y preparación.'
        })
    
    return dishes

def generate_comparison_data():
    """Generar datos de comparación Run 1 vs Run 2"""
    return [
        {
            'dish_name': 'Pizza',
            'before': {
                'compatibility_level': 'warning',
                'analysis': 'Contiene gluten y lácteos. Riesgo para intolerantes.'
            },
            'after': {
                'compatibility_level': 'warning',
                'analysis': 'Contiene gluten y lácteos. MEJORADO: Opciones sin gluten disponibles, información detallada de alérgenos, alternativas veganas.'
            }
        },
        {
            'dish_name': 'Ensalada',
            'before': {
                'compatibility_level': 'safe',
                'analysis': 'Opción segura con vegetales frescos.'
            },
            'after': {
                'compatibility_level': 'safe',
                'analysis': 'Opción segura. MEJORADO: Ingredientes orgánicos certificados, aderezo sin alérgenos disponible, información nutricional detallada.'
            }
        }
    ]

if __name__ == '__main__':
    print("=" * 60)
    print("AliMentor AI - Sistema de Analisis Alimentario")
    print("=" * 60)
    print("Backend Flask iniciando...")
    print("Frontend disponible en: http://127.0.0.1:5000")
    print("API Endpoints:")
    print("   • POST /login - Autenticación de usuarios")
    print("   • GET  /users - Listar usuarios")
    print("   • POST /users - Agregar usuario")
    print("   • GET  /usuarios/<id> - Obtener usuario por ID")
    print("   • PUT  /usuarios/<id> - Actualizar usuario")
    print("   • GET  /platos - Listar platos (con filtros)")
    print("   • GET  /platos/<id> - Obtener plato por ID")
    print("   • POST /platos - Crear plato")
    print("   • GET  /feedback - Obtener feedbacks (con filtros)")
    print("   • POST /feedback - Crear feedback")
    print("   • GET  /acciones_ia - Obtener acciones IA")
    print("   • POST /acciones_ia - Crear acción IA")
    print("   • GET  /mejora_ia - Obtener mejoras IA")
    print("   • POST /mejora_ia - Crear mejora IA")
    print("   • POST /analyze - Analizar menu")
    print("   • GET  /recommend - Obtener recomendaciones")
    print("   • POST /improve - Ejecutar mejora")
    print("   • GET  /metrics - Obtener metricas")
    print("=" * 60)
    print("Iniciando servidor...")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
