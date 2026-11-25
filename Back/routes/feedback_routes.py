"""
Rutas para feedback de usuarios - AliMentor AI
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from services.db_service import DatabaseService
from services.feedback_analyzer import FeedbackAnalyzer
from config import Config

logger = logging.getLogger(__name__)

# Crear Blueprint
feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

# Inicializar servicios (se configurarán en app.py)
db_service = None
feedback_analyzer = None

def init_services(db_svc: DatabaseService, feedback_anal: FeedbackAnalyzer):
    """Inicializa los servicios necesarios"""
    global db_service, feedback_analyzer
    db_service = db_svc
    feedback_analyzer = feedback_anal

@feedback_bp.route('', methods=['POST'])
def create_feedback():
    """
    Registra feedback del usuario y activa ciclo de mejora
    
    Endpoint: POST /feedback
    
    Body:
    {
        "id_usuario": 1,
        "id_plato": 2,
        "comentarios": "El análisis fue muy preciso, detectó correctamente los ingredientes",
        "calificacion": 4
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "feedback": {
                "id_feedback": 1,
                "id_usuario": 1,
                "id_plato": 2,
                "comentarios": "...",
                "calificacion": 4,
                "fecha": "2024-01-15T10:00:00Z"
            },
            "mejora_activada": true,
            "accion_mejora_id": 123
        },
        "message": "Feedback registrado y ciclo de mejora activado"
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
        
        # Validar campos requeridos
        id_usuario = data.get('id_usuario')
        id_plato = data.get('id_plato')
        comentarios = data.get('comentarios', '').strip()
        calificacion = data.get('calificacion')
        
        if not id_usuario:
            return jsonify({
                'success': False,
                'error': 'ID de usuario requerido',
                'message': 'El campo id_usuario es obligatorio'
            }), 400
        
        if not id_plato:
            return jsonify({
                'success': False,
                'error': 'ID de plato requerido',
                'message': 'El campo id_plato es obligatorio'
            }), 400
        
        # Validar que el usuario existe
        usuario = db_service.obtener_usuario(id_usuario)
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'message': f'No se encontró el usuario con ID {id_usuario}'
            }), 404
        
        # Validar que el plato existe
        plato = db_service.obtener_plato(id_plato)
        if not plato:
            return jsonify({
                'success': False,
                'error': 'Plato no encontrado',
                'message': f'No se encontró el plato con ID {id_plato}'
            }), 404
        
        # Validar calificación si se proporciona
        if calificacion is not None:
            try:
                calificacion = int(calificacion)
                if not (1 <= calificacion <= 5):
                    return jsonify({
                        'success': False,
                        'error': 'Calificación inválida',
                        'message': 'La calificación debe estar entre 1 y 5'
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': 'Calificación inválida',
                    'message': 'La calificación debe ser un número entero'
                }), 400
        
        # Validar que hay comentarios o calificación
        if not comentarios and calificacion is None:
            return jsonify({
                'success': False,
                'error': 'Comentarios o calificación requeridos',
                'message': 'Debe proporcionar al menos comentarios o una calificación'
            }), 400
        
        # Crear feedback
        feedback_data = {
            'usuario_id': id_usuario,
            'plato_id': id_plato,
            'comentarios': comentarios,
            'calificacion': calificacion
        }
        
        feedback = db_service.crear_feedback(feedback_data)
        if not feedback:
            return jsonify({
                'success': False,
                'error': 'Error creando feedback',
                'message': 'No se pudo crear el feedback'
            }), 500
        
        # Activar ciclo de mejora automática
        mejora_activada = False
        accion_mejora_id = None
        
        try:
            # Verificar si hay suficiente feedback para activar mejora
            feedbacks_recientes = db_service.obtener_feedback_reciente(7)  # Últimos 7 días
            if len(feedbacks_recientes) >= 5:  # Mínimo 5 feedbacks
                # Activar auto-mejora
                accion_mejora = _activar_auto_mejora(feedbacks_recientes)
                if accion_mejora:
                    mejora_activada = True
                    accion_mejora_id = accion_mejora.id_accion
                    logger.info(f"Ciclo de mejora activado: Acción ID {accion_mejora_id}")
        except Exception as e:
            logger.warning(f"Error activando auto-mejora: {e}")
        
        # Preparar respuesta
        respuesta = {
            'success': True,
            'data': {
                'feedback': feedback.to_dict(),
                'mejora_activada': mejora_activada,
                'accion_mejora_id': accion_mejora_id,
                'fecha_creacion': datetime.utcnow().isoformat()
            },
            'message': 'Feedback registrado exitosamente' + (' y ciclo de mejora activado' if mejora_activada else '')
        }
        
        logger.info(f"Feedback creado: ID {feedback.id_feedback} para plato {id_plato} por usuario {id_usuario}")
        return jsonify(respuesta), 201
        
    except Exception as e:
        logger.error(f"Error creando feedback: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado al crear el feedback',
            'details': str(e)
        }), 500

