"""
Rutas para métricas del sistema - AliMentor AI
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from services.db_service import DatabaseService
from services.metrics_service import MetricsService
from config import Config

logger = logging.getLogger(__name__)

# Crear Blueprint
metrics_bp = Blueprint('metrics', __name__, url_prefix='/metrics')

# Inicializar servicios (se configurarán en app.py)
db_service = None
metrics_service = None

def init_services(db_svc: DatabaseService, metrics_svc: MetricsService):
    """Inicializa los servicios necesarios"""
    global db_service, metrics_service
    db_service = db_svc
    metrics_service = metrics_svc

@metrics_bp.route('', methods=['GET'])
def get_metrics():
    """
    Muestra métricas de auto-mejora entre Run 1 y Run 2
    
    Endpoint: GET /metrics
    
    Query Parameters:
    - period: Período para métricas (7, 30, 90 días) (default: 30)
    - run_comparison: Comparar Run 1 vs Run 2 (true/false) (default: true)
    
    Returns:
    {
        "success": true,
        "data": {
            "metricas_auto_mejora": {
                "run1_metricas": {
                    "precision": 75.5,
                    "satisfaccion": 3.8,
                    "tiempo_respuesta": 2.1
                },
                "run2_metricas": {
                    "precision": 88.2,
                    "satisfaccion": 4.3,
                    "tiempo_respuesta": 1.8
                },
                "mejoras": {
                    "precision_mejora": 12.7,
                    "satisfaccion_mejora": 0.5,
                    "tiempo_mejora": 0.3
                }
            },
            "acciones_ia": {
                "total_acciones": 150,
                "acciones_exitosas": 135,
                "tasa_exito": 90.0
            },
            "mejoras_prompt": {
                "total_mejoras": 8,
                "mejoras_aplicadas": 6,
                "tasa_aplicacion": 75.0
            }
        }
    }
    """
    try:
        period = int(request.args.get('period', 30))
        run_comparison = request.args.get('run_comparison', 'true').lower() == 'true'
        
        # Validar período
        if period not in [7, 30, 90]:
            return jsonify({
                'success': False,
                'error': 'Período inválido',
                'message': 'El período debe ser 7, 30 o 90 días'
            }), 400
        
        # Obtener métricas de auto-mejora (Run 1 vs Run 2)
        metricas_auto_mejora = metrics_service.calcular_metricas_auto_mejora(period)
        
        # Obtener métricas de acciones de IA
        acciones_ia = metrics_service.obtener_metricas_acciones_ia(period)
        
        # Obtener métricas de mejoras de prompt
        mejoras_prompt = metrics_service.obtener_metricas_mejoras_prompt(period)
        
        # Preparar respuesta
        respuesta_data = {
            'metricas_auto_mejora': metricas_auto_mejora,
            'acciones_ia': acciones_ia,
            'mejoras_prompt': mejoras_prompt,
            'periodo_dias': period,
            'run_comparison': run_comparison,
            'fecha_consulta': datetime.utcnow().isoformat()
        }
        
        respuesta = {
            'success': True,
            'data': respuesta_data,
            'message': f'Métricas de auto-mejora obtenidas para los últimos {period} días'
        }
        
        logger.info(f"Métricas de auto-mejora consultadas: período {period} días, comparación Run 1 vs Run 2: {run_comparison}")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener las métricas del sistema',
            'details': str(e)
        }), 500

@metrics_bp.route('/precision', methods=['GET'])
def get_precision_metrics():
    """
    Obtiene métricas de precisión de la IA
    
    Endpoint: GET /metrics/precision
    
    Query Parameters:
    - period: Período en días (default: 30)
    - by_type: Agrupar por tipo de acción (true/false) (default: false)
    
    Returns:
    {
        "success": true,
        "data": {
            "precision_general": 85.5,
            "precision_por_tipo": {...},
            "tendencia": "mejorando",
            "detalles": {...}
        }
    }
    """
    try:
        period = int(request.args.get('period', 30))
        by_type = request.args.get('by_type', 'false').lower() == 'true'
        
        # Obtener métricas de precisión
        precision_data = metrics_service.calcular_precision_ia(period)
        
        if 'error' in precision_data:
            return jsonify({
                'success': False,
                'error': 'Error calculando precisión',
                'message': precision_data['error']
            }), 500
        
        # Preparar respuesta
        respuesta_data = {
            'precision_general': precision_data.get('precision_general', 0),
            'tasa_correccion': precision_data.get('tasa_correccion', 0),
            'total_feedbacks': precision_data.get('total_feedbacks', 0),
            'total_acciones_ia': precision_data.get('total_acciones_ia', 0),
            'periodo_dias': period,
            'fecha_calculo': datetime.utcnow().isoformat()
        }
        
        # Agregar precisión por tipo si se solicita
        if by_type and 'precision_por_tipo' in precision_data:
            respuesta_data['precision_por_tipo'] = precision_data['precision_por_tipo']
        
        # Calcular tendencia
        try:
            # Comparar con período anterior
            precision_anterior = metrics_service.calcular_precision_ia(period * 2)
            precision_actual = precision_data.get('precision_general', 0)
            precision_prev = precision_anterior.get('precision_general', 0)
            
            if precision_actual > precision_prev + 2:
                tendencia = 'mejorando'
            elif precision_actual < precision_prev - 2:
                tendencia = 'empeorando'
            else:
                tendencia = 'estable'
            
            respuesta_data['tendencia'] = tendencia
            respuesta_data['comparacion_anterior'] = {
                'precision_anterior': precision_prev,
                'diferencia': round(precision_actual - precision_prev, 2)
            }
            
        except Exception as e:
            logger.warning(f"Error calculando tendencia de precisión: {e}")
            respuesta_data['tendencia'] = 'desconocida'
        
        respuesta = {
            'success': True,
            'data': respuesta_data
        }
        
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de precisión: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener las métricas de precisión',
            'details': str(e)
        }), 500

@metrics_bp.route('/satisfaction', methods=['GET'])
def get_satisfaction_metrics():
    """
    Obtiene métricas de satisfacción de usuarios
    
    Endpoint: GET /metrics/satisfaction
    
    Query Parameters:
    - period: Período en días (default: 30)
    - by_user: Agrupar por usuario (true/false) (default: false)
    
    Returns:
    {
        "success": true,
        "data": {
            "satisfaccion_promedio": 4.2,
            "distribucion": {...},
            "tendencia": "estable",
            "detalles": {...}
        }
    }
    """
    try:
        period = int(request.args.get('period', 30))
        by_user = request.args.get('by_user', 'false').lower() == 'true'
        
        # Obtener métricas de satisfacción
        satisfaccion_data = metrics_service.calcular_satisfaccion_promedio(period)
        
        if 'error' in satisfaccion_data:
            return jsonify({
                'success': False,
                'error': 'Error calculando satisfacción',
                'message': satisfaccion_data['error']
            }), 500
        
        # Preparar respuesta
        respuesta_data = {
            'satisfaccion_promedio': satisfaccion_data.get('satisfaccion_promedio', 0),
            'mediana': satisfaccion_data.get('mediana', 0),
            'desviacion_estandar': satisfaccion_data.get('desviacion_estandar', 0),
            'total_calificaciones': satisfaccion_data.get('total_calificaciones', 0),
            'distribucion': satisfaccion_data.get('distribucion', {}),
            'tendencia': satisfaccion_data.get('tendencia', 'desconocida'),
            'periodo_dias': period,
            'fecha_calculo': datetime.utcnow().isoformat()
        }
        
        # Agregar análisis por usuario si se solicita
        if by_user:
            try:
                with db_service.get_session() as session:
                    from models.feedback import Feedback
                    from models.usuarios import Usuario
                    
                    # Obtener feedback del período
                    fecha_limite = datetime.utcnow() - timedelta(days=period)
                    feedbacks = session.query(Feedback).filter(
                        Feedback.fecha >= fecha_limite,
                        Feedback.calificacion.isnot(None)
                    ).all()
                    
                    # Agrupar por usuario
                    satisfaccion_por_usuario = {}
                    for feedback in feedbacks:
                        usuario_id = feedback.usuario_id
                        if usuario_id not in satisfaccion_por_usuario:
                            satisfaccion_por_usuario[usuario_id] = []
                        satisfaccion_por_usuario[usuario_id].append(feedback.calificacion)
                    
                    # Calcular métricas por usuario
                    usuarios_data = []
                    for usuario_id, calificaciones in satisfaccion_por_usuario.items():
                        usuario = session.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
                        if usuario:
                            usuarios_data.append({
                                'usuario_id': usuario_id,
                                'nombre': usuario.nombre,
                                'satisfaccion_promedio': sum(calificaciones) / len(calificaciones),
                                'total_calificaciones': len(calificaciones)
                            })
                    
                    respuesta_data['satisfaccion_por_usuario'] = usuarios_data
                    
            except Exception as e:
                logger.warning(f"Error calculando satisfacción por usuario: {e}")
                respuesta_data['error_por_usuario'] = str(e)
        
        respuesta = {
            'success': True,
            'data': respuesta_data
        }
        
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de satisfacción: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener las métricas de satisfacción',
            'details': str(e)
        }), 500

@metrics_bp.route('/improvement', methods=['GET'])
def get_improvement_metrics():
    """
    Obtiene métricas de mejora de la IA
    
    Endpoint: GET /metrics/improvement
    
    Query Parameters:
    - period: Período en días (default: 30)
    - by_confidence: Agrupar por nivel de confianza (true/false) (default: false)
    
    Returns:
    {
        "success": true,
        "data": {
            "tasa_mejora": 75.5,
            "confianza_promedio": 0.82,
            "mejoras_aplicadas": 12,
            "detalles": {...}
        }
    }
    """
    try:
        period = int(request.args.get('period', 30))
        by_confidence = request.args.get('by_confidence', 'false').lower() == 'true'
        
        # Obtener métricas de mejora
        mejora_data = metrics_service.calcular_tasa_mejora_ia(period)
        
        if 'error' in mejora_data:
            return jsonify({
                'success': False,
                'error': 'Error calculando mejora',
                'message': mejora_data['error']
            }), 500
        
        # Preparar respuesta
        respuesta_data = {
            'tasa_mejora': mejora_data.get('tasa_mejora', 0),
            'cobertura_mejora': mejora_data.get('cobertura_mejora', 0),
            'confianza_promedio': mejora_data.get('confianza_promedio', 0),
            'total_acciones': mejora_data.get('total_acciones', 0),
            'total_mejoras': mejora_data.get('total_mejoras', 0),
            'acciones_con_mejoras': mejora_data.get('acciones_con_mejoras', 0),
            'periodo_dias': period,
            'fecha_calculo': datetime.utcnow().isoformat()
        }
        
        # Agrupar por confianza si se solicita
        if by_confidence and 'mejoras_por_tipo' in mejora_data:
            respuesta_data['mejoras_por_tipo'] = mejora_data['mejoras_por_tipo']
        
        respuesta = {
            'success': True,
            'data': respuesta_data
        }
        
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo métricas de mejora: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener las métricas de mejora',
            'details': str(e)
        }), 500

@metrics_bp.route('/report', methods=['GET'])
def get_comprehensive_report():
    """
    Obtiene un reporte completo del sistema
    
    Endpoint: GET /metrics/report
    
    Query Parameters:
    - format: Formato del reporte (json, summary) (default: json)
    
    Returns:
    {
        "success": true,
        "data": {
            "reporte_completo": {...},
            "resumen_ejecutivo": {...},
            "recomendaciones": [...]
        }
    }
    """
    try:
        format_type = request.args.get('format', 'json').lower()
        
        if format_type not in ['json', 'summary']:
            return jsonify({
                'success': False,
                'error': 'Formato inválido',
                'message': 'El formato debe ser "json" o "summary"'
            }), 400
        
        # Generar reporte completo
        reporte_completo = metrics_service.generar_reporte_completo()
        
        if 'error' in reporte_completo:
            return jsonify({
                'success': False,
                'error': 'Error generando reporte',
                'message': reporte_completo['error']
            }), 500
        
        # Preparar respuesta según formato
        if format_type == 'summary':
            # Crear resumen ejecutivo
            resumen = {
                'fecha_generacion': reporte_completo['fecha_generacion'],
                'estado_general': reporte_completo.get('resumen_ejecutivo', {}).get('estado_general', 'desconocido'),
                'puntos_fuertes': reporte_completo.get('resumen_ejecutivo', {}).get('puntos_fuertes', []),
                'areas_mejora': reporte_completo.get('resumen_ejecutivo', {}).get('areas_mejora', []),
                'recomendaciones': reporte_completo.get('resumen_ejecutivo', {}).get('recomendaciones', []),
                'metricas_clave': {
                    'precision_ia': reporte_completo.get('precision_ia_30_dias', {}).get('precision_general', 0),
                    'satisfaccion': reporte_completo.get('satisfaccion_30_dias', {}).get('satisfaccion_promedio', 0),
                    'tasa_mejora': reporte_completo.get('mejora_ia_30_dias', {}).get('tasa_mejora', 0)
                }
            }
            
            respuesta_data = {
                'resumen_ejecutivo': resumen,
                'tipo_reporte': 'summary'
            }
        else:
            respuesta_data = {
                'reporte_completo': reporte_completo,
                'tipo_reporte': 'json'
            }
        
        respuesta = {
            'success': True,
            'data': respuesta_data
        }
        
        logger.info(f"Reporte completo generado en formato {format_type}")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte completo: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudo generar el reporte completo',
            'details': str(e)
        }), 500

@metrics_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    Obtiene datos para dashboard en tiempo real
    
    Endpoint: GET /metrics/dashboard
    
    Returns:
    {
        "success": true,
        "data": {
            "indicadores_clave": {...},
            "graficos": {...},
            "alertas": [...],
            "tendencias": {...}
        }
    }
    """
    try:
        # Obtener métricas básicas
        metricas_generales = metrics_service.calcular_metricas_generales()
        precision_7d = metrics_service.calcular_precision_ia(7)
        satisfaccion_7d = metrics_service.calcular_satisfaccion_promedio(7)
        mejora_7d = metrics_service.calcular_tasa_mejora_ia(7)
        
        # Indicadores clave
        indicadores_clave = {
            'total_usuarios': metricas_generales.get('total_usuarios', 0),
            'total_platos': metricas_generales.get('total_platos', 0),
            'total_feedbacks': metricas_generales.get('total_feedbacks', 0),
            'precision_ia': precision_7d.get('precision_general', 0),
            'satisfaccion_promedio': satisfaccion_7d.get('satisfaccion_promedio', 0),
            'tasa_mejora': mejora_7d.get('tasa_mejora', 0),
            'tasa_exito_acciones': metricas_generales.get('tasa_exito_acciones', 0)
        }
        
        # Datos para gráficos
        graficos = {
            'precision_temporal': {
                '7_dias': precision_7d.get('precision_general', 0),
                '30_dias': metrics_service.calcular_precision_ia(30).get('precision_general', 0)
            },
            'satisfaccion_temporal': {
                '7_dias': satisfaccion_7d.get('satisfaccion_promedio', 0),
                '30_dias': metrics_service.calcular_satisfaccion_promedio(30).get('satisfaccion_promedio', 0)
            },
            'distribucion_calificaciones': satisfaccion_7d.get('distribucion', {}),
            'mejoras_por_confianza': mejora_7d.get('mejoras_por_tipo', {})
        }
        
        # Generar alertas
        alertas = []
        
        if indicadores_clave['precision_ia'] < 70:
            alertas.append({
                'tipo': 'warning',
                'mensaje': 'La precisión de la IA está por debajo del 70%',
                'valor': indicadores_clave['precision_ia']
            })
        
        if indicadores_clave['satisfaccion_promedio'] < 3.0:
            alertas.append({
                'tipo': 'error',
                'mensaje': 'La satisfacción del usuario está por debajo de 3.0',
                'valor': indicadores_clave['satisfaccion_promedio']
            })
        
        if indicadores_clave['tasa_mejora'] < 50:
            alertas.append({
                'tipo': 'info',
                'mensaje': 'La tasa de mejora de la IA es baja',
                'valor': indicadores_clave['tasa_mejora']
            })
        
        # Tendencias
        tendencias = {
            'precision': 'mejorando' if graficos['precision_temporal']['7_dias'] > graficos['precision_temporal']['30_dias'] else 'estable',
            'satisfaccion': 'mejorando' if graficos['satisfaccion_temporal']['7_dias'] > graficos['satisfaccion_temporal']['30_dias'] else 'estable',
            'mejoras': 'activa' if indicadores_clave['tasa_mejora'] > 50 else 'inactiva'
        }
        
        respuesta = {
            'success': True,
            'data': {
                'indicadores_clave': indicadores_clave,
                'graficos': graficos,
                'alertas': alertas,
                'tendencias': tendencias,
                'fecha_actualizacion': datetime.utcnow().isoformat()
            }
        }
        
        logger.info("Datos de dashboard generados exitosamente")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error generando datos de dashboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron generar los datos del dashboard',
            'details': str(e)
        }), 500
