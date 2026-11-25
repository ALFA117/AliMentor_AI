"""
Rutas para mejora de IA - AliMentor AI
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from services.ai_service import AIService
from services.db_service import DatabaseService
from services.feedback_analyzer import FeedbackAnalyzer
from config import Config

logger = logging.getLogger(__name__)

# Crear Blueprint
improve_bp = Blueprint('improve', __name__, url_prefix='/improve')

# Inicializar servicios (se configurarán en app.py)
ai_service = None
db_service = None
feedback_analyzer = None

def init_services(ai_svc: AIService, db_svc: DatabaseService, feedback_anal: FeedbackAnalyzer):
    """Inicializa los servicios necesarios"""
    global ai_service, db_service, feedback_analyzer
    ai_service = ai_svc
    db_service = db_svc
    feedback_analyzer = feedback_anal

@improve_bp.route('', methods=['POST'])
def improve_ai():
    """
    Mejora la IA basándose en feedback reciente
    
    Endpoint: POST /improve
    
    Body (opcional):
    {
        "force_improvement": false,
        "min_feedback_count": 5,
        "days_back": 7
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "mejoras_generadas": [...],
            "feedback_analizado": {...},
            "accion_ia_id": 123
        },
        "message": "Mejoras de IA generadas exitosamente"
    }
    """
    try:
        data = request.get_json() or {}
        
        # Parámetros de configuración
        force_improvement = data.get('force_improvement', False)
        min_feedback_count = data.get('min_feedback_count', Config.MIN_FEEDBACK_FOR_IMPROVEMENT)
        days_back = data.get('days_back', 7)
        
        # Obtener feedback reciente
        feedbacks = db_service.obtener_feedback_reciente(days_back)
        
        if not feedbacks:
            return jsonify({
                'success': False,
                'error': 'No hay feedback suficiente',
                'message': f'No se encontró feedback en los últimos {days_back} días'
            }), 400
        
        # Verificar si hay suficiente feedback para mejorar
        if len(feedbacks) < min_feedback_count and not force_improvement:
            return jsonify({
                'success': False,
                'error': 'Feedback insuficiente',
                'message': f'Se requieren al menos {min_feedback_count} feedbacks para generar mejoras. Encontrados: {len(feedbacks)}'
            }), 400
        
        # Crear acción de IA para tracking
        accion_data = {
            'usuario_id': None,  # Mejora global
            'tipo_accion': 'mejora_prompt',
            'entrada': f"Análisis de {len(feedbacks)} feedbacks para mejora de IA",
            'exito': False
        }
        
        accion_ia = db_service.crear_accion_ia(accion_data)
        if not accion_ia:
            return jsonify({
                'success': False,
                'error': 'Error creando acción de IA',
                'message': 'No se pudo registrar la acción de mejora'
            }), 500
        
        # Analizar feedback para detectar patrones
        feedbacks_dict = [f.to_dict() for f in feedbacks]
        patrones = feedback_analyzer.analizar_patrones_feedback(feedbacks_dict)
        
        if 'error' in patrones:
            db_service.actualizar_accion_ia(accion_ia.id_accion, False, str(patrones['error']))
            return jsonify({
                'success': False,
                'error': 'Error analizando feedback',
                'message': 'No se pudo analizar el feedback para generar mejoras',
                'details': patrones['error']
            }), 500
        
        # Generar mejoras con IA
        mejoras = ai_service.mejorar_prompt_basado_feedback(feedbacks_dict)
        
        if 'error' in mejoras:
            db_service.actualizar_accion_ia(accion_ia.id_accion, False, str(mejoras['error']))
            return jsonify({
                'success': False,
                'error': 'Error generando mejoras',
                'message': 'La IA no pudo generar mejoras basadas en el feedback',
                'details': mejoras['error']
            }), 500
        
        # Guardar mejoras en base de datos
        mejoras_guardadas = []
        confianza = mejoras.get('confianza', 0.5)
        
        mejora_data = {
            'id_accion': accion_ia.id_accion,
            'ajuste_prompt': mejoras.get('ajuste_prompt', ''),
            'observacion': mejoras.get('observacion', 'Mejora generada automáticamente'),
            'confianza': confianza
        }
        
        mejora_guardada = db_service.crear_mejora_ia(mejora_data)
        if mejora_guardada:
            mejoras_guardadas.append(mejora_guardada.to_dict())
        
        # Actualizar acción de IA como exitosa
        resumen_mejora = f"Mejoras generadas: {len(mejoras_guardadas)} mejoras con confianza {confianza:.2f}"
        db_service.actualizar_accion_ia(accion_ia.id_accion, True, resumen_mejora)
        
        # Preparar respuesta
        respuesta = {
            'success': True,
            'data': {
                'mejoras_generadas': mejoras_guardadas,
                'feedback_analizado': {
                    'total_feedbacks': len(feedbacks),
                    'periodo_dias': days_back,
                    'patrones_detectados': patrones
                },
                'accion_ia_id': accion_ia.id_accion,
                'confianza_promedio': confianza,
                'fecha_mejora': datetime.utcnow().isoformat()
            },
            'message': f'Mejoras de IA generadas exitosamente. Confianza: {confianza:.2f}'
        }
        
        logger.info(f"Mejoras de IA generadas: {len(mejoras_guardadas)} mejoras con confianza {confianza:.2f}")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error generando mejoras de IA: {e}")
        
        # Marcar acción como fallida si existe
        if 'accion_ia' in locals() and accion_ia:
            db_service.actualizar_accion_ia(accion_ia.id_accion, False, str(e))
        
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado al generar mejoras de IA',
            'details': str(e)
        }), 500

@improve_bp.route('/status', methods=['GET'])
def get_improvement_status():
    """
    Obtiene el estado de las mejoras de IA
    
    Endpoint: GET /improve/status
    
    Query Parameters:
    - days_back: Días hacia atrás para analizar (default: 30)
    
    Returns:
    {
        "success": true,
        "data": {
            "estado_mejoras": {...},
            "mejoras_recientes": [...],
            "metricas": {...}
        }
    }
    """
    try:
        days_back = int(request.args.get('days_back', 30))
        
        with db_service.get_session() as session:
            from models.acciones_ia import AccionIA
            from models.mejora_ia import MejoraIA
            from models.feedback import Feedback
            
            # Obtener mejoras recientes
            fecha_limite = datetime.utcnow() - timedelta(days=days_back)
            
            mejoras = session.query(MejoraIA).filter(
                MejoraIA.fecha >= fecha_limite
            ).order_by(MejoraIA.fecha.desc()).all()
            
            # Obtener acciones de mejora
            acciones_mejora = session.query(AccionIA).filter(
                AccionIA.tipo_accion == 'mejora_prompt',
                AccionIA.fecha >= fecha_limite
            ).order_by(AccionIA.fecha.desc()).all()
            
            # Obtener feedback reciente
            feedbacks = session.query(Feedback).filter(
                Feedback.fecha >= fecha_limite
            ).all()
            
            # Calcular métricas
            total_mejoras = len(mejoras)
            mejoras_exitosas = sum(1 for m in mejoras if m.es_aplicable())
            confianza_promedio = sum(float(m.confianza) for m in mejoras if m.confianza) / len(mejoras) if mejoras else 0
            
            # Preparar datos de mejoras
            mejoras_data = []
            for mejora in mejoras:
                mejora_dict = mejora.to_dict()
                mejora_dict['aplicable'] = mejora.es_aplicable()
                mejora_dict['nivel_confianza'] = mejora.get_nivel_confianza()
                mejoras_data.append(mejora_dict)
            
            # Estado de mejoras
            estado_mejoras = {
                'total_mejoras': total_mejoras,
                'mejoras_exitosas': mejoras_exitosas,
                'mejoras_aplicables': sum(1 for m in mejoras if m.es_aplicable()),
                'confianza_promedio': round(confianza_promedio, 2),
                'ultima_mejora': mejoras[0].fecha.isoformat() if mejoras else None,
                'periodo_analisis': f"{days_back} días"
            }
            
            # Métricas adicionales
            metricas = {
                'total_feedbacks_analizados': len(feedbacks),
                'total_acciones_mejora': len(acciones_mejora),
                'tasa_exito_mejoras': round((mejoras_exitosas / total_mejoras * 100), 2) if total_mejoras > 0 else 0,
                'mejoras_por_tipo': {}
            }
            
            # Agrupar mejoras por nivel de confianza
            confianzas = [m.get_nivel_confianza() for m in mejoras]
            from collections import Counter
            metricas['mejoras_por_tipo'] = dict(Counter(confianzas))
            
            respuesta = {
                'success': True,
                'data': {
                    'estado_mejoras': estado_mejoras,
                    'mejoras_recientes': mejoras_data,
                    'metricas': metricas,
                    'fecha_consulta': datetime.utcnow().isoformat()
                }
            }
            
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error obteniendo estado de mejoras: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo obtener el estado de las mejoras',
            'details': str(e)
        }), 500

@improve_bp.route('/apply', methods=['POST'])
def apply_improvements():
    """
    Aplica mejoras pendientes a los prompts
    
    Endpoint: POST /improve/apply
    
    Body (opcional):
    {
        "min_confidence": 0.7,
        "mejora_ids": [1, 2, 3]  # IDs específicos de mejoras a aplicar
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "mejoras_aplicadas": [...],
            "prompts_actualizados": [...],
            "resumen": {...}
        }
    }
    """
    try:
        data = request.get_json() or {}
        
        min_confidence = data.get('min_confidence', Config.CONFIDENCE_THRESHOLD)
        mejora_ids = data.get('mejora_ids', [])
        
        with db_service.get_session() as session:
            from models.mejora_ia import MejoraIA
            
            # Obtener mejoras a aplicar
            if mejora_ids:
                # Aplicar mejoras específicas
                mejoras = session.query(MejoraIA).filter(
                    MejoraIA.id_mejora.in_(mejora_ids)
                ).all()
            else:
                # Aplicar mejoras con confianza suficiente
                mejoras = session.query(MejoraIA).filter(
                    MejoraIA.confianza >= min_confidence,
                    MejoraIA.confianza.isnot(None)
                ).order_by(MejoraIA.confianza.desc()).all()
            
            if not mejoras:
                return jsonify({
                    'success': False,
                    'error': 'No hay mejoras para aplicar',
                    'message': f'No se encontraron mejoras con confianza >= {min_confidence}'
                }), 400
            
            # Aplicar mejoras
            mejoras_aplicadas = []
            prompts_actualizados = []
            
            for mejora in mejoras:
                try:
                    # Aquí se aplicaría la mejora al sistema de prompts
                    # Por ahora, solo registramos que se aplicó
                    
                    mejora_dict = mejora.to_dict()
                    mejora_dict['aplicada'] = True
                    mejora_dict['fecha_aplicacion'] = datetime.utcnow().isoformat()
                    mejoras_aplicadas.append(mejora_dict)
                    
                    # Simular actualización de prompt
                    prompt_actualizado = {
                        'tipo': 'analisis_menu',
                        'mejora_id': mejora.id_mejora,
                        'ajuste_aplicado': mejora.ajuste_prompt[:100] + '...' if len(mejora.ajuste_prompt) > 100 else mejora.ajuste_prompt,
                        'confianza': float(mejora.confianza) if mejora.confianza else 0.0
                    }
                    prompts_actualizados.append(prompt_actualizado)
                    
                except Exception as e:
                    logger.warning(f"Error aplicando mejora {mejora.id_mejora}: {e}")
                    continue
            
            # Resumen
            resumen = {
                'total_mejoras_encontradas': len(mejoras),
                'mejoras_aplicadas': len(mejoras_aplicadas),
                'mejoras_fallidas': len(mejoras) - len(mejoras_aplicadas),
                'confianza_minima': min_confidence,
                'fecha_aplicacion': datetime.utcnow().isoformat()
            }
            
            respuesta = {
                'success': True,
                'data': {
                    'mejoras_aplicadas': mejoras_aplicadas,
                    'prompts_actualizados': prompts_actualizados,
                    'resumen': resumen
                },
                'message': f'Se aplicaron {len(mejoras_aplicadas)} mejoras exitosamente'
            }
            
            logger.info(f"Mejoras aplicadas: {len(mejoras_aplicadas)} de {len(mejoras)} mejoras")
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error aplicando mejoras: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron aplicar las mejoras',
            'details': str(e)
        }), 500

@improve_bp.route('/history', methods=['GET'])
def get_improvement_history():
    """
    Obtiene el historial de mejoras de IA
    
    Endpoint: GET /improve/history
    
    Query Parameters:
    - limit: Número máximo de mejoras (default: 20)
    - offset: Número de mejoras a omitir (default: 0)
    - min_confidence: Confianza mínima (opcional)
    
    Returns:
    {
        "success": true,
        "data": {
            "mejoras": [...],
            "total": 15,
            "estadisticas": {...}
        }
    }
    """
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
        min_confidence = request.args.get('min_confidence')
        
        with db_service.get_session() as session:
            from models.mejora_ia import MejoraIA
            from models.acciones_ia import AccionIA
            
            # Construir consulta
            query = session.query(MejoraIA)
            
            if min_confidence:
                try:
                    min_conf = float(min_confidence)
                    query = query.filter(MejoraIA.confianza >= min_conf)
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'Confianza mínima inválida',
                        'message': 'La confianza mínima debe ser un número válido'
                    }), 400
            
            # Obtener mejoras
            mejoras = query.order_by(MejoraIA.fecha.desc()).offset(offset).limit(limit).all()
            total = query.count()
            
            # Preparar datos
            mejoras_data = []
            for mejora in mejoras:
                # Obtener acción relacionada
                accion = session.query(AccionIA).filter(AccionIA.id_accion == mejora.id_accion).first()
                
                mejora_dict = mejora.to_dict()
                mejora_dict['accion_relacionada'] = accion.to_dict() if accion else None
                mejora_dict['aplicable'] = mejora.es_aplicable()
                mejora_dict['nivel_confianza'] = mejora.get_nivel_confianza()
                mejoras_data.append(mejora_dict)
            
            # Calcular estadísticas
            todas_mejoras = session.query(MejoraIA).all()
            estadisticas = {
                'total_mejoras': len(todas_mejoras),
                'mejoras_alta_confianza': sum(1 for m in todas_mejoras if m.es_alta_confianza()),
                'mejoras_media_confianza': sum(1 for m in todas_mejoras if m.es_media_confianza()),
                'mejoras_baja_confianza': sum(1 for m in todas_mejoras if m.es_baja_confianza()),
                'confianza_promedio': sum(float(m.confianza) for m in todas_mejoras if m.confianza) / len(todas_mejoras) if todas_mejoras else 0
            }
            
            respuesta = {
                'success': True,
                'data': {
                    'mejoras': mejoras_data,
                    'total': total,
                    'estadisticas': estadisticas,
                    'fecha_consulta': datetime.utcnow().isoformat()
                }
            }
            
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error obteniendo historial de mejoras: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo obtener el historial de mejoras',
            'details': str(e)
        }), 500

@improve_bp.route('/analyze-errors', methods=['POST'])
def analyze_errors():
    """
    Analiza errores específicos de la IA para generar mejoras dirigidas
    
    Endpoint: POST /improve/analyze-errors
    
    Body:
    {
        "error_types": ["ingrediente_no_detectado", "alergeno_no_detectado"],
        "days_back": 14
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "errores_detectados": [...],
            "mejoras_sugeridas": [...],
            "accion_ia_id": 123
        }
    }
    """
    try:
        data = request.get_json() or {}
        
        error_types = data.get('error_types', [])
        days_back = data.get('days_back', 14)
        
        # Obtener feedback reciente
        feedbacks = db_service.obtener_feedback_reciente(days_back)
        
        if not feedbacks:
            return jsonify({
                'success': False,
                'error': 'No hay feedback suficiente',
                'message': f'No se encontró feedback en los últimos {days_back} días'
            }), 400
        
        # Crear acción de IA
        accion_data = {
            'usuario_id': None,
            'tipo_accion': 'analisis_errores',
            'entrada': f"Análisis de errores específicos: {', '.join(error_types)}",
            'exito': False
        }
        
        accion_ia = db_service.crear_accion_ia(accion_data)
        if not accion_ia:
            return jsonify({
                'success': False,
                'error': 'Error creando acción de IA',
                'message': 'No se pudo registrar la acción de análisis'
            }), 500
        
        # Detectar errores específicos
        feedbacks_dict = [f.to_dict() for f in feedbacks]
        errores_detectados = feedback_analyzer.detectar_errores_ia(feedbacks_dict)
        
        # Filtrar por tipos de error solicitados
        if error_types:
            errores_filtrados = [e for e in errores_detectados if e.get('tipo') in error_types]
        else:
            errores_filtrados = errores_detectados
        
        # Generar mejoras específicas para los errores
        mejoras_sugeridas = []
        
        for error in errores_filtrados:
            try:
                # Generar mejora específica para este tipo de error
                mejora_especifica = {
                    'tipo_error': error.get('tipo'),
                    'descripcion': error.get('descripcion'),
                    'frecuencia': sum(1 for e in errores_filtrados if e.get('tipo') == error.get('tipo')),
                    'mejora_sugerida': generar_mejora_especifica(error.get('tipo')),
                    'prioridad': calcular_prioridad_error(error, errores_filtrados)
                }
                mejoras_sugeridas.append(mejora_especifica)
                
            except Exception as e:
                logger.warning(f"Error generando mejora para error {error.get('tipo')}: {e}")
                continue
        
        # Actualizar acción como exitosa
        resumen_analisis = f"Análisis de errores completado: {len(errores_filtrados)} errores, {len(mejoras_sugeridas)} mejoras"
        db_service.actualizar_accion_ia(accion_ia.id_accion, True, resumen_analisis)
        
        respuesta = {
            'success': True,
            'data': {
                'errores_detectados': errores_filtrados,
                'mejoras_sugeridas': mejoras_sugeridas,
                'accion_ia_id': accion_ia.id_accion,
                'total_errores': len(errores_filtrados),
                'total_mejoras': len(mejoras_sugeridas),
                'fecha_analisis': datetime.utcnow().isoformat()
            },
            'message': f'Análisis de errores completado: {len(errores_filtrados)} errores detectados'
        }
        
        logger.info(f"Análisis de errores completado: {len(errores_filtrados)} errores, {len(mejoras_sugeridas)} mejoras")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error analizando errores: {e}")
        
        if 'accion_ia' in locals() and accion_ia:
            db_service.actualizar_accion_ia(accion_ia.id_accion, False, str(e))
        
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo analizar los errores',
            'details': str(e)
        }), 500

def generar_mejora_especifica(tipo_error: str) -> str:
    """Genera una mejora específica para un tipo de error"""
    mejoras_especificas = {
        'ingrediente_no_detectado': 'Mejorar la detección de ingredientes incluyendo sinónimos y variaciones comunes',
        'alergeno_no_detectado': 'Ampliar la lista de alérgenos y mejorar la detección de alérgenos ocultos',
        'categoria_incorrecta': 'Refinar los criterios de clasificación de categorías de platos',
        'precio_incorrecto': 'Mejorar la estimación de precios basándose en datos de mercado actuales'
    }
    
    return mejoras_especificas.get(tipo_error, 'Revisar y mejorar el área específica del error detectado')

def calcular_prioridad_error(error: Dict[str, Any], todos_errores: List[Dict[str, Any]]) -> str:
    """Calcula la prioridad de un error basándose en su frecuencia"""
    tipo = error.get('tipo')
    frecuencia = sum(1 for e in todos_errores if e.get('tipo') == tipo)
    
    if frecuencia >= 5:
        return 'alta'
    elif frecuencia >= 3:
        return 'media'
    else:
        return 'baja'