def _activar_auto_mejora(feedbacks: List) -> Optional[Any]:
    """
    Activa el ciclo de auto-mejora basándose en feedback acumulado
    
    Args:
        feedbacks: Lista de feedbacks recientes
        
    Returns:
        Acción de mejora creada o None
    """
    try:
        from services.ai_service import AIService
        
        # Crear acción de mejora
        accion_data = {
            'tipo_accion': 'mejora_prompt',
            'usuario_id': None,  # Mejora global
            'entrada': f"Análisis de {len(feedbacks)} feedbacks para mejora automática",
            'exito': False
        }
        
        accion_mejora = db_service.crear_accion_ia(accion_data)
        if not accion_mejora:
            return None
        
        # Analizar feedback para detectar patrones
        feedbacks_dict = [f.to_dict() for f in feedbacks]
        patrones = feedback_analyzer.analizar_patrones_feedback(feedbacks_dict)
        
        if 'error' in patrones:
            db_service.actualizar_accion_ia(accion_mejora.id_accion, False, str(patrones['error']))
            return None
        
        # Generar mejora de prompt con IA
        ai_service = AIService(db_service.config.get('OPENAI_API_KEY'))
        mejoras = ai_service.mejorar_prompt_basado_feedback(feedbacks_dict)
        
        if 'error' in mejoras:
            db_service.actualizar_accion_ia(accion_mejora.id_accion, False, str(mejoras['error']))
            return None
        
        # Guardar mejora de prompt
        mejora_data = {
            'id_accion': accion_mejora.id_accion,
            'prompt_nuevo': mejoras.get('ajuste_prompt', '')
        }
        
        mejora_guardada = db_service.crear_mejora_prompt(mejora_data)
        if mejora_guardada:
            # Actualizar acción como exitosa
            resumen = f"Mejora de prompt generada: {mejora_guardada.id_mejora}"
            db_service.actualizar_accion_ia(accion_mejora.id_accion, True, resumen)
            return accion_mejora
        
        return None
        
    except Exception as e:
        logger.error(f"Error en auto-mejora: {e}")
        return None

@feedback_bp.route('/<int:feedback_id>', methods=['GET'])
def get_feedback(feedback_id: int):
    """
    Obtiene un feedback específico por ID
    
    Endpoint: GET /feedback/<feedback_id>
    
    Returns:
    {
        "success": true,
        "data": {
            "feedback": {...},
            "usuario": {...},
            "plato": {...}
        }
    }
    """
    try:
        with db_service.get_session() as session:
            from models.feedback import Feedback
            from models.usuarios import Usuario
            from models.platos import Plato
            
            # Obtener feedback con relaciones
            feedback = session.query(Feedback).filter(Feedback.id_feedback == feedback_id).first()
            if not feedback:
                return jsonify({
                    'success': False,
                    'error': 'Feedback no encontrado',
                    'message': f'No se encontró el feedback con ID {feedback_id}'
                }), 404
            
            # Obtener datos relacionados
            usuario = session.query(Usuario).filter(Usuario.id_usuario == feedback.usuario_id).first()
            plato = session.query(Plato).filter(Plato.id_plato == feedback.plato_id).first()
            
            respuesta = {
                'success': True,
                'data': {
                    'feedback': feedback.to_dict(),
                    'usuario': usuario.to_dict() if usuario else None,
                    'plato': plato.to_dict() if plato else None,
                    'fecha_consulta': datetime.utcnow().isoformat()
                }
            }
            
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error obteniendo feedback {feedback_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo obtener el feedback',
            'details': str(e)
        }), 500

