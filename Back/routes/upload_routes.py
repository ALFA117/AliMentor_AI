"""
Rutas para upload de menús - AliMentor AI
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from typing import Dict, Any, List
import json

from services.db_service import DatabaseService
from services.ai_service import AIService
from utils.data_cleaner import DataCleaner

logger = logging.getLogger(__name__)

# Crear Blueprint
upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

# Inicializar servicios (se configurarán en app.py)
db_service = None
ai_service = None
data_cleaner = None

def init_services(db_svc: DatabaseService, ai_svc: AIService, data_cln: DataCleaner):
    """Inicializa los servicios necesarios"""
    global db_service, ai_service, data_cleaner
    db_service = db_svc
    ai_service = ai_svc
    data_cleaner = data_cln

@upload_bp.route('', methods=['POST'])
def upload_menu():
    """
    Sube un menú (texto o imagen simulada) y extrae platillos
    
    Endpoint: POST /upload
    
    Body:
    {
        "menu_data": "Texto del menú o datos de imagen",
        "menu_type": "texto|imagen",
        "restaurant_name": "Nombre del restaurante" (opcional)
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "platillos": [
                {
                    "nombre": "Ensalada César",
                    "descripcion": "Lechuga romana, crutones, parmesano",
                    "categoria": "entrada",
                    "imagen_url": "url_de_imagen"
                }
            ],
            "total_platillos": 5,
            "restaurant_name": "Restaurante XYZ"
        }
    }
    """
    try:
        # Validar datos de entrada
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos JSON',
                'message': 'El cuerpo de la petición debe contener datos JSON válidos'
            }), 400
        
        menu_data = data.get('menu_data')
        menu_type = data.get('menu_type', 'texto')
        restaurant_name = data.get('restaurant_name', 'Restaurante')
        
        if not menu_data or not menu_data.strip():
            return jsonify({
                'success': False,
                'error': 'Datos de menú requeridos',
                'message': 'El campo menu_data es obligatorio y no puede estar vacío'
            }), 400
        
        # Procesar según el tipo de menú
        if menu_type == 'imagen':
            # Simular OCR - en producción aquí se procesaría la imagen
            platillos = _simular_ocr_procesamiento(menu_data)
        else:
            # Procesar texto del menú
            platillos = _procesar_texto_menu(menu_data)
        
        # Limpiar y validar datos de platillos
        platillos_limpios = []
        for platillo_data in platillos:
            platillo_limpio = data_cleaner.validar_datos_plato(platillo_data)
            if platillo_limpio['valido']:
                platillos_limpios.append(platillo_limpio['datos_validados'])
        
        # Guardar platillos en base de datos
        platillos_guardados = []
        for platillo_data in platillos_limpios:
            # Agregar metadatos
            platillo_data['imagen_url'] = f"https://ejemplo.com/imagenes/{platillo_data['nombre'].lower().replace(' ', '_')}.jpg"
            
            # Guardar en BD
            platillo_guardado = db_service.crear_plato(platillo_data)
            if platillo_guardado:
                platillos_guardados.append(platillo_guardado.to_dict())
        
        # Preparar respuesta
        respuesta = {
            'success': True,
            'data': {
                'platillos': platillos_guardados,
                'total_platillos': len(platillos_guardados),
                'restaurant_name': restaurant_name,
                'menu_type': menu_type,
                'fecha_procesamiento': datetime.utcnow().isoformat()
            },
            'message': f'Menú procesado exitosamente. Se extrajeron {len(platillos_guardados)} platillos.'
        }
        
        logger.info(f"Menú procesado: {len(platillos_guardados)} platillos de {restaurant_name}")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error procesando menú: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado al procesar el menú',
            'details': str(e)
        }), 500

def _simular_ocr_procesamiento(imagen_data: str) -> List[Dict[str, Any]]:
    """
    Simula el procesamiento OCR de una imagen de menú
    
    Args:
        imagen_data: Datos de la imagen (simulado)
        
    Returns:
        Lista de platillos extraídos
    """
    # En producción, aquí se usaría una librería como Tesseract o Azure OCR
    # Por ahora simulamos la extracción
    logger.info("Simulando procesamiento OCR...")
    
    # Simular platillos extraídos de imagen
    platillos_simulados = [
        {
            'nombre': 'Pizza Margherita',
            'descripcion': 'Tomate, mozzarella, albahaca fresca',
            'categoria': 'plato_principal'
        },
        {
            'nombre': 'Ensalada Verde',
            'descripcion': 'Lechuga, espinacas, tomate cherry',
            'categoria': 'entrada'
        },
        {
            'nombre': 'Tiramisú',
            'descripcion': 'Postre italiano con café y mascarpone',
            'categoria': 'postre'
        }
    ]
    
    return platillos_simulados

def _procesar_texto_menu(texto_menu: str) -> List[Dict[str, Any]]:
    """
    Procesa texto de menú y extrae platillos
    
    Args:
        texto_menu: Texto del menú
        
    Returns:
        Lista de platillos extraídos
    """
    try:
        # Limpiar texto del menú
        texto_limpio = data_cleaner.limpiar_texto_menu(texto_menu)
        
        # Extraer platillos usando patrones
        platillos = data_cleaner.extraer_platos_del_texto(texto_limpio)
        
        # Si no se extrajeron platillos, usar análisis con IA
        if not platillos:
            logger.info("No se pudieron extraer platillos con patrones, usando IA...")
            analisis_ia = ai_service.analizar_menu(texto_limpio)
            
            if 'platos_detectados' in analisis_ia:
                platillos = analisis_ia['platos_detectados']
        
        return platillos
        
    except Exception as e:
        logger.error(f"Error procesando texto de menú: {e}")
        return []

@upload_bp.route('/batch', methods=['POST'])
def upload_batch_menus():
    """
    Sube múltiples menús en lote
    
    Endpoint: POST /upload/batch
    
    Body:
    {
        "menus": [
            {
                "menu_data": "Texto del menú 1",
                "menu_type": "texto",
                "restaurant_name": "Restaurante A"
            },
            {
                "menu_data": "Datos de imagen 2",
                "menu_type": "imagen",
                "restaurant_name": "Restaurante B"
            }
        ]
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "menus_procesados": [...],
            "total_menus": 2,
            "total_platillos": 8,
            "errores": []
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'menus' not in data:
            return jsonify({
                'success': False,
                'error': 'Datos de menús requeridos',
                'message': 'Se requiere un array de menús en el campo "menus"'
            }), 400
        
        menus = data['menus']
        if not isinstance(menus, list) or len(menus) == 0:
            return jsonify({
                'success': False,
                'error': 'Array de menús inválido',
                'message': 'El campo "menus" debe ser un array no vacío'
            }), 400
        
        # Limitar número de menús por lote
        max_menus = 10
        if len(menus) > max_menus:
            return jsonify({
                'success': False,
                'error': 'Demasiados menús',
                'message': f'Máximo {max_menus} menús por lote'
            }), 400
        
        menus_procesados = []
        errores = []
        total_platillos = 0
        
        for i, menu_data in enumerate(menus):
            try:
                menu_type = menu_data.get('menu_type', 'texto')
                restaurant_name = menu_data.get('restaurant_name', f'Restaurante {i+1}')
                menu_content = menu_data.get('menu_data', '')
                
                if not menu_content.strip():
                    errores.append({
                        'indice': i,
                        'error': 'Datos de menú vacíos',
                        'restaurant_name': restaurant_name
                    })
                    continue
                
                # Procesar menú individual
                if menu_type == 'imagen':
                    platillos = _simular_ocr_procesamiento(menu_content)
                else:
                    platillos = _procesar_texto_menu(menu_content)
                
                # Guardar platillos
                platillos_guardados = []
                for platillo_data in platillos:
                    platillo_limpio = data_cleaner.validar_datos_plato(platillo_data)
                    if platillo_limpio['valido']:
                        platillo_data_limpio = platillo_limpio['datos_validados']
                        platillo_data_limpio['imagen_url'] = f"https://ejemplo.com/imagenes/{platillo_data_limpio['nombre'].lower().replace(' ', '_')}.jpg"
                        
                        platillo_guardado = db_service.crear_plato(platillo_data_limpio)
                        if platillo_guardado:
                            platillos_guardados.append(platillo_guardado.to_dict())
                
                menus_procesados.append({
                    'indice': i,
                    'restaurant_name': restaurant_name,
                    'menu_type': menu_type,
                    'platillos': platillos_guardados,
                    'total_platillos': len(platillos_guardados)
                })
                
                total_platillos += len(platillos_guardados)
                
            except Exception as e:
                errores.append({
                    'indice': i,
                    'error': str(e),
                    'restaurant_name': menu_data.get('restaurant_name', f'Restaurante {i+1}')
                })
        
        respuesta = {
            'success': True,
            'data': {
                'menus_procesados': menus_procesados,
                'total_menus': len(menus),
                'total_platillos': total_platillos,
                'errores': errores,
                'exitosos': len(menus_procesados),
                'fallidos': len(errores)
            },
            'message': f'Procesamiento en lote completado: {len(menus_procesados)} exitosos, {len(errores)} fallidos'
        }
        
        logger.info(f"Procesamiento en lote completado: {len(menus_procesados)} exitosos, {len(errores)} fallidos")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error en procesamiento en lote: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado durante el procesamiento en lote',
            'details': str(e)
        }), 500
