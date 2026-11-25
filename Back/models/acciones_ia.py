"""
Modelo de AccionIA para AliMentor AI - Arquitectura 4NF
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Optional
from .base import Base

class AccionIA(Base):
    """
    Modelo de AccionIA - Registro de acciones de IA con trazabilidad (4NF)
    """
    __tablename__ = 'acciones_ia'
    
    id_accion = Column(Integer, primary_key=True, autoincrement=True)
    tipo_accion = Column(String(50), nullable=False)  # Ej: "analisis_menu", "recomendacion", "mejora_prompt"
    usuario_id = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='SET NULL'), nullable=True)
    plato_id = Column(Integer, ForeignKey('platos.id_plato', ondelete='SET NULL'), nullable=True)
    entrada = Column(Text, nullable=True)  # Entrada que recibió la IA
    salida = Column(Text, nullable=True)  # Salida de la IA
    fecha = Column(DateTime, default=datetime.utcnow)
    exito = Column(Boolean, default=False)  # Si la acción fue exitosa
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="acciones_ia")
    plato = relationship("Plato", back_populates="acciones_ia")
    mejoras = relationship("MejoraPrompt", back_populates="accion_ia", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<AccionIA(id={self.id_accion}, tipo='{self.tipo_accion}', exito={self.exito})>"
    
    def to_dict(self) -> Dict:
        """Convierte el objeto AccionIA a diccionario"""
        return {
            'id_accion': self.id_accion,
            'usuario_id': self.usuario_id,
            'plato_id': self.plato_id,
            'tipo_accion': self.tipo_accion,
            'entrada': self.entrada,
            'salida': self.salida,
            'exito': self.exito,
            'fecha': self.fecha.isoformat() if self.fecha else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AccionIA':
        """Crea una AccionIA desde un diccionario"""
        return cls(
            usuario_id=data.get('usuario_id'),
            plato_id=data.get('plato_id'),
            tipo_accion=data.get('tipo_accion'),
            entrada=data.get('entrada'),
            salida=data.get('salida_resumen'),
            exito=data.get('exito', False)
        )
    
    def marcar_como_exitosa(self) -> None:
        """Marca la acción como exitosa"""
        self.exito = True
    
    def marcar_como_fallida(self) -> None:
        """Marca la acción como fallida"""
        self.exito = False
    
    def actualizar_salida(self, salida: str) -> None:
        """Actualiza el resumen de la salida de la IA"""
        self.salida_resumen = salida
    
    def es_analisis_menu(self) -> bool:
        """Verifica si la acción es un análisis de menú"""
        return self.tipo_accion == "analisis_menu"
    
    def es_recomendacion(self) -> bool:
        """Verifica si la acción es una recomendación"""
        return self.tipo_accion == "recomendacion"
    
    def es_mejora_prompt(self) -> bool:
        """Verifica si la acción es una mejora de prompt"""
        return self.tipo_accion == "mejora_prompt"
    
    def get_duracion_segundos(self) -> Optional[float]:
        """
        Calcula la duración de la acción en segundos
        Requiere que se haya registrado una fecha de finalización
        """
        # Este método se puede extender si se agrega un campo fecha_fin
        return None
