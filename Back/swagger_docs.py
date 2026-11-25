"""
Documentación Swagger para AliMentor AI
"""
from flask import Blueprint, jsonify

swagger_bp = Blueprint('swagger', __name__)

@swagger_bp.route('/api/swagger.json')
def swagger_spec():
    """Especificación Swagger de la API"""
    return jsonify({
        "swagger": "2.0",
        "info": {
            "title": "AliMentor AI - Analizador Inteligente de Menús",
            "description": "API para análisis inteligente de menús con detección de alérgenos y recomendaciones personalizadas",
            "version": "1.0.0",
            "contact": {
                "name": "AliMentor AI Team",
                "email": "contact@alimentorai.com"
            }
        },
        "host": "alimentorai.onrender.com",
        "basePath": "/",
        "schemes": ["https"],
        "paths": {
            "/upload": {
                "post": {
                    "summary": "Sube un menú (texto o imagen)",
                    "description": "Procesa un menú y extrae platillos",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "menu_data": {"type": "string"},
                                    "menu_type": {"type": "string", "enum": ["texto", "imagen"]},
                                    "restaurant_name": {"type": "string"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Menú procesado exitosamente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "platillos": {"type": "array"},
                                            "total_platillos": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/analyze": {
                "post": {
                    "summary": "Analiza compatibilidad alimentaria",
                    "description": "Analiza compatibilidad de platillos con perfil del usuario",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "platillos": {"type": "array"},
                                    "perfil_usuario": {"type": "object"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Análisis de compatibilidad completado",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "compatibilidad": {"type": "array"},
                                            "accion_ia_id": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/recommend": {
                "post": {
                    "summary": "Obtiene recomendaciones personalizadas",
                    "description": "Genera recomendaciones basadas en perfil del usuario",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "id_usuario": {"type": "integer"},
                                    "criterios": {"type": "object"}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Recomendaciones generadas",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "recomendaciones": {"type": "array"},
                                            "total_encontrados": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/feedback": {
                "post": {
                    "summary": "Registra feedback del usuario",
                    "description": "Guarda feedback y activa ciclo de mejora",
                    "parameters": [
                        {
                            "name": "body",
                            "in": "body",
                            "required": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "id_usuario": {"type": "integer"},
                                    "id_plato": {"type": "integer"},
                                    "comentarios": {"type": "string"},
                                    "calificacion": {"type": "integer", "minimum": 1, "maximum": 5}
                                }
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "Feedback registrado exitosamente",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "feedback": {"type": "object"},
                                            "mejora_activada": {"type": "boolean"},
                                            "accion_mejora_id": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/metrics": {
                "get": {
                    "summary": "Obtiene métricas de auto-mejora",
                    "description": "Muestra métricas entre Run 1 y Run 2",
                    "parameters": [
                        {
                            "name": "period",
                            "in": "query",
                            "type": "integer",
                            "enum": [7, 30, 90],
                            "default": 30
                        },
                        {
                            "name": "run_comparison",
                            "in": "query",
                            "type": "boolean",
                            "default": True
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Métricas de auto-mejora",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "success": {"type": "boolean"},
                                    "data": {
                                        "type": "object",
                                        "properties": {
                                            "metricas_auto_mejora": {"type": "object"},
                                            "acciones_ia": {"type": "object"},
                                            "mejoras_prompt": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    })
