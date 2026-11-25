"""
Servicio de IA para AliMentor AI
"""
import openai
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import Config
from utils.prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)

class AIService:
    """
    Servicio para interactuar con OpenAI GPT-4o-mini
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Inicializa el servicio de IA
        
        Args:
            api_key: Clave API de OpenAI
            model: Modelo a utilizar
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.prompt_templates = PromptTemplates()
    
    def analizar_menu(self, menu_text: str, usuario_id: int = None) -> Dict[str, Any]:
        """
        Analiza un menú de texto usando OpenAI
        
        Args:
            menu_text: Texto del menú a analizar
            usuario_id: ID del usuario (opcional)
            
        Returns:
            Diccionario con el análisis del menú
        """
        try:
            # Obtener el prompt de análisis
            prompt = self.prompt_templates.get_analisis_menu_prompt(menu_text)
            
            # Llamar a OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto nutricionista y analista de menús especializado en detectar ingredientes, alérgenos y proporcionar recomendaciones alimentarias."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Procesar la respuesta
            respuesta_texto = response.choices[0].message.content
            analisis = self._procesar_respuesta_analisis(respuesta_texto)
            
            # Agregar metadatos
            analisis['fecha_analisis'] = datetime.utcnow().isoformat()
            analisis['usuario_id'] = usuario_id
            analisis['modelo_ia'] = self.model
            
            logger.info(f"Menú analizado exitosamente para usuario {usuario_id}")
            return analisis
            
        except Exception as e:
            logger.error(f"Error analizando menú: {e}")
            return {
                'error': str(e),
                'fecha_analisis': datetime.utcnow().isoformat(),
                'usuario_id': usuario_id
            }
    
    def generar_recomendaciones(self, usuario_id: int, restricciones: List[str]) -> Dict[str, Any]:
        """
        Genera recomendaciones personalizadas para un usuario
        
        Args:
            usuario_id: ID del usuario
            restricciones: Lista de restricciones del usuario
            
        Returns:
            Diccionario con recomendaciones
        """
        try:
            prompt = self.prompt_templates.get_recomendaciones_prompt(restricciones)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un nutricionista experto que proporciona recomendaciones alimentarias personalizadas basadas en restricciones dietéticas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            respuesta_texto = response.choices[0].message.content
            recomendaciones = self._procesar_respuesta_recomendaciones(respuesta_texto)
            
            recomendaciones['usuario_id'] = usuario_id
            recomendaciones['fecha_generacion'] = datetime.utcnow().isoformat()
            
            logger.info(f"Recomendaciones generadas para usuario {usuario_id}")
            return recomendaciones
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}")
            return {
                'error': str(e),
                'usuario_id': usuario_id,
                'fecha_generacion': datetime.utcnow().isoformat()
            }
    
    def mejorar_prompt_basado_feedback(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Mejora los prompts basándose en el feedback de usuarios
        
        Args:
            feedbacks: Lista de feedbacks para analizar
            
        Returns:
            Diccionario con mejoras de prompt
        """
        try:
            # Preparar datos de feedback para análisis
            feedback_text = self._preparar_feedback_para_analisis(feedbacks)
            
            prompt = self.prompt_templates.get_mejora_prompt_prompt(feedback_text)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en optimización de prompts de IA. Analiza el feedback de usuarios y sugiere mejoras específicas para prompts de análisis de menús."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            respuesta_texto = response.choices[0].message.content
            mejoras = self._procesar_respuesta_mejoras(respuesta_texto)
            
            # Calcular nivel de confianza basado en la cantidad y calidad del feedback
            confianza = self._calcular_confianza_mejora(feedbacks)
            mejoras['confianza'] = confianza
            mejoras['fecha_mejora'] = datetime.utcnow().isoformat()
            mejoras['cantidad_feedback_analizado'] = len(feedbacks)
            
            logger.info(f"Mejoras de prompt generadas con confianza {confianza}")
            return mejoras
            
        except Exception as e:
            logger.error(f"Error mejorando prompt: {e}")
            return {
                'error': str(e),
                'fecha_mejora': datetime.utcnow().isoformat()
            }
    
    def _procesar_respuesta_analisis(self, respuesta: str) -> Dict[str, Any]:
        """
        Procesa la respuesta de análisis de menú
        
        Args:
            respuesta: Respuesta de texto de OpenAI
            
        Returns:
            Diccionario estructurado con el análisis
        """
        try:
            # Intentar parsear como JSON primero
            if respuesta.strip().startswith('{'):
                return json.loads(respuesta)
            
            # Si no es JSON, procesar como texto estructurado
            analisis = {
                'platos_detectados': [],
                'ingredientes_totales': [],
                'alergenos_detectados': [],
                'recomendaciones': [],
                'resumen': respuesta
            }
            
            # Buscar patrones en el texto (implementación básica)
            lineas = respuesta.split('\n')
            plato_actual = None
            
            for linea in lineas:
                linea = linea.strip()
                if not linea:
                    continue
                
                # Detectar platos
                if any(palabra in linea.lower() for palabra in ['plato', 'entrada', 'principal', 'postre', 'bebida']):
                    plato_actual = {
                        'nombre': linea,
                        'ingredientes': [],
                        'alergenos': []
                    }
                    analisis['platos_detectados'].append(plato_actual)
                
                # Detectar ingredientes
                elif any(palabra in linea.lower() for palabra in ['ingrediente', 'contiene', 'incluye']):
                    if plato_actual:
                        plato_actual['ingredientes'].append(linea)
                
                # Detectar alérgenos
                elif any(palabra in linea.lower() for palabra in ['alergeno', 'alergia', 'intolerancia']):
                    if plato_actual:
                        plato_actual['alergenos'].append(linea)
            
            return analisis
            
        except Exception as e:
            logger.error(f"Error procesando respuesta de análisis: {e}")
            return {
                'error': f"Error procesando respuesta: {str(e)}",
                'resumen': respuesta
            }
    
    def _procesar_respuesta_recomendaciones(self, respuesta: str) -> Dict[str, Any]:
        """
        Procesa la respuesta de recomendaciones
        
        Args:
            respuesta: Respuesta de texto de OpenAI
            
        Returns:
            Diccionario estructurado con recomendaciones
        """
        try:
            if respuesta.strip().startswith('{'):
                return json.loads(respuesta)
            
            return {
                'recomendaciones_generales': respuesta,
                'alimentos_recomendados': [],
                'alimentos_evitar': [],
                'consejos_nutricionales': []
            }
            
        except Exception as e:
            logger.error(f"Error procesando recomendaciones: {e}")
            return {
                'error': f"Error procesando recomendaciones: {str(e)}",
                'recomendaciones_generales': respuesta
            }
    
    def _procesar_respuesta_mejoras(self, respuesta: str) -> Dict[str, Any]:
        """
        Procesa la respuesta de mejoras de prompt
        
        Args:
            respuesta: Respuesta de texto de OpenAI
            
        Returns:
            Diccionario estructurado con mejoras
        """
        try:
            if respuesta.strip().startswith('{'):
                return json.loads(respuesta)
            
            return {
                'ajuste_prompt': respuesta,
                'observacion': 'Mejora generada automáticamente basada en feedback',
                'patrones_detectados': [],
                'sugerencias_especificas': []
            }
            
        except Exception as e:
            logger.error(f"Error procesando mejoras: {e}")
            return {
                'error': f"Error procesando mejoras: {str(e)}",
                'ajuste_prompt': respuesta
            }
    
    def _preparar_feedback_para_analisis(self, feedbacks: List[Dict[str, Any]]) -> str:
        """
        Prepara el feedback para análisis de mejoras
        
        Args:
            feedbacks: Lista de feedbacks
            
        Returns:
            Texto estructurado con el feedback
        """
        feedback_text = "ANÁLISIS DE FEEDBACK PARA MEJORA DE IA:\n\n"
        
        for i, feedback in enumerate(feedbacks, 1):
            feedback_text += f"Feedback {i}:\n"
            feedback_text += f"- Tipo: {feedback.get('tipo_feedback', 'N/A')}\n"
            feedback_text += f"- Calificación: {feedback.get('calificacion', 'N/A')}\n"
            feedback_text += f"- Comentario: {feedback.get('comentario', 'N/A')}\n"
            feedback_text += f"- Fecha: {feedback.get('fecha', 'N/A')}\n\n"
        
        return feedback_text
    
    def _calcular_confianza_mejora(self, feedbacks: List[Dict[str, Any]]) -> float:
        """
        Calcula el nivel de confianza para una mejora basada en el feedback
        
        Args:
            feedbacks: Lista de feedbacks
            
        Returns:
            Nivel de confianza entre 0.0 y 1.0
        """
        if not feedbacks:
            return 0.0
        
        # Factores que afectan la confianza
        cantidad_feedback = len(feedbacks)
        feedbacks_correccion = sum(1 for f in feedbacks if f.get('tipo_feedback') == 'correccion')
        calificaciones_altas = sum(1 for f in feedbacks if f.get('calificacion', 0) >= 4)
        
        # Cálculo base de confianza
        confianza_base = min(cantidad_feedback / 10.0, 1.0)  # Máximo 1.0 con 10+ feedbacks
        
        # Bonus por feedbacks de corrección (más valiosos)
        bonus_correccion = (feedbacks_correccion / cantidad_feedback) * 0.2
        
        # Bonus por calificaciones altas
        bonus_calificaciones = (calificaciones_altas / cantidad_feedback) * 0.1
        
        confianza_final = min(confianza_base + bonus_correccion + bonus_calificaciones, 1.0)
        
        return round(confianza_final, 2)
    
    def validar_respuesta_ia(self, respuesta: Dict[str, Any]) -> bool:
        """
        Valida si una respuesta de IA es válida y completa
        
        Args:
            respuesta: Respuesta de la IA
            
        Returns:
            bool: True si es válida
        """
        if not respuesta or 'error' in respuesta:
            return False
        
        # Validar campos mínimos para análisis de menú
        campos_requeridos = ['platos_detectados', 'ingredientes_totales', 'alergenos_detectados']
        return all(campo in respuesta for campo in campos_requeridos)
    
    def analizar_compatibilidad_platillo(self, platillo: Dict[str, Any], restricciones_usuario: List[str]) -> Dict[str, Any]:
        """
        Analiza la compatibilidad de un platillo con las restricciones del usuario
        
        Args:
            platillo: Datos del platillo
            restricciones_usuario: Lista de restricciones del usuario
            
        Returns:
            Diccionario con el análisis de compatibilidad
        """
        try:
            # Crear prompt específico para análisis de compatibilidad
            prompt = f"""
            Analiza la compatibilidad del siguiente platillo con las restricciones del usuario:
            
            PLATO: {platillo.get('nombre', '')}
            DESCRIPCIÓN: {platillo.get('descripcion', '')}
            
            RESTRICCIONES DEL USUARIO: {', '.join(restricciones_usuario)}
            
            Identifica:
            1. Ingredientes peligrosos para el usuario
            2. Nivel de riesgo (bajo/medio/alto)
            3. Recomendación específica
            
            Responde en formato JSON:
            {{
                "ingredientes_peligrosos": ["lista", "de", "ingredientes"],
                "nivel_riesgo": "bajo|medio|alto",
                "recomendacion": "Recomendación específica",
                "detalles": {{
                    "ingredientes_detectados": ["lista", "de", "todos", "los", "ingredientes"],
                    "alergenos_presentes": ["lista", "de", "alergenos"],
                    "confianza": 0.85
                }}
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en análisis nutricional y detección de alérgenos. Proporciona análisis precisos y detallados."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Procesar respuesta
            content = response.choices[0].message.content.strip()
            
            # Intentar parsear JSON
            try:
                analisis = json.loads(content)
                
                # Validar estructura
                if not isinstance(analisis, dict):
                    raise ValueError("Respuesta no es un diccionario")
                
                return analisis
                
            except json.JSONDecodeError:
                # Si no es JSON válido, crear respuesta estructurada
                return {
                    "ingredientes_peligrosos": [],
                    "nivel_riesgo": "bajo",
                    "recomendacion": "Análisis no disponible",
                    "detalles": {
                        "ingredientes_detectados": [],
                        "alergenos_presentes": [],
                        "confianza": 0.0,
                        "error": "No se pudo procesar la respuesta de la IA"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error analizando compatibilidad: {e}")
            return {
                "ingredientes_peligrosos": [],
                "nivel_riesgo": "bajo",
                "recomendacion": "Error en análisis",
                "detalles": {
                    "ingredientes_detectados": [],
                    "alergenos_presentes": [],
                    "confianza": 0.0,
                    "error": str(e)
                }
            }
    
    def mejorar_prompt_basado_feedback(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Mejora el prompt basándose en feedback de usuarios
        
        Args:
            feedbacks: Lista de feedbacks recientes
            
        Returns:
            Diccionario con el prompt mejorado
        """
        try:
            # Crear prompt para análisis de feedback
            feedback_text = "\n".join([
                f"Feedback {i+1}: {f.get('comentarios', '')} - Calificación: {f.get('calificacion', 'N/A')}"
                for i, f in enumerate(feedbacks[:10])  # Limitar a 10 feedbacks
            ])
            
            prompt = f"""
            Analiza el siguiente feedback de usuarios sobre análisis de menús y genera mejoras para el prompt:
            
            FEEDBACK RECIBIDO:
            {feedback_text}
            
            Identifica:
            1. Patrones comunes en los errores
            2. Áreas de mejora en la detección de ingredientes
            3. Sugerencias específicas para el prompt
            
            Genera un prompt mejorado que:
            - Sea más preciso en la detección de alérgenos
            - Proporcione recomendaciones más útiles
            - Reduzca falsos positivos/negativos
            
            Responde en formato JSON:
            {{
                "ajuste_prompt": "Nuevo prompt mejorado",
                "patrones_detectados": ["patrón1", "patrón2"],
                "mejoras_aplicadas": ["mejora1", "mejora2"],
                "confianza_mejora": 0.85
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en mejora de prompts de IA. Analiza feedback y genera mejoras específicas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            # Procesar respuesta
            content = response.choices[0].message.content.strip()
            
            try:
                mejoras = json.loads(content)
                return mejoras
                
            except json.JSONDecodeError:
                return {
                    "ajuste_prompt": "Prompt base sin mejoras específicas",
                    "patrones_detectados": [],
                    "mejoras_aplicadas": [],
                    "confianza_mejora": 0.0,
                    "error": "No se pudo procesar la respuesta de mejora"
                }
                
        except Exception as e:
            logger.error(f"Error mejorando prompt: {e}")
            return {
                "ajuste_prompt": "Prompt base sin mejoras",
                "patrones_detectados": [],
                "mejoras_aplicadas": [],
                "confianza_mejora": 0.0,
                "error": str(e)
            }
