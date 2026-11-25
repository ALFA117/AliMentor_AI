"""
Modelo de MejoraIA para AliMentor AI
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal

Base = declarative_base()

class MejoraIA(Base):
    """
    Modelo de MejoraIA que almacena mejoras generadas por la IA basadas en feedback
    """
    __tablename__ = 'mejora_ia'
    
    id_mejora = Column(Integer, primary_key=True, autoincrement=True)
    id_accion = Column(Integer, ForeignKey('acciones_IA.id_accion', ondelete='CASCADE'), nullable=False)
    ajuste_prompt = Column(Text, nullable=False)  # Nuevo prompt mejorado
    observacion = Column(Text, nullable=True)  # Observación sobre la mejora
    confianza = Column(DECIMAL(3, 2), nullable=True)  # Nivel de confianza en la mejora (0.00-1.00)
    fecha = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    accion_ia = relationship("AccionIA", back_populates="mejoras")
    
    def __repr__(self) -> str:
        return f"<MejoraIA(id={self.id_mejora}, confianza={self.confianza})>"
    
    def to_dict(self) -> Dict:
        """Convierte el objeto MejoraIA a diccionario"""
        return {
            'id_mejora': self.id_mejora,
            'id_accion': self.id_accion,
            'ajuste_prompt': self.ajuste_prompt,
            'observacion': self.observacion,
            'confianza': float(self.confianza) if self.confianza else None,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MejoraIA':
        """Crea una MejoraIA desde un diccionario"""
        confianza = None
        if data.get('confianza') is not None:
            confianza = Decimal(str(data.get('confianza')))
        
        return cls(
            id_accion=data.get('id_accion'),
            ajuste_prompt=data.get('ajuste_prompt'),
            observacion=data.get('observacion'),
            confianza=confianza
        )
    
    def es_alta_confianza(self, umbral: float = 0.8) -> bool:
        """Verifica si la mejora tiene alta confianza"""
        if self.confianza is None:
            return False
        return float(self.confianza) >= umbral
    
    def es_media_confianza(self, umbral_bajo: float = 0.5, umbral_alto: float = 0.8) -> bool:
        """Verifica si la mejora tiene confianza media"""
        if self.confianza is None:
            return False
        confianza_float = float(self.confianza)
        return umbral_bajo <= confianza_float < umbral_alto
    
    def es_baja_confianza(self, umbral: float = 0.5) -> bool:
        """Verifica si la mejora tiene baja confianza"""
        if self.confianza is None:
            return True
        return float(self.confianza) < umbral
    
    def get_nivel_confianza(self) -> str:
        """Obtiene el nivel de confianza como string"""
        if self.confianza is None:
            return "desconocido"
        
        confianza_float = float(self.confianza)
        if confianza_float >= 0.8:
            return "alta"
        elif confianza_float >= 0.5:
            return "media"
        else:
            return "baja"
    
    def es_aplicable(self, umbral_minimo: float = 0.6) -> bool:
        """Verifica si la mejora es aplicable basada en el umbral mínimo de confianza"""
        if self.confianza is None:
            return False
        return float(self.confianza) >= umbral_minimo
