"""
Aplicación principal de AliMentor AI - Analizador Inteligente de Menús
"""
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from datetime import datetime

# Importar configuración
from config import config

# Importar servicios
from services.db_service import DatabaseService
from services.ai_service import AIService
from services.feedback_analyzer import FeedbackAnalyzer
from services.metrics_service import MetricsService

# Importar utilidades
from utils.data_cleaner import DataCleaner

# Importar rutas
from routes.upload_routes import upload_bp, init_services as init_upload_services
from routes.analyze_routes import analyze_bp, init_services as init_analyze_services
from routes.recommend_routes import recommend_bp, init_services as init_recommend_services
from routes.feedback_routes import feedback_bp, init_services as init_feedback_services
from routes.metrics_routes import metrics_bp, init_services as init_metrics_services
from swagger_docs import swagger_bp

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('alimentor_ai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """
    Factory function para crear la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Flask app configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Configurar CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    
    # Inicializar servicios
    try:
        # Servicio de base de datos
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        if not db_uri or 'mysql' in db_uri:
            # Usar SQLite para desarrollo si no hay MySQL disponible
            db_uri = 'sqlite:///alimentor_ai.db'
            logger.warning("Usando SQLite para desarrollo - configura MySQL para producción")
        
        db_service = DatabaseService(db_uri)
        
        # Servicio de IA
        openai_key = app.config.get('OPENAI_API_KEY')
        if not openai_key:
            logger.warning("OPENAI_API_KEY no está configurada - usando clave de prueba")
            openai_key = "sk-test-key-for-development"
        
        ai_service = AIService(
            api_key=openai_key,
            model=app.config.get('OPENAI_MODEL', 'gpt-4o-mini')
        )
        
        # Servicios auxiliares
        feedback_analyzer = FeedbackAnalyzer()
        metrics_service = MetricsService(db_service)
        data_cleaner = DataCleaner()
        
        # Inicializar servicios en las rutas
        init_upload_services(db_service, ai_service, data_cleaner)
        init_analyze_services(ai_service, db_service, feedback_analyzer, data_cleaner)
        init_recommend_services(ai_service, db_service, data_cleaner)
        init_feedback_services(db_service, feedback_analyzer)
        init_metrics_services(db_service, metrics_service)
        
        # Crear tablas de base de datos
        if not db_service.create_tables():
            logger.error("Error creando tablas de base de datos")
            raise RuntimeError("No se pudieron crear las tablas de base de datos")
        
        logger.info("Servicios inicializados exitosamente")
        
    except Exception as e:
        logger.error(f"Error inicializando servicios: {e}")
        raise RuntimeError(f"Error inicializando servicios: {e}")
    
    # Registrar blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(swagger_bp)
    
    # Configurar Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/api/swagger.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "AliMentor AI - API Documentation"
        }
    )
    
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Rutas principales
    @app.route('/')
    def index():
        """Ruta principal de la API"""
        return jsonify({
            'message': 'AliMentor AI - Analizador Inteligente de Menús',
            'version': '1.0.0',
            'status': 'active',
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'analyze': '/analyze',
                'recommend': '/recommend',
                'feedback': '/feedback',
                'improve': '/improve',
                'metrics': '/metrics'
            }
        })
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        try:
            # Verificar conexión a base de datos
            with db_service.get_session() as session:
                session.execute("SELECT 1")
            
            # Verificar servicios
            services_status = {
                'database': 'ok',
                'ai_service': 'ok' if ai_service else 'error',
                'feedback_analyzer': 'ok' if feedback_analyzer else 'error',
                'metrics_service': 'ok' if metrics_service else 'error',
                'data_cleaner': 'ok' if data_cleaner else 'error'
            }
            
            overall_status = 'healthy' if all(status == 'ok' for status in services_status.values()) else 'degraded'
            
            return jsonify({
                'status': overall_status,
                'timestamp': datetime.utcnow().isoformat(),
                'services': services_status,
                'version': '1.0.0'
            }), 200 if overall_status == 'healthy' else 503
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'version': '1.0.0'
            }), 503
    
    @app.route('/status')
    def status():
        """Status endpoint con información detallada del sistema"""
        try:
            # Obtener estadísticas básicas
            stats = db_service.obtener_estadisticas_generales()
            
            return jsonify({
                'status': 'operational',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'statistics': stats,
                'configuration': {
                    'environment': config_name,
                    'debug_mode': app.config.get('DEBUG', False),
                    'database_configured': bool(app.config.get('SQLALCHEMY_DATABASE_URI')),
                    'openai_configured': bool(app.config.get('OPENAI_API_KEY'))
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return jsonify({
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500
    
    # Manejo de errores globales
    @app.errorhandler(400)
    def bad_request(error):
        """Manejo de errores 400"""
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': 'La petición no es válida',
            'timestamp': datetime.utcnow().isoformat()
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Manejo de errores 401"""
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': 'No autorizado para acceder a este recurso',
            'timestamp': datetime.utcnow().isoformat()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Manejo de errores 403"""
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': 'Acceso prohibido a este recurso',
            'timestamp': datetime.utcnow().isoformat()
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Manejo de errores 404"""
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': 'El recurso solicitado no fue encontrado',
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Manejo de errores 405"""
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': 'Método HTTP no permitido para este endpoint',
            'timestamp': datetime.utcnow().isoformat()
        }), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Manejo de errores 422"""
        return jsonify({
            'success': False,
            'error': 'Unprocessable Entity',
            'message': 'Los datos proporcionados no pueden ser procesados',
            'timestamp': datetime.utcnow().isoformat()
        }), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        """Manejo de errores 500"""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'Error interno del servidor',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Manejo de excepciones no controladas"""
        logger.error(f"Unhandled exception: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'Ocurrió un error inesperado',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    # Middleware para logging de requests
    @app.before_request
    def log_request_info():
        """Log de información de requests"""
        logger.info(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")
    
    @app.after_request
    def log_response_info(response):
        """Log de información de responses"""
        logger.info(f"Response: {response.status_code} - {request.method} {request.path}")
        return response
    
    logger.info("Aplicación Flask creada exitosamente")
    return app

def main():
    """Función principal para ejecutar la aplicación"""
    # Obtener configuración del entorno
    config_name = os.getenv('FLASK_ENV', 'default')
    
    # Crear aplicación
    app = create_app(config_name)
    
    # Configurar puerto y host
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando AliMentor AI en {host}:{port} (modo: {config_name})")
    
    # Ejecutar aplicación
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == '__main__':
    main()

# Crear instancia global de la aplicación para importación
app = create_app()