@feedback_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_feedback(user_id: int):
    """
    Obtiene todos los feedbacks de un usuario
    
    Endpoint: GET /feedback/user/<user_id>
    
    Query Parameters:
    - limit: Número máximo de feedbacks (default: 20)
    - offset: Número de feedbacks a omitir (default: 0)
    - tipo: Filtrar por tipo de feedback (opcional)
    
    Returns:
    {
        "success": true,
        "data": {
            "feedbacks": [...],
            "usuario": {...},
            "total": 15,
            "resumen": {...}
        }
    }
    """
    try:
        # Obtener parámetros de consulta
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
        tipo_filtro = request.args.get('tipo')
        
        # Validar tipo de feedback si se proporciona
        if tipo_filtro:
            tipos_validos = ['positivo', 'negativo', 'correccion']
            if tipo_filtro not in tipos_validos:
                return jsonify({
                    'success': False,
                    'error': 'Tipo de feedback inválido',
                    'message': f'El tipo debe ser uno de: {", ".join(tipos_validos)}'
                }), 400
        
        # Verificar que el usuario existe
        usuario = db_service.obtener_usuario(user_id)
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'message': f'No se encontró el usuario con ID {user_id}'
            }), 404
        
        with db_service.get_session() as session:
            from models.feedback import Feedback
            from models.platos import Plato
            
            # Construir consulta
            query = session.query(Feedback).filter(Feedback.usuario_id == user_id)
            
            if tipo_filtro:
                query = query.filter(Feedback.tipo_feedback == tipo_filtro)
            
            # Obtener feedbacks
            feedbacks = query.order_by(Feedback.fecha.desc()).offset(offset).limit(limit).all()
            
            # Obtener total
            total_query = session.query(Feedback).filter(Feedback.usuario_id == user_id)
            if tipo_filtro:
                total_query = total_query.filter(Feedback.tipo_feedback == tipo_filtro)
            total = total_query.count()
            
            # Preparar datos de respuesta
            feedbacks_data = []
            for feedback in feedbacks:
                plato = session.query(Plato).filter(Plato.id_plato == feedback.plato_id).first()
                feedback_dict = feedback.to_dict()
                feedback_dict['plato'] = plato.to_dict() if plato else None
                feedbacks_data.append(feedback_dict)
            
            # Crear resumen
            resumen = {
                'total_feedbacks': total,
                'tipo_filtro': tipo_filtro,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            }
            
            # Agregar estadísticas si no hay filtro
            if not tipo_filtro:
                todos_feedbacks = session.query(Feedback).filter(Feedback.usuario_id == user_id).all()
                tipos_count = {}
                calificaciones = []
                
                for fb in todos_feedbacks:
                    tipo = fb.tipo_feedback.value if fb.tipo_feedback else 'desconocido'
                    tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
                    
                    if fb.calificacion:
                        calificaciones.append(fb.calificacion)
                
                resumen['estadisticas'] = {
                    'por_tipo': tipos_count,
                    'calificacion_promedio': sum(calificaciones) / len(calificaciones) if calificaciones else 0,
                    'total_calificaciones': len(calificaciones)
                }
            
            respuesta = {
                'success': True,
                'data': {
                    'feedbacks': feedbacks_data,
                    'usuario': usuario.to_dict(),
                    'total': total,
                    'resumen': resumen,
                    'fecha_consulta': datetime.utcnow().isoformat()
                }
            }
            
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error obteniendo feedbacks del usuario {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener los feedbacks del usuario',
            'details': str(e)
        }), 500

