"""
Rutas para análisis de menús - AliMentor AI
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from typing import Dict, Any, List

from services.ai_service import AIService
from services.db_service import DatabaseService
from services.feedback_analyzer import FeedbackAnalyzer
from utils.data_cleaner import DataCleaner
from config import Config

logger = logging.getLogger(__name__)

# Crear Blueprint
analyze_bp = Blueprint('analyze', __name__, url_prefix='/analyze')

# Inicializar servicios (se configurarán en app.py)
ai_service = None
db_service = None
feedback_analyzer = None
data_cleaner = None

def init_services(ai_svc: AIService, db_svc: DatabaseService, 
                 feedback_anal: FeedbackAnalyzer, data_cln: DataCleaner):
    """Inicializa los servicios necesarios"""
    global ai_service, db_service, feedback_analyzer, data_cleaner
    ai_service = ai_svc
    db_service = db_svc
    feedback_analyzer = feedback_anal
    data_cleaner = data_cln

@analyze_bp.route('', methods=['POST'])
def analyze_menu():
    """
    Analiza compatibilidad alimentaria de platillos con perfil del usuario
    
    Endpoint: POST /analyze
    
    Body:
    {
        "platillos": [
            {
                "id_plato": 1,
                "nombre": "Ensalada César",
                "descripcion": "Lechuga, crutones, parmesano"
            }
        ],
        "perfil_usuario": {
            "id_usuario": 1,
            "restricciones": ["vegetariano"],
            "alergias": ["lactosa"],
            "enfermedades": []
        }
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "compatibilidad": [
                {
                    "id_plato": 1,
                    "nombre": "Ensalada César",
                    "nivel_riesgo": "🟡",
                    "ingredientes_peligrosos": ["lactosa"],
                    "recomendacion": "Contiene lácteos"
                }
            ],
            "accion_ia_id": 123
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
        
        platillos = data.get('platillos', [])
        perfil_usuario = data.get('perfil_usuario', {})
        
        if not platillos:
            return jsonify({
                'success': False,
                'error': 'Lista de platillos requerida',
                'message': 'El campo platillos es obligatorio y no puede estar vacío'
            }), 400
        
        if not perfil_usuario:
            return jsonify({
                'success': False,
                'error': 'Perfil de usuario requerido',
                'message': 'El campo perfil_usuario es obligatorio'
            }), 400
        
        # Crear acción de IA para tracking
        accion_data = {
            'tipo_accion': 'analisis_compatibilidad',
            'usuario_id': perfil_usuario.get('id_usuario'),
            'entrada': f"Análisis de compatibilidad para {len(platillos)} platillos",
            'exito': False
        }
        
        accion_ia = db_service.crear_accion_ia(accion_data)
        if not accion_ia:
            return jsonify({
                'success': False,
                'error': 'Error creando acción de IA',
                'message': 'No se pudo registrar la acción de análisis'
            }), 500
        
        # Analizar compatibilidad de cada platillo
        compatibilidad = []
        restricciones_usuario = (
            perfil_usuario.get('restricciones', []) + 
            perfil_usuario.get('alergias', []) + 
            perfil_usuario.get('enfermedades', [])
        )
        
        for platillo in platillos:
            try:
                # Obtener información del platillo desde BD
                plato_bd = db_service.obtener_plato(platillo.get('id_plato'))
                if not plato_bd:
                    continue
                
                # Analizar compatibilidad con IA
                analisis_platillo = ai_service.analizar_compatibilidad_platillo(
                    platillo, 
                    restricciones_usuario
                )
                
                # Determinar nivel de riesgo
                nivel_riesgo = _determinar_nivel_riesgo(analisis_platillo, restricciones_usuario)
                
                compatibilidad.append({
                    'id_plato': platillo.get('id_plato'),
                    'nombre': platillo.get('nombre'),
                    'nivel_riesgo': nivel_riesgo,
                    'ingredientes_peligrosos': analisis_platillo.get('ingredientes_peligrosos', []),
                    'recomendacion': analisis_platillo.get('recomendacion', ''),
                    'detalles': analisis_platillo.get('detalles', {})
                })
                
            except Exception as e:
                logger.warning(f"Error analizando platillo {platillo.get('id_plato')}: {e}")
                continue
        
        # Actualizar acción de IA como exitosa
        resumen_analisis = f"Análisis de compatibilidad completado: {len(compatibilidad)} platillos analizados"
        db_service.actualizar_accion_ia(accion_ia.id_accion, True, resumen_analisis)
        
        # Preparar respuesta
        respuesta = {
            'success': True,
            'data': {
                'compatibilidad': compatibilidad,
                'accion_ia_id': accion_ia.id_accion,
                'total_platillos': len(compatibilidad),
                'perfil_usuario': perfil_usuario,
                'fecha_analisis': datetime.utcnow().isoformat()
            },
            'message': f'Análisis de compatibilidad completado para {len(compatibilidad)} platillos.'
        }
        
        logger.info(f"Análisis de compatibilidad completado: {len(compatibilidad)} platillos para usuario {perfil_usuario.get('id_usuario')}")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error en análisis de compatibilidad: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado durante el análisis de compatibilidad',
            'details': str(e)
        }), 500

