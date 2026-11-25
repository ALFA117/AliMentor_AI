"""
Tests unitarios para endpoints de AliMentor AI
"""
import json
import pytest
import os
from datetime import datetime
from unittest.mock import Mock, patch

# Configurar variables de entorno para testing
os.environ['FLASK_ENV'] = 'testing'
os.environ['OPENAI_API_KEY'] = 'test-key'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'test'
os.environ['DB_PASSWORD'] = 'test'
os.environ['DB_NAME'] = 'alimentor_ai_test'

from app import create_app

@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    app = create_app('testing')
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Crear cliente de prueba"""
    return app.test_client()

@pytest.fixture
def sample_menu():
    """Menú de prueba"""
    return {
        "menu_text": "MENÚ DEL DÍA\n\n1. Ensalada César - Lechuga, crutones, parmesano - $8.50\n2. Pollo a la parrilla - Con arroz y vegetales - $15.00",
        "user_id": 1
    }

@pytest.fixture
def sample_user():
    """Usuario de prueba"""
    return {
        "nombre": "Usuario Test",
        "edad": 30,
        "genero": "femenino",
        "restricciones": ["vegetariano"],
        "alergias": ["lactosa"],
        "enfermedades": []
    }

class TestAnalyzeEndpoints:
    """Tests para endpoints de análisis"""
    
    def test_analyze_menu_success(self, client, sample_menu):
        """Test análisis exitoso de menú"""
        with patch('services.ai_service.AIService.analizar_menu') as mock_ai:
            mock_ai.return_value = {
                'platos_detectados': [
                    {
                        'nombre': 'Ensalada César',
                        'categoria': 'entrada',
                        'ingredientes': ['lechuga', 'crutones', 'parmesano'],
                        'alergenos_detectados': ['gluten', 'lactosa'],
                        'precio': 8.50
                    }
                ],
                'ingredientes_totales': ['lechuga', 'crutones', 'parmesano'],
                'alergenos_detectados': ['gluten', 'lactosa'],
                'recomendaciones': ['Recomendación 1']
            }
            
            response = client.post('/analyze', json=sample_menu)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
            assert 'analisis' in data['data']
            assert len(data['data']['platos_guardados']) == 1
    
    def test_analyze_menu_missing_text(self, client):
        """Test análisis con texto faltante"""
        response = client.post('/analyze', json={"user_id": 1})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'menu_text' in data['error']
    
    def test_analyze_menu_empty_text(self, client):
        """Test análisis con texto vacío"""
        response = client.post('/analyze', json={"menu_text": "", "user_id": 1})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_analyze_batch_success(self, client):
        """Test análisis en lote exitoso"""
        with patch('services.ai_service.AIService.analizar_menu') as mock_ai:
            mock_ai.return_value = {
                'platos_detectados': [],
                'ingredientes_totales': [],
                'alergenos_detectados': [],
                'recomendaciones': []
            }
            
            data = {
                "menus": [
                    {"menu_text": "Menú 1", "user_id": 1},
                    {"menu_text": "Menú 2", "user_id": 2}
                ]
            }
            
            response = client.post('/analyze/batch', json=data)
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
            assert data['data']['total_procesados'] == 2
    
    def test_analyze_batch_too_many_menus(self, client):
        """Test análisis en lote con demasiados menús"""
        menus = [{"menu_text": f"Menú {i}", "user_id": i} for i in range(15)]
        data = {"menus": menus}
        
        response = client.post('/analyze/batch', json=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False

class TestRecommendEndpoints:
    """Tests para endpoints de recomendaciones"""
    
    def test_get_recommendations_success(self, client):
        """Test obtención exitosa de recomendaciones"""
        with patch('services.db_service.DatabaseService.obtener_usuario') as mock_user:
            mock_user.return_value = Mock(
                id_usuario=1,
                nombre="Test User",
                get_restricciones_completas=lambda: ["vegetariano"]
            )
            
            with patch('services.db_service.DatabaseService.obtener_platos_recomendados') as mock_platos:
                mock_plato = Mock()
                mock_plato.to_dict.return_value = {"nombre": "Plato Test"}
                mock_plato.get_nivel_riesgo.return_value = "bajo"
                mock_platos.return_value = [mock_plato]
                
                response = client.get('/recommend?user_id=1')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] == True
                assert 'recomendaciones' in data['data']
    
    def test_get_recommendations_missing_user_id(self, client):
        """Test recomendaciones sin user_id"""
        response = client.get('/recommend')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_get_safe_plates_success(self, client):
        """Test obtención de platos seguros"""
        with patch('services.db_service.DatabaseService.obtener_usuario') as mock_user:
            mock_user.return_value = Mock(
                id_usuario=1,
                nombre="Test User",
                get_restricciones_completas=lambda: ["vegetariano"]
            )
            
            with patch('services.db_service.DatabaseService.get_session') as mock_session:
                mock_plato = Mock()
                mock_plato.to_dict.return_value = {"nombre": "Plato Seguro"}
                mock_plato.es_seguro_para_usuario.return_value = True
                mock_plato.get_nivel_riesgo.return_value = "bajo"
                
                mock_session.return_value.__enter__.return_value.query.return_value.all.return_value = [mock_plato]
                
                response = client.get('/recommend/safe?user_id=1')
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] == True
                assert 'platos_seguros' in data['data']

class TestFeedbackEndpoints:
    """Tests para endpoints de feedback"""
    
    def test_create_feedback_success(self, client):
        """Test creación exitosa de feedback"""
        with patch('services.db_service.DatabaseService.obtener_usuario') as mock_user:
            mock_user.return_value = Mock(id_usuario=1, nombre="Test User")
            
            with patch('services.db_service.DatabaseService.obtener_plato') as mock_plato:
                mock_plato.return_value = Mock(id_plato=1, nombre="Plato Test")
                
                with patch('services.db_service.DatabaseService.crear_feedback') as mock_create:
                    mock_feedback = Mock()
                    mock_feedback.to_dict.return_value = {
                        "id_feedback": 1,
                        "usuario_id": 1,
                        "plato_id": 1,
                        "calificacion": 5,
                        "tipo_feedback": "positivo"
                    }
                    mock_create.return_value = mock_feedback
                    
                    data = {
                        "usuario_id": 1,
                        "plato_id": 1,
                        "comentario": "Excelente análisis",
                        "calificacion": 5,
                        "tipo_feedback": "positivo"
                    }
                    
                    response = client.post('/feedback', json=data)
                    assert response.status_code == 201
                    data = json.loads(response.data)
                    assert data['success'] == True
    
    def test_create_feedback_missing_required_fields(self, client):
        """Test feedback con campos requeridos faltantes"""
        data = {"usuario_id": 1}
        response = client.post('/feedback', json=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_create_feedback_invalid_rating(self, client):
        """Test feedback con calificación inválida"""
        data = {
            "usuario_id": 1,
            "plato_id": 1,
            "calificacion": 6,  # Inválida (debe ser 1-5)
            "tipo_feedback": "positivo"
        }
        response = client.post('/feedback', json=data)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_get_feedback_success(self, client):
        """Test obtención exitosa de feedback"""
        with patch('services.db_service.DatabaseService.get_session') as mock_session:
            mock_feedback = Mock()
            mock_feedback.to_dict.return_value = {"id_feedback": 1}
            
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_feedback
            
            response = client.get('/feedback/1')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True

class TestImproveEndpoints:
    """Tests para endpoints de mejora"""
    
    def test_improve_ai_success(self, client):
        """Test mejora exitosa de IA"""
        with patch('services.db_service.DatabaseService.obtener_feedback_reciente') as mock_feedback:
            mock_feedback.return_value = [
                Mock(to_dict=lambda: {"tipo_feedback": "correccion", "calificacion": 3})
            ] * 5  # 5 feedbacks
            
            with patch('services.ai_service.AIService.mejorar_prompt_basado_feedback') as mock_improve:
                mock_improve.return_value = {
                    'ajuste_prompt': 'Prompt mejorado',
                    'confianza': 0.8
                }
                
                with patch('services.db_service.DatabaseService.crear_accion_ia') as mock_accion:
                    mock_accion.return_value = Mock(id_accion=1)
                    
                    with patch('services.db_service.DatabaseService.crear_mejora_ia') as mock_mejora:
                        mock_mejora.return_value = Mock(to_dict=lambda: {"id_mejora": 1})
                        
                        response = client.post('/improve')
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data['success'] == True
    
    def test_improve_ai_insufficient_feedback(self, client):
        """Test mejora con feedback insuficiente"""
        with patch('services.db_service.DatabaseService.obtener_feedback_reciente') as mock_feedback:
            mock_feedback.return_value = []  # Sin feedback
            
            response = client.post('/improve')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] == False
    
    def test_get_improvement_status_success(self, client):
        """Test obtención exitosa del estado de mejoras"""
        with patch('services.db_service.DatabaseService.get_session') as mock_session:
            mock_mejora = Mock()
            mock_mejora.to_dict.return_value = {"id_mejora": 1}
            mock_mejora.es_aplicable.return_value = True
            mock_mejora.get_nivel_confianza.return_value = "alta"
            
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_mejora]
            mock_session.return_value.__enter__.return_value.query.return_value.filter.return_value.count.return_value = 1
            
            response = client.get('/improve/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True

class TestMetricsEndpoints:
    """Tests para endpoints de métricas"""
    
    def test_get_metrics_success(self, client):
        """Test obtención exitosa de métricas"""
        with patch('services.metrics_service.MetricsService.calcular_metricas_generales') as mock_general:
            mock_general.return_value = {"total_usuarios": 10}
            
            with patch('services.metrics_service.MetricsService.calcular_precision_ia') as mock_precision:
                mock_precision.return_value = {"precision_general": 85}
                
                with patch('services.metrics_service.MetricsService.calcular_satisfaccion_promedio') as mock_satisfaction:
                    mock_satisfaction.return_value = {"satisfaccion_promedio": 4.2}
                    
                    with patch('services.metrics_service.MetricsService.calcular_tasa_mejora_ia') as mock_improvement:
                        mock_improvement.return_value = {"tasa_mejora": 75}
                        
                        response = client.get('/metrics')
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data['success'] == True
                        assert 'metricas_generales' in data['data']
    
    def test_get_precision_metrics_success(self, client):
        """Test obtención exitosa de métricas de precisión"""
        with patch('services.metrics_service.MetricsService.calcular_precision_ia') as mock_precision:
            mock_precision.return_value = {
                "precision_general": 85,
                "tasa_correccion": 15,
                "total_feedbacks": 100
            }
            
            response = client.get('/metrics/precision')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
            assert data['data']['precision_general'] == 85
    
    def test_get_dashboard_data_success(self, client):
        """Test obtención exitosa de datos de dashboard"""
        with patch('services.metrics_service.MetricsService.calcular_metricas_generales') as mock_general:
            mock_general.return_value = {"total_usuarios": 10, "total_platos": 50}
            
            with patch('services.metrics_service.MetricsService.calcular_precision_ia') as mock_precision:
                mock_precision.return_value = {"precision_general": 85}
                
                with patch('services.metrics_service.MetricsService.calcular_satisfaccion_promedio') as mock_satisfaction:
                    mock_satisfaction.return_value = {"satisfaccion_promedio": 4.2}
                    
                    with patch('services.metrics_service.MetricsService.calcular_tasa_mejora_ia') as mock_improvement:
                        mock_improvement.return_value = {"tasa_mejora": 75}
                        
                        response = client.get('/metrics/dashboard')
                        assert response.status_code == 200
                        data = json.loads(response.data)
                        assert data['success'] == True
                        assert 'indicadores_clave' in data['data']

class TestHealthEndpoints:
    """Tests para endpoints de salud"""
    
    def test_health_check_success(self, client):
        """Test health check exitoso"""
        with patch('services.db_service.DatabaseService.get_session') as mock_session:
            mock_session.return_value.__enter__.return_value.execute.return_value = None
            
            response = client.get('/health')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'healthy'
    
    def test_status_endpoint_success(self, client):
        """Test endpoint de status exitoso"""
        with patch('services.db_service.DatabaseService.obtener_estadisticas_generales') as mock_stats:
            mock_stats.return_value = {"total_usuarios": 10}
            
            response = client.get('/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'operational'
    
    def test_index_endpoint_success(self, client):
        """Test endpoint principal exitoso"""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'endpoints' in data

if __name__ == '__main__':
    pytest.main([__file__])
