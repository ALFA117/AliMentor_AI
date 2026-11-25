"""
Modelos de Perfil y Usuario para AliMentor AI - Arquitectura 4NF
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, List, Optional
from .base import Base

class Perfil(Base):
    """
    Modelo de Perfil - Información personal básica (4NF)
    """
    __tablename__ = 'perfiles'
    
    id_perfil = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    edad = Column(Integer, nullable=True)
    genero = Column(String(20), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relación uno a uno con Usuario
    usuario = relationship("Usuario", back_populates="perfil", uselist=False)

class Usuario(Base):
    """
    Modelo de Usuario - Información dietética específica (4NF)
    """
    __tablename__ = 'usuarios'
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    perfil_id = Column(Integer, ForeignKey('perfiles.id_perfil'), nullable=False, unique=True)
    restricciones = Column(JSON, nullable=True)  # Lista de restricciones alimentarias
    alergias = Column(JSON, nullable=True)  # Lista de alergias
    enfermedades = Column(JSON, nullable=True)  # Lista de enfermedades relacionadas con alimentación
    
    # Relaciones
    perfil = relationship("Perfil", back_populates="usuario")
    feedbacks = relationship("Feedback", back_populates="usuario", cascade="all, delete-orphan")
    acciones_ia = relationship("AccionIA", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Usuario(id={self.id_usuario}, perfil_id={self.perfil_id})>"
    
    def to_dict(self) -> Dict:
        """Convierte el objeto Usuario a diccionario"""
        return {
            'id_usuario': self.id_usuario,
            'perfil_id': self.perfil_id,
            'restricciones': self.restricciones or [],
            'alergias': self.alergias or [],
            'enfermedades': self.enfermedades or []
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Usuario':
        """Crea un Usuario desde un diccionario"""
        return cls(
            perfil_id=data.get('perfil_id'),
            restricciones=data.get('restricciones', []),
            alergias=data.get('alergias', []),
            enfermedades=data.get('enfermedades', [])
        )
    
    def tiene_restriccion(self, restriccion: str) -> bool:
        """Verifica si el usuario tiene una restricción específica"""
        return restriccion in (self.restricciones or [])
    
    def tiene_alergia(self, alergeno: str) -> bool:
        """Verifica si el usuario tiene alergia a un alérgeno específico"""
        return alergeno in (self.alergias or [])
    
    def get_restricciones_completas(self) -> List[str]:
        """Obtiene todas las restricciones del usuario (restricciones + alergias + enfermedades)"""
        restricciones = []
        if self.restricciones:
            restricciones.extend(self.restricciones)
        if self.alergias:
            restricciones.extend(self.alergias)
        if self.enfermedades:
            restricciones.extend(self.enfermedades)
        return list(set(restricciones))  # Eliminar duplicados
    
    def get_nombre(self) -> str:
        """Obtiene el nombre del perfil asociado"""
        return self.perfil.nombre if self.perfil else "Usuario sin perfil"
    
    def get_edad(self) -> Optional[int]:
        """Obtiene la edad del perfil asociado"""
        return self.perfil.edad if self.perfil else None
    
    def get_genero(self) -> Optional[str]:
        """Obtiene el género del perfil asociado"""
        return self.perfil.genero if self.perfil else None
