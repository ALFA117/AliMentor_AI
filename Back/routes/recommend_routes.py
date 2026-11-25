"""
Rutas para recomendaciones - AliMentor AI
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from typing import Dict, Any, List

from services.ai_service import AIService
from services.db_service import DatabaseService
from utils.data_cleaner import DataCleaner
from config import Config

logger = logging.getLogger(__name__)

# Crear Blueprint
recommend_bp = Blueprint('recommend', __name__, url_prefix='/recommend')

# Inicializar servicios (se configurarán en app.py)
ai_service = None
db_service = None
data_cleaner = None

def init_services(ai_svc: AIService, db_svc: DatabaseService, data_cln: DataCleaner):
    """Inicializa los servicios necesarios"""
    global ai_service, db_service, data_cleaner
    ai_service = ai_svc
    db_service = db_svc
    data_cleaner = data_cln

@recommend_bp.route('', methods=['POST'])
def get_recommendations():
    """
    Obtiene recomendaciones personalizadas basadas en perfil del usuario
    
    Endpoint: POST /recommend
    
    Body:
    {
        "id_usuario": 1,
        "criterios": {
            "categoria": "plato_principal",
            "max_precio": 20.00,
            "limit": 10
        }
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "recomendaciones": [
                {
                    "id_plato": 1,
                    "nombre": "Pollo a la parrilla",
                    "descripcion": "Pechuga de pollo con vegetales",
                    "categoria": "plato_principal",
                    "nivel_seguridad": "🟢",
                    "razon_recomendacion": "Sin alérgenos para tu perfil"
                }
            ],
            "total_encontrados": 5,
            "perfil_usuario": {...}
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
        
        id_usuario = data.get('id_usuario')
        criterios = data.get('criterios', {})
        
        if not id_usuario:
            return jsonify({
                'success': False,
                'error': 'ID de usuario requerido',
                'message': 'El campo id_usuario es obligatorio'
            }), 400
        
        # Obtener usuario y perfil
        usuario = db_service.obtener_usuario(id_usuario)
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'message': f'No se encontró el usuario con ID {id_usuario}'
            }), 404
        
        # Obtener criterios de búsqueda
        categoria = criterios.get('categoria')
        max_precio = criterios.get('max_precio')
        limit = min(criterios.get('limit', 10), 50)
        
        # Obtener platos recomendados basados en restricciones del usuario
        restricciones = usuario.get_restricciones_completas()
        platos_recomendados = db_service.obtener_platos_recomendados(id_usuario)
        
        # Aplicar filtros
        platos_filtrados = platos_recomendados
        
        if categoria:
            platos_filtrados = [p for p in platos_filtrados if p.categoria == categoria]
        
        # Limitar resultados
        platos_finales = platos_filtrados[:limit]
        
        # Generar recomendaciones con IA
        recomendaciones_data = []
        for plato in platos_finales:
            try:
                # Analizar compatibilidad con IA
                analisis = ai_service.analizar_compatibilidad_platillo(
                    plato.to_dict(), 
                    restricciones
                )
                
                # Determinar nivel de seguridad
                nivel_seguridad = "🟢"  # Verde por defecto
                razon = "Plato seguro para tu perfil"
                
                if analisis.get('ingredientes_peligrosos'):
                    if len(analisis['ingredientes_peligrosos']) == 1:
                        nivel_seguridad = "🟡"
                        razon = f"Contiene {analisis['ingredientes_peligrosos'][0]}"
                    else:
                        nivel_seguridad = "🔴"
                    razon = f"Contiene múltiples alérgenos: {', '.join(analisis['ingredientes_peligrosos'])}"
                
                recomendaciones_data.append({
                    'id_plato': plato.id_plato,
                    'nombre': plato.nombre,
                    'descripcion': plato.descripcion,
                    'categoria': plato.categoria,
                    'imagen_url': plato.imagen_url,
                    'nivel_seguridad': nivel_seguridad,
                    'razon_recomendacion': razon,
                    'detalles_analisis': analisis
                })
                
            except Exception as e:
                logger.warning(f"Error analizando plato {plato.id_plato}: {e}")
                continue
        
        # Preparar respuesta
        respuesta = {
            'success': True,
            'data': {
                'recomendaciones': recomendaciones_data,
                'total_encontrados': len(platos_filtrados),
                'perfil_usuario': {
                    'id_usuario': usuario.id_usuario,
                    'nombre': usuario.get_nombre(),
                    'restricciones': usuario.restricciones or [],
                    'alergias': usuario.alergias or [],
                    'enfermedades': usuario.enfermedades or []
                },
                'criterios_aplicados': criterios,
                'fecha_consulta': datetime.utcnow().isoformat()
            },
            'message': f'Se encontraron {len(recomendaciones_data)} recomendaciones para el usuario'
        }
        
        logger.info(f"Recomendaciones generadas para usuario {id_usuario}: {len(recomendaciones_data)} platos")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener las recomendaciones',
            'details': str(e)
        }), 500