@feedback_bp.route('/plate/<int:plato_id>', methods=['GET'])
def get_plate_feedback(plato_id: int):
    """
    Obtiene todos los feedbacks de un plato específico
    
    Endpoint: GET /feedback/plate/<plato_id>
    
    Query Parameters:
    - limit: Número máximo de feedbacks (default: 20)
    - offset: Número de feedbacks a omitir (default: 0)
    
    Returns:
    {
        "success": true,
        "data": {
            "feedbacks": [...],
            "plato": {...},
            "total": 8,
            "estadisticas": {...}
        }
    }
    """
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
        
        # Verificar que el plato existe
        plato = db_service.obtener_plato(plato_id)
        if not plato:
            return jsonify({
                'success': False,
                'error': 'Plato no encontrado',
                'message': f'No se encontró el plato con ID {plato_id}'
            }), 404
        
        with db_service.get_session() as session:
            from models.feedback import Feedback
            from models.usuarios import Usuario
            
            # Obtener feedbacks del plato
            feedbacks = session.query(Feedback).filter(
                Feedback.plato_id == plato_id
            ).order_by(Feedback.fecha.desc()).offset(offset).limit(limit).all()
            
            # Obtener total
            total = session.query(Feedback).filter(Feedback.plato_id == plato_id).count()
            
            # Preparar datos de respuesta
            feedbacks_data = []
            calificaciones = []
            tipos_count = {}
            
            for feedback in feedbacks:
                usuario = session.query(Usuario).filter(Usuario.id_usuario == feedback.usuario_id).first()
                feedback_dict = feedback.to_dict()
                feedback_dict['usuario'] = usuario.to_dict() if usuario else None
                feedbacks_data.append(feedback_dict)
                
                # Recopilar estadísticas
                if feedback.calificacion:
                    calificaciones.append(feedback.calificacion)
                
                tipo = feedback.tipo_feedback.value if feedback.tipo_feedback else 'desconocido'
                tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
            
            # Calcular estadísticas
            estadisticas = {
                'total_feedbacks': total,
                'por_tipo': tipos_count,
                'calificacion_promedio': sum(calificaciones) / len(calificaciones) if calificaciones else 0,
                'total_calificaciones': len(calificaciones),
                'calificacion_mas_frecuente': max(set(calificaciones), key=calificaciones.count) if calificaciones else None
            }
            
            respuesta = {
                'success': True,
                'data': {
                    'feedbacks': feedbacks_data,
                    'plato': plato.to_dict(),
                    'total': total,
                    'estadisticas': estadisticas,
                    'fecha_consulta': datetime.utcnow().isoformat()
                }
            }
            
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error obteniendo feedbacks del plato {plato_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener los feedbacks del plato',
            'details': str(e)
        }), 500

@feedback_bp.route('/recent', methods=['GET'])
def get_recent_feedback():
    """
    Obtiene feedbacks recientes del sistema
    
    Endpoint: GET /feedback/recent
    
    Query Parameters:
    - days: Número de días hacia atrás (default: 7)
    - limit: Número máximo de feedbacks (default: 50)
    
    Returns:
    {
        "success": true,
        "data": {
            "feedbacks": [...],
            "periodo": {...},
            "estadisticas": {...}
        }
    }
    """
    try:
        days = int(request.args.get('days', 7))
        limit = min(int(request.args.get('limit', 50)), 200)
        
        # Obtener feedbacks recientes
        feedbacks = db_service.obtener_feedback_reciente(days)
        
        # Limitar resultados
        feedbacks_limite = feedbacks[:limit]
        
        # Preparar datos de respuesta
        feedbacks_data = []
        calificaciones = []
        tipos_count = {}
        
        with db_service.get_session() as session:
            from models.usuarios import Usuario
            from models.platos import Plato
            
            for feedback in feedbacks_limite:
                usuario = session.query(Usuario).filter(Usuario.id_usuario == feedback.usuario_id).first()
                plato = session.query(Plato).filter(Plato.id_plato == feedback.plato_id).first()
                
                feedback_dict = feedback.to_dict()
                feedback_dict['usuario'] = usuario.to_dict() if usuario else None
                feedback_dict['plato'] = plato.to_dict() if plato else None
                feedbacks_data.append(feedback_dict)
                
                # Recopilar estadísticas
                if feedback.calificacion:
                    calificaciones.append(feedback.calificacion)
                
                tipo = feedback.tipo_feedback.value if feedback.tipo_feedback else 'desconocido'
                tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
        
        # Calcular estadísticas
        estadisticas = {
            'total_feedbacks': len(feedbacks),
            'por_tipo': tipos_count,
            'calificacion_promedio': sum(calificaciones) / len(calificaciones) if calificaciones else 0,
            'total_calificaciones': len(calificaciones)
        }
        
        # Analizar patrones si hay suficientes feedbacks
        analisis_patrones = None
        if len(feedbacks) >= 5:
            try:
                feedbacks_dict = [f.to_dict() for f in feedbacks_limite]
                analisis_patrones = feedback_analyzer.analizar_patrones_feedback(feedbacks_dict)
            except Exception as e:
                logger.warning(f"Error analizando patrones de feedback: {e}")
        
        respuesta = {
            'success': True,
            'data': {
                'feedbacks': feedbacks_data,
                'periodo': {
                    'dias': days,
                    'fecha_inicio': (datetime.utcnow() - timedelta(days=days)).isoformat(),
                    'fecha_fin': datetime.utcnow().isoformat()
                },
                'estadisticas': estadisticas,
                'analisis_patrones': analisis_patrones,
                'fecha_consulta': datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Feedbacks recientes obtenidos: {len(feedbacks_data)} feedbacks de los últimos {days} días")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo feedbacks recientes: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener los feedbacks recientes',
            'details': str(e)
        }), 500

