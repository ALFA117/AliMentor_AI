"""
Modelo de Feedback para AliMentor AI - Arquitectura 4NF
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Optional
import enum
from .base import Base

class TipoFeedback(enum.Enum):
    """Enum para tipos de feedback"""
    POSITIVO = "positivo"
    NEGATIVO = "negativo"
    CORRECCION = "correccion"

class Feedback(Base):
    """
    Modelo de Feedback - Comentarios y calificaciones de usuarios (4NF)
    """
    __tablename__ = 'feedback'
    
    id_feedback = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), nullable=False)
    plato_id = Column(Integer, ForeignKey('platos.id_plato', ondelete='CASCADE'), nullable=False)
    comentarios = Column(Text, nullable=True)  # Cambio de 'comentario' a 'comentarios'
    calificacion = Column(Integer, nullable=True)
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # Restricción de calificación entre 1 y 5
    __table_args__ = (
        CheckConstraint('calificacion BETWEEN 1 AND 5', name='check_calificacion_range'),
    )
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="feedbacks")
    plato = relationship("Plato", back_populates="feedbacks")
    
    def __repr__(self) -> str:
        return f"<Feedback(id={self.id_feedback}, usuario_id={self.usuario_id}, plato_id={self.plato_id})>"
    
    def to_dict(self) -> Dict:
        """Convierte el objeto Feedback a diccionario"""
        return {
            'id_feedback': self.id_feedback,
            'usuario_id': self.usuario_id,
            'plato_id': self.plato_id,
            'comentarios': self.comentarios,
            'calificacion': self.calificacion,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Feedback':
        """Crea un Feedback desde un diccionario"""
        return cls(
            usuario_id=data.get('usuario_id'),
            plato_id=data.get('plato_id'),
            comentarios=data.get('comentarios'),
            calificacion=data.get('calificacion')
        )
    
    def get_puntuacion_numerica(self) -> float:
        """
        Convierte la calificación a un valor numérico para cálculos
        Si no hay calificación, devuelve 0
        """
        if self.calificacion is None:
            return 0.0
        return float(self.calificacion)
    
    def es_valido(self) -> bool:
        """Verifica si el feedback es válido (tiene calificación o comentarios)"""
        return self.calificacion is not None or (self.comentarios and self.comentarios.strip())