@recommend_bp.route('/safe', methods=['GET'])
def get_safe_plates():
    """
    Obtiene platos seguros para un usuario (sin alérgenos problemáticos)
    
    Endpoint: GET /recommend/safe?user_id=1
    
    Query Parameters:
    - user_id: ID del usuario (requerido)
    - limit: Número máximo de platos (default: 10)
    
    Returns:
    {
        "success": true,
        "data": {
            "platos_seguros": [...],
            "usuario": {...},
            "total_seguros": 8
        }
    }
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'ID de usuario requerido',
                'message': 'El parámetro user_id es obligatorio'
            }), 400
        
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'ID de usuario inválido',
                'message': 'El user_id debe ser un número entero'
            }), 400
        
        limit = min(int(request.args.get('limit', 10)), 50)
        
        # Obtener usuario
        usuario = db_service.obtener_usuario(user_id)
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'message': f'No se encontró el usuario con ID {user_id}'
            }), 404
        
        # Obtener todos los platos
        with db_service.get_session() as session:
            from models.platos import Plato
            
            todos_platos = session.query(Plato).all()
        
        # Filtrar platos seguros
        platos_seguros = []
        restricciones = usuario.get_restricciones_completas()
        
        for plato in todos_platos:
            if plato.es_seguro_para_usuario(restricciones):
                plato_dict = plato.to_dict()
                plato_dict['nivel_riesgo'] = 'bajo'
                plato_dict['recomendacion'] = 'Plato completamente seguro para tu perfil dietético'
                platos_seguros.append(plato_dict)
        
        # Limitar resultados
        platos_finales = platos_seguros[:limit]
        
        respuesta = {
            'success': True,
            'data': {
                'platos_seguros': platos_finales,
                'usuario': usuario.to_dict(),
                'total_seguros': len(platos_seguros),
                'fecha_consulta': datetime.utcnow().isoformat()
            },
            'message': f'Se encontraron {len(platos_finales)} platos seguros para el usuario'
        }
        
        logger.info(f"Platos seguros obtenidos para usuario {user_id}: {len(platos_finales)} platos")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo platos seguros: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener los platos seguros',
            'details': str(e)
        }), 500

@recommend_bp.route('/by-category', methods=['GET'])
def get_recommendations_by_category():
    """
    Obtiene recomendaciones agrupadas por categoría
    
    Endpoint: GET /recommend/by-category?user_id=1
    
    Query Parameters:
    - user_id: ID del usuario (requerido)
    - limit_per_category: Límite por categoría (default: 5)
    
    Returns:
    {
        "success": true,
        "data": {
            "recomendaciones_por_categoria": {
                "entrada": [...],
                "plato_principal": [...],
                "postre": [...]
            },
            "usuario": {...},
            "resumen": {...}
        }
    }
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'ID de usuario requerido',
                'message': 'El parámetro user_id es obligatorio'
            }), 400
        
        try:
            user_id = int(user_id)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'ID de usuario inválido',
                'message': 'El user_id debe ser un número entero'
            }), 400
        
        limit_per_category = min(int(request.args.get('limit_per_category', 5)), 20)
        
        # Obtener usuario
        usuario = db_service.obtener_usuario(user_id)
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado',
                'message': f'No se encontró el usuario con ID {user_id}'
            }), 404
        
        # Obtener platos recomendados
        platos_recomendados = db_service.obtener_platos_recomendados(user_id)
        
        # Agrupar por categoría
        recomendaciones_por_categoria = {}
        categorias = ['entrada', 'plato_principal', 'postre', 'bebida']
        
        for categoria in categorias:
            platos_categoria = [p for p in platos_recomendados if p.categoria == categoria]
            
            # Limitar por categoría
            platos_limite = platos_categoria[:limit_per_category]
            
            # Preparar datos
            platos_data = []
            for plato in platos_limite:
                plato_dict = plato.to_dict()
                nivel_riesgo = plato.get_nivel_riesgo(usuario.get_restricciones_completas())
                plato_dict['nivel_riesgo'] = nivel_riesgo
                platos_data.append(plato_dict)
            
            recomendaciones_por_categoria[categoria] = platos_data
        
        # Crear resumen
        resumen = {
            'total_categorias': len([c for c in categorias if recomendaciones_por_categoria[c]]),
            'total_platos': sum(len(platos) for platos in recomendaciones_por_categoria.values()),
            'categoria_mas_platos': max(recomendaciones_por_categoria.keys(), 
                                      key=lambda k: len(recomendaciones_por_categoria[k])),
            'restricciones_aplicadas': usuario.get_restricciones_completas()
        }
        
        respuesta = {
            'success': True,
            'data': {
                'recomendaciones_por_categoria': recomendaciones_por_categoria,
                'usuario': usuario.to_dict(),
                'resumen': resumen,
                'fecha_consulta': datetime.utcnow().isoformat()
            },
            'message': 'Recomendaciones agrupadas por categoría obtenidas exitosamente'
        }
        
        logger.info(f"Recomendaciones por categoría obtenidas para usuario {user_id}")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones por categoría: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener las recomendaciones por categoría',
            'details': str(e)
        }), 500

