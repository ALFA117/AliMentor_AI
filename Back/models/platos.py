"""
Modelo de Plato para AliMentor AI - Arquitectura 4NF
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, List, Optional
from .base import Base

class Plato(Base):
    """
    Modelo de Plato - Información básica de platos (4NF)
    """
    __tablename__ = 'platos'
    
    id_plato = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True)  # Ej: "entrada", "plato_principal", "postre"
    imagen_url = Column(String(500), nullable=True)  # URL de imagen (no guardar en BD)
    
    # Relaciones
    feedbacks = relationship("Feedback", back_populates="plato", cascade="all, delete-orphan")
    acciones_ia = relationship("AccionIA", back_populates="plato", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Plato(id={self.id_plato}, nombre='{self.nombre}')>"
    
    def to_dict(self) -> Dict:
        """Convierte el objeto Plato a diccionario"""
        return {
            'id_plato': self.id_plato,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'categoria': self.categoria,
            'imagen_url': self.imagen_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Plato':
        """Crea un Plato desde un diccionario"""
        return cls(
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion'),
            categoria=data.get('categoria'),
            imagen_url=data.get('imagen_url')
        )
    
    def es_seguro_para_usuario(self, restricciones: List[str]) -> bool:
        """
        Verifica si el plato es seguro para el usuario basándose en sus restricciones
        
        Args:
            restricciones: Lista de restricciones del usuario
            
        Returns:
            True si el plato es seguro, False en caso contrario
        """
        if not restricciones:
            return True
            
        descripcion_lower = (self.descripcion or "").lower()
        
        # Verificar restricciones comunes
        restricciones_map = {
            'vegetariano': ['carne', 'pollo', 'cerdo', 'res', 'pescado', 'mariscos'],
            'vegano': ['carne', 'pollo', 'cerdo', 'res', 'pescado', 'mariscos', 'queso', 'leche', 'huevo', 'mantequilla'],
            'sin_lactosa': ['queso', 'leche', 'mantequilla', 'crema', 'yogurt'],
            'sin_gluten': ['trigo', 'cebada', 'centeno', 'avena', 'harina'],
            'sin_nueces': ['nueces', 'almendras', 'avellanas', 'pistachos', 'cacahuetes']
        }
        
        for restriccion in restricciones:
            if restriccion.lower() in restricciones_map:
                ingredientes_prohibidos = restricciones_map[restriccion.lower()]
                for ingrediente in ingredientes_prohibidos:
                    if ingrediente in descripcion_lower:
                        return False
        
        return True
