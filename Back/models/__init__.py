"""
Módulo de modelos SQLAlchemy para AliMentor AI - Arquitectura 4NF
"""
from .base import Base
from .usuarios import Perfil, Usuario
from .platos import Plato
from .feedback import Feedback
from .acciones_ia import AccionIA
from .mejora_prompt import MejoraPrompt

__all__ = ['Base', 'Perfil', 'Usuario', 'Plato', 'Feedback', 'AccionIA', 'MejoraPrompt']
