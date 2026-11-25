"""
Servicio de base de datos para AliMentor AI
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from models.usuarios import Usuario
from models.platos import Plato
from models.feedback import Feedback, TipoFeedback
from models.acciones_ia import AccionIA
from models.mejora_prompt import MejoraPrompt
from config import Config

logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Servicio para manejar operaciones de base de datos
    """
    
    def __init__(self, database_uri: str):
        """
        Inicializa el servicio de base de datos
        
        Args:
            database_uri: URI de conexión a la base de datos
        """
        self.engine = create_engine(database_uri, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self) -> Session:
        """Obtiene una nueva sesión de base de datos"""
        return self.SessionLocal()
    
    def create_tables(self) -> bool:
        """
        Crea todas las tablas en la base de datos
        
        Returns:
            bool: True si se crearon correctamente, False en caso contrario
        """
        try:
            # Importar todos los modelos para que SQLAlchemy los reconozca
            from models.base import Base
            from models.usuarios import Usuario, Perfil
            from models.platos import Plato
            from models.feedback import Feedback
            from models.acciones_ia import AccionIA
            from models.mejora_prompt import MejoraPrompt
            
            # Crear todas las tablas
            Base.metadata.create_all(bind=self.engine)
            logger.info("Tablas creadas exitosamente")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error creando tablas: {e}")
            return False
    
    # ========== OPERACIONES DE USUARIOS ==========
    
    def crear_usuario(self, usuario_data: Dict[str, Any]) -> Optional[Usuario]:
        """
        Crea un nuevo usuario
        
        Args:
            usuario_data: Datos del usuario
            
        Returns:
            Usuario creado o None si hay error
        """
        try:
            with self.get_session() as session:
                usuario = Usuario.from_dict(usuario_data)
                session.add(usuario)
                session.commit()
                session.refresh(usuario)
                logger.info(f"Usuario creado: {usuario.id_usuario}")
                return usuario
        except SQLAlchemyError as e:
            logger.error(f"Error creando usuario: {e}")
            return None
    
    def obtener_usuario(self, usuario_id: int) -> Optional[Usuario]:
        """
        Obtiene un usuario por ID
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Usuario encontrado o None
        """
        try:
            with self.get_session() as session:
                return session.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo usuario {usuario_id}: {e}")
            return None
    
    def actualizar_usuario(self, usuario_id: int, datos_actualizacion: Dict[str, Any]) -> bool:
        """
        Actualiza un usuario existente
        
        Args:
            usuario_id: ID del usuario
            datos_actualizacion: Datos a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            with self.get_session() as session:
                usuario = session.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
                if not usuario:
                    return False
                
                for key, value in datos_actualizacion.items():
                    if hasattr(usuario, key):
                        setattr(usuario, key, value)
                
                session.commit()
                logger.info(f"Usuario {usuario_id} actualizado")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error actualizando usuario {usuario_id}: {e}")
            return False
    
    # ========== OPERACIONES DE PLATOS ==========
    
    def crear_plato(self, plato_data: Dict[str, Any]) -> Optional[Plato]:
        """
        Crea un nuevo plato
        
        Args:
            plato_data: Datos del plato
            
        Returns:
            Plato creado o None si hay error
        """
        try:
            with self.get_session() as session:
                plato = Plato.from_dict(plato_data)
                session.add(plato)
                session.commit()
                session.refresh(plato)
                logger.info(f"Plato creado: {plato.id_plato}")
                return plato
        except SQLAlchemyError as e:
            logger.error(f"Error creando plato: {e}")
            return None
    
    def obtener_plato(self, plato_id: int) -> Optional[Plato]:
        """
        Obtiene un plato por ID
        
        Args:
            plato_id: ID del plato
            
        Returns:
            Plato encontrado o None
        """
        try:
            with self.get_session() as session:
                return session.query(Plato).filter(Plato.id_plato == plato_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo plato {plato_id}: {e}")
            return None
    
    def buscar_platos_por_nombre(self, nombre: str) -> List[Plato]:
        """
        Busca platos por nombre (búsqueda parcial)
        
        Args:
            nombre: Nombre o parte del nombre a buscar
            
        Returns:
            Lista de platos encontrados
        """
        try:
            with self.get_session() as session:
                return session.query(Plato).filter(
                    Plato.nombre.ilike(f"%{nombre}%")
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error buscando platos por nombre '{nombre}': {e}")
            return []
    
    def obtener_platos_recomendados(self, usuario_id: int) -> List[Plato]:
        """
        Obtiene platos recomendados para un usuario basado en sus restricciones
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            Lista de platos recomendados
        """
        try:
            with self.get_session() as session:
                usuario = session.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
                if not usuario:
                    return []
                
                restricciones = usuario.get_restricciones_completas()
                if not restricciones:
                    # Si no tiene restricciones, devolver todos los platos
                    return session.query(Plato).all()
                
                # Buscar platos seguros para el usuario
                platos_seguros = []
                todos_platos = session.query(Plato).all()
                
                for plato in todos_platos:
                    if plato.es_seguro_para_usuario(restricciones):
                        platos_seguros.append(plato)
                
                return platos_seguros
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo platos recomendados para usuario {usuario_id}: {e}")
            return []
    
    # ========== OPERACIONES DE FEEDBACK ==========
    
    def crear_feedback(self, feedback_data: Dict[str, Any]) -> Optional[Feedback]:
        """
        Crea un nuevo feedback
        
        Args:
            feedback_data: Datos del feedback
            
        Returns:
            Feedback creado o None si hay error
        """
        try:
            with self.get_session() as session:
                feedback = Feedback.from_dict(feedback_data)
                session.add(feedback)
                session.commit()
                session.refresh(feedback)
                logger.info(f"Feedback creado: {feedback.id_feedback}")
                return feedback
        except SQLAlchemyError as e:
            logger.error(f"Error creando feedback: {e}")
            return None
    
    def obtener_feedback_por_plato(self, plato_id: int) -> List[Feedback]:
        """
        Obtiene todos los feedbacks de un plato
        
        Args:
            plato_id: ID del plato
            
        Returns:
            Lista de feedbacks
        """
        try:
            with self.get_session() as session:
                return session.query(Feedback).filter(Feedback.plato_id == plato_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo feedbacks del plato {plato_id}: {e}")
            return []
    
    def obtener_feedback_reciente(self, dias: int = 7) -> List[Feedback]:
        """
        Obtiene feedbacks recientes
        
        Args:
            dias: Número de días hacia atrás
            
        Returns:
            Lista de feedbacks recientes
        """
        try:
            with self.get_session() as session:
                fecha_limite = datetime.utcnow() - timedelta(days=dias)
                return session.query(Feedback).filter(
                    Feedback.fecha >= fecha_limite
                ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo feedbacks recientes: {e}")
            return []
    
    # ========== OPERACIONES DE ACCIONES IA ==========
    
    def crear_accion_ia(self, accion_data: Dict[str, Any]) -> Optional[AccionIA]:
        """
        Crea una nueva acción de IA
        
        Args:
            accion_data: Datos de la acción
            
        Returns:
            AccionIA creada o None si hay error
        """
        try:
            with self.get_session() as session:
                accion = AccionIA.from_dict(accion_data)
                session.add(accion)
                session.commit()
                session.refresh(accion)
                logger.info(f"Acción IA creada: {accion.id_accion}")
                return accion
        except SQLAlchemyError as e:
            logger.error(f"Error creando acción IA: {e}")
            return None
    
    def actualizar_accion_ia(self, accion_id: int, exito: bool, salida: str = None) -> bool:
        """
        Actualiza una acción de IA
        
        Args:
            accion_id: ID de la acción
            exito: Si la acción fue exitosa
            salida: Resumen de la salida (opcional)
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            with self.get_session() as session:
                accion = session.query(AccionIA).filter(AccionIA.id_accion == accion_id).first()
                if not accion:
                    return False
                
                accion.exito = exito
                if salida:
                    accion.salida_resumen = salida
                
                session.commit()
                logger.info(f"Acción IA {accion_id} actualizada")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error actualizando acción IA {accion_id}: {e}")
            return False
    
    # ========== OPERACIONES DE MEJORAS IA ==========
    
    def crear_mejora_ia(self, mejora_data: Dict[str, Any]) -> Optional[MejoraPrompt]:
        """
        Crea una nueva mejora de IA
        
        Args:
            mejora_data: Datos de la mejora
            
        Returns:
            MejoraPrompt creada o None si hay error
        """
        try:
            with self.get_session() as session:
                mejora = MejoraPrompt.from_dict(mejora_data)
                session.add(mejora)
                session.commit()
                session.refresh(mejora)
                logger.info(f"Mejora IA creada: {mejora.id_mejora}")
                return mejora
        except SQLAlchemyError as e:
            logger.error(f"Error creando mejora IA: {e}")
            return None
    
    def obtener_ultima_mejora(self) -> Optional[MejoraPrompt]:
        """
        Obtiene la última mejora de IA aplicada
        
        Returns:
            Última mejora o None
        """
        try:
            with self.get_session() as session:
                return session.query(MejoraPrompt).order_by(MejoraPrompt.fecha.desc()).first()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo última mejora IA: {e}")
            return None
    
    def obtener_mejoras_por_accion(self, accion_id: int) -> List[MejoraPrompt]:
        """
        Obtiene todas las mejoras de una acción específica
        
        Args:
            accion_id: ID de la acción
            
        Returns:
            Lista de mejoras
        """
        try:
            with self.get_session() as session:
                return session.query(MejoraPrompt).filter(MejoraPrompt.id_accion == accion_id).all()
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo mejoras de la acción {accion_id}: {e}")
            return []
    
    # ========== MÉTRICAS Y ESTADÍSTICAS ==========
    
    def obtener_estadisticas_generales(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales del sistema
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            with self.get_session() as session:
                total_usuarios = session.query(Usuario).count()
                total_platos = session.query(Plato).count()
                total_feedbacks = session.query(Feedback).count()
                total_acciones = session.query(AccionIA).count()
                total_mejoras = session.query(MejoraPrompt).count()
                
                # Calcular satisfacción promedio
                calificaciones = session.query(Feedback.calificacion).filter(
                    Feedback.calificacion.isnot(None)
                ).all()
                satisfaccion_promedio = 0
                if calificaciones:
                    satisfaccion_promedio = sum(c[0] for c in calificaciones) / len(calificaciones)
                
                # Calcular tasa de éxito de acciones
                acciones_exitosas = session.query(AccionIA).filter(AccionIA.exito == True).count()
                tasa_exito = 0
                if total_acciones > 0:
                    tasa_exito = acciones_exitosas / total_acciones
                
                return {
                    'total_usuarios': total_usuarios,
                    'total_platos': total_platos,
                    'total_feedbacks': total_feedbacks,
                    'total_acciones_ia': total_acciones,
                    'total_mejoras_ia': total_mejoras,
                    'satisfaccion_promedio': round(satisfaccion_promedio, 2),
                    'tasa_exito_acciones': round(tasa_exito, 2)
                }
        except SQLAlchemyError as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def crear_mejora_prompt(self, mejora_data: Dict[str, Any]) -> Optional[Any]:
        """
        Crea una nueva mejora de prompt
        
        Args:
            mejora_data: Datos de la mejora
            
        Returns:
            Objeto MejoraPrompt creado o None
        """
        try:
            from models.mejora_prompt import MejoraPrompt
            
            mejora = MejoraPrompt.from_dict(mejora_data)
            self.db.session.add(mejora)
            self.db.session.commit()
            
            logger.info(f"Mejora de prompt creada: ID {mejora.id_mejora}")
            return mejora
            
        except Exception as e:
            logger.error(f"Error creando mejora de prompt: {e}")
            self.db.session.rollback()
            return None
    
    def obtener_feedback_reciente(self, dias: int = 7) -> List[Any]:
        """
        Obtiene feedback reciente de los últimos N días
        
        Args:
            dias: Número de días hacia atrás
            
        Returns:
            Lista de feedbacks recientes
        """
        try:
            from models.feedback import Feedback
            from datetime import datetime, timedelta
            
            fecha_limite = datetime.utcnow() - timedelta(days=dias)
            
            feedbacks = self.db.session.query(Feedback).filter(
                Feedback.fecha >= fecha_limite
            ).order_by(Feedback.fecha.desc()).all()
            
            logger.info(f"Feedbacks recientes obtenidos: {len(feedbacks)} en los últimos {dias} días")
            return feedbacks
            
        except Exception as e:
            logger.error(f"Error obteniendo feedback reciente: {e}")
            return []
    
    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