@recommend_bp.route('/similar/<int:plato_id>', methods=['GET'])
def get_similar_plates(plato_id: int):
    """
    Obtiene platos similares a uno específico
    
    Endpoint: GET /recommend/similar/<plato_id>
    
    Query Parameters:
    - limit: Número máximo de platos similares (default: 5)
    - user_id: ID del usuario para personalización (opcional)
    
    Returns:
    {
        "success": true,
        "data": {
            "plato_base": {...},
            "platos_similares": [...],
            "criterios_similitud": {...}
        }
    }
    """
    try:
        limit = min(int(request.args.get('limit', 5)), 20)
        user_id = request.args.get('user_id')
        if user_id:
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'ID de usuario inválido',
                    'message': 'El user_id debe ser un número entero'
                }), 400
        
        # Obtener plato base
        plato_base = db_service.obtener_plato(plato_id)
        if not plato_base:
            return jsonify({
                'success': False,
                'error': 'Plato no encontrado',
                'message': f'No se encontró el plato con ID {plato_id}'
            }), 404
        
        # Obtener usuario si se proporcionó
        usuario = None
        if user_id:
            usuario = db_service.obtener_usuario(user_id)
        
        # Buscar platos similares
        with db_service.get_session() as session:
            from models.platos import Plato
            
            # Obtener todos los platos excepto el base
            todos_platos = session.query(Plato).filter(Plato.id_plato != plato_id).all()
        
        platos_similares = []
        
        for plato in todos_platos:
            # Calcular similitud
            similitud = calcular_similitud_platos(plato_base, plato)
            
            if similitud > 0.3:  # Umbral mínimo de similitud
                plato_dict = plato.to_dict()
                plato_dict['similitud'] = round(similitud, 2)
                
                # Agregar recomendación si hay usuario
                if usuario:
                    nivel_riesgo = plato.get_nivel_riesgo(usuario.get_restricciones_completas())
                    plato_dict['nivel_riesgo'] = nivel_riesgo
                    plato_dict['recomendacion'] = f'Similitud: {similitud:.0%}'
                
                platos_similares.append(plato_dict)
        
        # Ordenar por similitud y limitar
        platos_similares.sort(key=lambda x: x['similitud'], reverse=True)
        platos_finales = platos_similares[:limit]
        
        # Criterios de similitud
        criterios = {
            'ingredientes_comunes': len(set(plato_base.ingredientes or []) & set(plato_base.ingredientes or [])),
            'categoria_igual': plato_base.categoria,
            'alergenos_comunes': len(set(plato_base.alergenos_detectados or []) & set(plato_base.alergenos_detectados or []))
        }
        
        respuesta = {
            'success': True,
            'data': {
                'plato_base': plato_base.to_dict(),
                'platos_similares': platos_finales,
                'criterios_similitud': criterios,
                'total_encontrados': len(platos_similares),
                'fecha_consulta': datetime.utcnow().isoformat()
            },
            'message': f'Se encontraron {len(platos_finales)} platos similares'
        }
        
        logger.info(f"Platos similares obtenidos para plato {plato_id}: {len(platos_finales)} platos")
        return jsonify(respuesta), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo platos similares: {e}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': 'No se pudieron obtener los platos similares',
            'details': str(e)
        }), 500