@feedback_bp.route('/<int:feedback_id>', methods=['PUT'])
def update_feedback(feedback_id: int):
    """
    Actualiza un feedback existente
    
    Endpoint: PUT /feedback/<feedback_id>
    
    Body:
    {
        "comentario": "Comentario actualizado",
        "calificacion": 5,
        "tipo_feedback": "positivo"
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "feedback": {...}
        },
        "message": "Feedback actualizado exitosamente"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos JSON',
                'message': 'El cuerpo de la petición debe contener datos JSON válidos'
            }), 400
        
        with db_service.get_session() as session:
            from models.feedback import Feedback
            
            # Obtener feedback
            feedback = session.query(Feedback).filter(Feedback.id_feedback == feedback_id).first()
            if not feedback:
                return jsonify({
                    'success': False,
                    'error': 'Feedback no encontrado',
                    'message': f'No se encontró el feedback con ID {feedback_id}'
                }), 404
            
            # Actualizar campos permitidos
            campos_actualizables = ['comentario', 'calificacion', 'tipo_feedback']
            actualizaciones = {}
            
            for campo in campos_actualizables:
                if campo in data:
                    valor = data[campo]
                    
                    # Validaciones específicas
                    if campo == 'calificacion' and valor is not None:
                        try:
                            valor = int(valor)
                            if not (1 <= valor <= 5):
                                return jsonify({
                                    'success': False,
                                    'error': 'Calificación inválida',
                                    'message': 'La calificación debe estar entre 1 y 5'
                                }), 400
                        except (ValueError, TypeError):
                            return jsonify({
                                'success': False,
                                'error': 'Calificación inválida',
                                'message': 'La calificación debe ser un número entero'
                            }), 400
                    
                    elif campo == 'tipo_feedback' and valor:
                        tipos_validos = ['positivo', 'negativo', 'correccion']
                        if valor not in tipos_validos:
                            return jsonify({
                                'success': False,
                                'error': 'Tipo de feedback inválido',
                                'message': f'El tipo_feedback debe ser uno de: {", ".join(tipos_validos)}'
                            }), 400
                    
                    actualizaciones[campo] = valor
            
            # Aplicar actualizaciones
            for campo, valor in actualizaciones.items():
                setattr(feedback, campo, valor)
            
            session.commit()
            
            respuesta = {
                'success': True,
                'data': {
                    'feedback': feedback.to_dict()
                },
                'message': 'Feedback actualizado exitosamente'
            }
            
            logger.info(f"Feedback {feedback_id} actualizado exitosamente")
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error actualizando feedback {feedback_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo actualizar el feedback',
            'details': str(e)
        }), 500

@feedback_bp.route('/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id: int):
    """
    Elimina un feedback
    
    Endpoint: DELETE /feedback/<feedback_id>
    
    Returns:
    {
        "success": true,
        "message": "Feedback eliminado exitosamente"
    }
    """
    try:
        with db_service.get_session() as session:
            from models.feedback import Feedback
            
            # Obtener feedback
            feedback = session.query(Feedback).filter(Feedback.id_feedback == feedback_id).first()
            if not feedback:
                return jsonify({
                    'success': False,
                    'error': 'Feedback no encontrado',
                    'message': f'No se encontró el feedback con ID {feedback_id}'
                }), 404
            
            # Eliminar feedback
            session.delete(feedback)
            session.commit()
            
            respuesta = {
                'success': True,
                'message': 'Feedback eliminado exitosamente'
            }
            
            logger.info(f"Feedback {feedback_id} eliminado exitosamente")
            return jsonify(respuesta), 200
            
    except Exception as e:
        logger.error(f"Error eliminando feedback {feedback_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo eliminar el feedback',
            'details': str(e)
        }), 500
