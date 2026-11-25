"""
Módulo de rutas para AliMentor AI
"""
from .analyze_routes import analyze_bp
from .recommend_routes import recommend_bp
from .feedback_routes import feedback_bp
from .improve_routes import improve_bp
from .metrics_routes import metrics_bp

__all__ = ['analyze_bp', 'recommend_bp', 'feedback_bp', 'improve_bp', 'metrics_bp']
