"""
AliMentor AI - Backend Flask Example
Ejemplo de implementación del backend para integrar con el frontend
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import random
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilitar CORS para el frontend

# Cargar datos de ejemplo
def load_test_data():
    try:
        with open('data/test_run1.json', 'r', encoding='utf-8') as f:
            run1_data = json.load(f)
        with open('data/test_run2.json', 'r', encoding='utf-8') as f:
            run2_data = json.load(f)
        with open('data/metrics.json', 'r', encoding='utf-8') as f:
            metrics_data = json.load(f)
        return run1_data, run2_data, metrics_data
    except FileNotFoundError:
        # Datos de fallback si no existen los archivos
        return None, None, None

# Variables globales para simular estado
current_run = 1
feedback_data = []

@app.route('/')
def index():
    """Página principal - sirve el frontend"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_menu():
    """Analizar menú de texto"""
    try:
        data = request.get_json()
        menu_text = data.get('menu_text', '')
        user_id = data.get('user_id', 'guest_001')
        
        if not menu_text:
            return jsonify({'error': 'Texto del menú requerido'}), 400
        
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
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recommend', methods=['GET'])
def get_recommendations():
    """Obtener recomendaciones de platillos"""
    recommendations = {
        'safe_dishes': [
            'Ensalada verde con pollo',
            'Salmón a la parrilla',
            'Quinoa con vegetales',
            'Sopa de lentejas'
        ],
        'warning_dishes': [
            'Pizza (contiene gluten y lácteos)',
            'Pasta (contiene gluten)',
            'Helado (contiene lácteos)'
        ],
        'danger_dishes': [
            'Platos con nueces',
            'Mariscos para alérgicos',
            'Platos con soja'
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
            'user_id': data.get('user_id'),
            'timestamp': datetime.now().isoformat()
        }
        
        feedback_data.append(feedback)
        
        return jsonify({
            'success': True,
            'message': 'Feedback recibido correctamente',
            'feedback_id': feedback['id']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/improve', methods=['POST'])
def execute_improvement():
    """Ejecutar mejora del sistema basada en feedback"""
    global current_run
    current_run += 1
    
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
    
    return jsonify(improvements)

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Obtener métricas del sistema"""
    try:
        _, _, metrics = load_test_data()
        
        if metrics:
            return jsonify(metrics)
        else:
            # Métricas de fallback
            return jsonify({
                'accuracy': 0.89,
                'satisfaction': 4.2,
                'improvement_rate': 0.12,
                'total_analyses': 1000,
                'total_feedback': 50,
                'positive_feedback_percentage': 0.75
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def simulate_menu_analysis(menu_text):
    """Simular análisis de IA del menú"""
    # Extraer platos del texto (simulación simple)
    dishes = []
    
    # Buscar platos comunes en el texto
    if 'pizza' in menu_text.lower():
        dishes.append({
            'name': 'Pizza',
            'ingredients': ['masa de trigo', 'salsa de tomate', 'queso', 'ingredientes varios'],
            'compatibility_level': 'warning',
            'analysis': 'Contiene gluten y lácteos. Puede causar problemas para personas con intolerancia.',
            'recommendations': 'Considerar opciones sin gluten y sin lactosa.'
        })
    
    if 'ensalada' in menu_text.lower():
        dishes.append({
            'name': 'Ensalada',
            'ingredients': ['lechuga', 'vegetales', 'aderezo'],
            'compatibility_level': 'safe',
            'analysis': 'Opción relativamente segura. Verificar ingredientes del aderezo.',
            'recommendations': 'Opción saludable y bien tolerada.'
        })
    
    if 'pasta' in menu_text.lower():
        dishes.append({
            'name': 'Pasta',
            'ingredients': ['pasta de trigo', 'salsa', 'ingredientes varios'],
            'compatibility_level': 'warning',
            'analysis': 'Contiene gluten. No recomendado para celíacos.',
            'recommendations': 'Considerar pasta sin gluten.'
        })
    
    # Si no se detectan platos específicos, crear uno genérico
    if not dishes:
        dishes.append({
            'name': 'Plato Principal',
            'ingredients': ['ingredientes varios'],
            'compatibility_level': 'warning',
            'analysis': 'Análisis general: verificar ingredientes específicos.',
            'recommendations': 'Consultar ingredientes detallados.'
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
                'analysis': 'Contiene gluten y lácteos. MEJORADO: Opciones sin gluten disponibles, información detallada de alérgenos.'
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
                'analysis': 'Opción segura. MEJORADO: Ingredientes orgánicos certificados, aderezo sin alérgenos disponible.'
            }
        }
    ]

if __name__ == '__main__':
    print("🍽️  AliMentor AI Backend iniciando...")
    print("📡 API disponible en: http://127.0.0.1:5000")
    print("🌐 Frontend disponible en: http://127.0.0.1:5000")
    print("📚 Documentación API: http://127.0.0.1:5000/metrics")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