def _determinar_nivel_riesgo(analisis: Dict[str, Any], restricciones: List[str]) -> str:
    """
    Determina el nivel de riesgo de un platillo
    
    Args:
        analisis: Análisis del platillo
        restricciones: Restricciones del usuario
        
    Returns:
        Emoji del nivel de riesgo (🟢 🟡 🔴)
    """
    ingredientes_peligrosos = analisis.get('ingredientes_peligrosos', [])
    
    if not ingredientes_peligrosos:
        return "🟢"  # Verde - Sin riesgo
    elif len(ingredientes_peligrosos) == 1:
        return "🟡"  # Amarillo - Riesgo medio
    else:
        return "🔴"  # Rojo - Alto riesgo

@analyze_bp.route('/batch', methods=['POST'])
def analyze_batch_menus():
    """
    Analiza múltiples menús en lote
    
    Endpoint: POST /analyze/batch
    
    Body:
    {
        "menus": [
            {
                "menu_text": "Texto del menú 1",
                "user_id": 1
            },
            {
                "menu_text": "Texto del menú 2",
                "user_id": 2
            }
        ]
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "analisis_completados": [...],
            "errores": [...],
            "total_procesados": 2,
            "exitosos": 2,
            "fallidos": 0
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
        
        analisis_completados = []
        errores = []
        
        for i, menu_data in enumerate(menus):
            try:
                menu_text = menu_data.get('menu_text', '')
                user_id = menu_data.get('user_id')
                
                if not menu_text.strip():
                    errores.append({
                        'indice': i,
                        'error': 'Texto de menú vacío',
                        'menu_data': menu_data
                    })
                    continue
                
                # Procesar menú individual
                menu_text_clean = data_cleaner.limpiar_texto_menu(menu_text)
                analisis = ai_service.analizar_menu(menu_text_clean, user_id)
                
                if 'error' in analisis:
                    errores.append({
                        'indice': i,
                        'error': analisis['error'],
                        'menu_data': menu_data
                    })
                    continue
                
                # Guardar platos
                platos_guardados = []
                platos_detectados = analisis.get('platos_detectados', [])
                
                for plato_data in platos_detectados:
                    validacion = data_cleaner.validar_datos_plato(plato_data)
                    plato_validado = validacion['datos_validados']
                    plato_validado['fuente'] = 'analisis_ia_batch'
                    plato_validado['fecha_registro'] = datetime.utcnow()
                    
                    plato_guardado = db_service.crear_plato(plato_validado)
                    if plato_guardado:
                        platos_guardados.append(plato_guardado.to_dict())
                
                analisis_completados.append({
                    'indice': i,
                    'analisis': analisis,
                    'platos_guardados': platos_guardados,
                    'total_platos': len(platos_guardados)
                })
                
            except Exception as e:
                errores.append({
                    'indice': i,
                    'error': str(e),
                    'menu_data': menu_data
                })
        
        respuesta = {
            'success': True,
            'data': {
                'analisis_completados': analisis_completados,
                'errores': errores,
                'total_procesados': len(menus),
                'exitosos': len(analisis_completados),
                'fallidos': len(errores)
            },
            'message': f'Procesamiento en lote completado: {len(analisis_completados)} exitosos, {len(errores)} fallidos'
        }
        
        logger.info(f"Análisis en lote completado: {len(analisis_completados)} exitosos, {len(errores)} fallidos")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error en análisis en lote: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado durante el análisis en lote',
            'details': str(e)
        }), 500

@analyze_bp.route('/status/<int:accion_id>', methods=['GET'])
def get_analysis_status(accion_id: int):
    """
    Obtiene el estado de un análisis específico
    
    Endpoint: GET /analyze/status/<accion_id>
    
    Returns:
    {
        "success": true,
        "data": {
            "accion_ia": {...},
            "platos_relacionados": [...],
            "estado": "completado|en_progreso|fallido"
        }
    }
    """
    try:
        # Obtener acción de IA
        with db_service.get_session() as session:
            from models.acciones_ia import AccionIA
            from models.platos import Plato
            
            accion = session.query(AccionIA).filter(AccionIA.id_accion == accion_id).first()
            if not accion:
                return jsonify({
                    'success': False,
                    'error': 'Acción no encontrada',
                    'message': f'No se encontró la acción con ID {accion_id}'
                }), 404
            
            # Obtener platos relacionados
            platos = session.query(Plato).filter(Plato.id_plato == accion.plato_id).all()
            platos_data = [plato.to_dict() for plato in platos]
            
            # Determinar estado
            if accion.exito:
                estado = 'completado'
            elif accion.salida_resumen and 'error' in accion.salida_resumen.lower():
                estado = 'fallido'
            else:
                estado = 'en_progreso'
            
            respuesta = {
                'success': True,
                'data': {
                    'accion_ia': accion.to_dict(),
                    'platos_relacionados': platos_data,
                    'estado': estado,
                    'fecha_consulta': datetime.utcnow().isoformat()
                }
            }
            
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error obteniendo estado de análisis {accion_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo obtener el estado del análisis',
            'details': str(e)
        }), 500

@analyze_bp.route('/history/<int:user_id>', methods=['GET'])
def get_analysis_history(user_id: int):
    """
    Obtiene el historial de análisis de un usuario
    
    Endpoint: GET /analyze/history/<user_id>
    
    Query Parameters:
    - limit: Número máximo de análisis a devolver (default: 10)
    - offset: Número de análisis a omitir (default: 0)
    
    Returns:
    {
        "success": true,
        "data": {
            "analisis": [...],
            "total": 25,
            "limit": 10,
            "offset": 0
        }
    }
    """
    try:
        # Obtener parámetros de consulta
        limit = min(int(request.args.get('limit', 10)), 50)  # Máximo 50
        offset = max(int(request.args.get('offset', 0)), 0)
        
        with db_service.get_session() as session:
            from models.acciones_ia import AccionIA
            from models.platos import Plato
            
            # Obtener acciones de análisis del usuario
            acciones = session.query(AccionIA).filter(
                AccionIA.usuario_id == user_id,
                AccionIA.tipo_accion == 'analisis_menu'
            ).order_by(AccionIA.fecha.desc()).offset(offset).limit(limit).all()
            
            # Obtener total de acciones
            total = session.query(AccionIA).filter(
                AccionIA.usuario_id == user_id,
                AccionIA.tipo_accion == 'analisis_menu'
            ).count()
            
            # Preparar datos de respuesta
            analisis_data = []
            for accion in acciones:
                platos = []
                if accion.plato_id:
                    plato = session.query(Plato).filter(Plato.id_plato == accion.plato_id).first()
                    if plato:
                        platos.append(plato.to_dict())
                
                analisis_data.append({
                    'accion_ia': accion.to_dict(),
                    'platos': platos
                })
            
            respuesta = {
                'success': True,
                'data': {
                    'analisis': analisis_data,
                    'total': total,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total
                }
            }
            
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error obteniendo historial de análisis para usuario {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo obtener el historial de análisis',
            'details': str(e)
        }), 500
