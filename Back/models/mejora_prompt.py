"""
Modelo de MejoraPrompt para AliMentor AI - Arquitectura 4NF
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Optional
from .base import Base

class MejoraPrompt(Base):
    """
    Modelo de MejoraPrompt - Registro de mejoras de prompts (4NF)
    """
    __tablename__ = 'mejoras_prompt'
    
    id_mejora = Column(Integer, primary_key=True, autoincrement=True)
    id_accion = Column(Integer, ForeignKey('acciones_ia.id_accion', ondelete='CASCADE'), nullable=False)
    prompt_nuevo = Column(Text, nullable=False)  # Nuevo prompt mejorado
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    accion_ia = relationship("AccionIA", back_populates="mejoras")
    
    def __repr__(self) -> str:
        return f"<MejoraPrompt(id={self.id_mejora}, accion_id={self.id_accion})>"
    
    def to_dict(self) -> Dict:
        """Convierte el objeto MejoraPrompt a diccionario"""
        return {
            'id_mejora': self.id_mejora,
            'id_accion': self.id_accion,
            'prompt_nuevo': self.prompt_nuevo,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MejoraPrompt':
        """Crea una MejoraPrompt desde un diccionario"""
        return cls(
            id_accion=data.get('id_accion'),
            prompt_nuevo=data.get('prompt_nuevo')
        )