def calcular_similitud_platos(plato1, plato2):
    """
    Calcula la similitud entre dos platos basándose en ingredientes y categoría
    
    Args:
        plato1: Primer plato
        plato2: Segundo plato
        
    Returns:
        float: Similitud entre 0.0 y 1.0
    """
    try:
        # Similitud por categoría
        similitud_categoria = 1.0 if plato1.categoria == plato2.categoria else 0.0
        
        # Similitud por ingredientes
        ingredientes1 = set(plato1.ingredientes or [])
        ingredientes2 = set(plato2.ingredientes or [])
        
        if not ingredientes1 and not ingredientes2:
            similitud_ingredientes = 0.0
        elif not ingredientes1 or not ingredientes2:
            similitud_ingredientes = 0.0
        else:
            interseccion = len(ingredientes1 & ingredientes2)
            union = len(ingredientes1 | ingredientes2)
            similitud_ingredientes = interseccion / union if union > 0 else 0.0
        
        # Similitud por alérgenos
        alergenos1 = set(plato1.alergenos_detectados or [])
        alergenos2 = set(plato2.alergenos_detectados or [])
        
        if not alergenos1 and not alergenos2:
            similitud_alergenos = 1.0  # Ambos sin alérgenos
        elif not alergenos1 or not alergenos2:
            similitud_alergenos = 0.0
        else:
            interseccion = len(alergenos1 & alergenos2)
            union = len(alergenos1 | alergenos2)
            similitud_alergenos = interseccion / union if union > 0 else 0.0
        
        # Similitud por nombre (básica)
        nombre1 = (plato1.nombre or '').lower().split()
        nombre2 = (plato2.nombre or '').lower().split()
        
        if not nombre1 and not nombre2:
            similitud_nombre = 0.0
        elif not nombre1 or not nombre2:
            similitud_nombre = 0.0
        else:
            interseccion = len(set(nombre1) & set(nombre2))
            union = len(set(nombre1) | set(nombre2))
            similitud_nombre = interseccion / union if union > 0 else 0.0
        
        # Ponderación de similitudes
        similitud_total = (
            similitud_categoria * 0.3 +
            similitud_ingredientes * 0.4 +
            similitud_alergenos * 0.2 +
            similitud_nombre * 0.1
        )
        
        return min(similitud_total, 1.0)
        
    except Exception as e:
        logger.error(f"Error calculando similitud de platos: {e}")
        return 0.0
