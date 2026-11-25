"""
Analizador de Feedback para AliMentor AI
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import statistics

logger = logging.getLogger(__name__)

class FeedbackAnalyzer:
    """
    Analizador de feedback para detectar patrones y generar mejoras
    """
    
    def __init__(self):
        """Inicializa el analizador de feedback"""
        self.logger = logger
    
    def analizar_patrones_feedback(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analiza patrones en el feedback para identificar problemas comunes
        
        Args:
            feedbacks: Lista de feedbacks a analizar
            
        Returns:
            Diccionario con patrones detectados
        """
        try:
            if not feedbacks:
                return {'error': 'No hay feedback para analizar'}
            
            patrones = {
                'resumen_general': self._generar_resumen_general(feedbacks),
                'problemas_frecuentes': self._detectar_problemas_frecuentes(feedbacks),
                'tendencias_calificaciones': self._analizar_tendencias_calificaciones(feedbacks),
                'tipos_feedback': self._analizar_tipos_feedback(feedbacks),
                'sugerencias_mejora': self._generar_sugerencias_mejora(feedbacks),
                'fecha_analisis': datetime.utcnow().isoformat(),
                'cantidad_feedback_analizado': len(feedbacks)
            }
            
            self.logger.info(f"Patrones de feedback analizados: {len(feedbacks)} feedbacks")
            return patrones
            
        except Exception as e:
            self.logger.error(f"Error analizando patrones de feedback: {e}")
            return {'error': f'Error analizando feedback: {str(e)}'}
    
    def detectar_errores_ia(self, feedbacks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detecta errores específicos de la IA basándose en feedback de corrección
        
        Args:
            feedbacks: Lista de feedbacks
            
        Returns:
            Lista de errores detectados
        """
        try:
            errores = []
            feedbacks_correccion = [f for f in feedbacks if f.get('tipo_feedback') == 'correccion']
            
            for feedback in feedbacks_correccion:
                comentario = feedback.get('comentario', '').lower()
                
                # Detectar tipos de errores comunes
                if any(palabra in comentario for palabra in ['ingrediente', 'ingredientes']):
                    errores.append({
                        'tipo': 'ingrediente_no_detectado',
                        'descripcion': 'La IA no detectó correctamente los ingredientes',
                        'comentario': feedback.get('comentario'),
                        'fecha': feedback.get('fecha')
                    })
                
                if any(palabra in comentario for palabra in ['alergeno', 'alergia', 'alérgeno']):
                    errores.append({
                        'tipo': 'alergeno_no_detectado',
                        'descripcion': 'La IA no detectó correctamente los alérgenos',
                        'comentario': feedback.get('comentario'),
                        'fecha': feedback.get('fecha')
                    })
                
                if any(palabra in comentario for palabra in ['categoria', 'categoría', 'tipo']):
                    errores.append({
                        'tipo': 'categoria_incorrecta',
                        'descripcion': 'La IA clasificó incorrectamente la categoría del plato',
                        'comentario': feedback.get('comentario'),
                        'fecha': feedback.get('fecha')
                    })
                
                if any(palabra in comentario for palabra in ['precio', 'costo', 'valor']):
                    errores.append({
                        'tipo': 'precio_incorrecto',
                        'descripcion': 'La IA estimó incorrectamente el precio',
                        'comentario': feedback.get('comentario'),
                        'fecha': feedback.get('fecha')
                    })
            
            self.logger.info(f"Errores de IA detectados: {len(errores)}")
            return errores
            
        except Exception as e:
            self.logger.error(f"Error detectando errores de IA: {e}")
            return []
    
    def calcular_metricas_satisfaccion(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula métricas de satisfacción del usuario
        
        Args:
            feedbacks: Lista de feedbacks
            
        Returns:
            Diccionario con métricas de satisfacción
        """
        try:
            calificaciones = [f.get('calificacion') for f in feedbacks if f.get('calificacion') is not None]
            
            if not calificaciones:
                return {
                    'satisfaccion_promedio': 0,
                    'total_calificaciones': 0,
                    'distribucion_calificaciones': {},
                    'tendencia': 'sin_datos'
                }
            
            # Calcular métricas básicas
            satisfaccion_promedio = statistics.mean(calificaciones)
            mediana = statistics.median(calificaciones)
            desviacion_estandar = statistics.stdev(calificaciones) if len(calificaciones) > 1 else 0
            
            # Distribución de calificaciones
            distribucion = Counter(calificaciones)
            
            # Determinar tendencia
            if satisfaccion_promedio >= 4.0:
                tendencia = 'muy_positiva'
            elif satisfaccion_promedio >= 3.0:
                tendencia = 'positiva'
            elif satisfaccion_promedio >= 2.0:
                tendencia = 'neutral'
            else:
                tendencia = 'negativa'
            
            return {
                'satisfaccion_promedio': round(satisfaccion_promedio, 2),
                'mediana': round(mediana, 2),
                'desviacion_estandar': round(desviacion_estandar, 2),
                'total_calificaciones': len(calificaciones),
                'distribucion_calificaciones': dict(distribucion),
                'tendencia': tendencia,
                'calificacion_mas_frecuente': distribucion.most_common(1)[0][0] if distribucion else None
            }
            
        except Exception as e:
            self.logger.error(f"Error calculando métricas de satisfacción: {e}")
            return {'error': f'Error calculando métricas: {str(e)}'}
    
    def identificar_areas_mejora(self, feedbacks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifica áreas específicas que necesitan mejora
        
        Args:
            feedbacks: Lista de feedbacks
            
        Returns:
            Lista de áreas de mejora identificadas
        """
        try:
            areas_mejora = []
            
            # Analizar feedback negativo y de corrección
            feedbacks_problema = [f for f in feedbacks if f.get('tipo_feedback') in ['negativo', 'correccion']]
            
            if not feedbacks_problema:
                return areas_mejora
            
            # Contar problemas por área
            problemas_por_area = Counter()
            comentarios_por_area = {}
            
            for feedback in feedbacks_problema:
                comentario = feedback.get('comentario', '').lower()
                
                # Detectar áreas problemáticas
                if any(palabra in comentario for palabra in ['ingrediente', 'ingredientes', 'componente']):
                    area = 'deteccion_ingredientes'
                    problemas_por_area[area] += 1
                    if area not in comentarios_por_area:
                        comentarios_por_area[area] = []
                    comentarios_por_area[area].append(feedback.get('comentario'))
                
                if any(palabra in comentario for palabra in ['alergeno', 'alergia', 'alérgeno', 'intolerancia']):
                    area = 'deteccion_alergenos'
                    problemas_por_area[area] += 1
                    if area not in comentarios_por_area:
                        comentarios_por_area[area] = []
                    comentarios_por_area[area].append(feedback.get('comentario'))
                
                if any(palabra in comentario for palabra in ['categoria', 'categoría', 'tipo', 'clasificacion']):
                    area = 'clasificacion_platos'
                    problemas_por_area[area] += 1
                    if area not in comentarios_por_area:
                        comentarios_por_area[area] = []
                    comentarios_por_area[area].append(feedback.get('comentario'))
                
                if any(palabra in comentario for palabra in ['precio', 'costo', 'valor', 'económico']):
                    area = 'estimacion_precios'
                    problemas_por_area[area] += 1
                    if area not in comentarios_por_area:
                        comentarios_por_area[area] = []
                    comentarios_por_area[area].append(feedback.get('comentario'))
                
                if any(palabra in comentario for palabra in ['recomendacion', 'recomendación', 'sugerencia']):
                    area = 'recomendaciones'
                    problemas_por_area[area] += 1
                    if area not in comentarios_por_area:
                        comentarios_por_area[area] = []
                    comentarios_por_area[area].append(feedback.get('comentario'))
            
            # Crear áreas de mejora
            for area, cantidad in problemas_por_area.most_common():
                areas_mejora.append({
                    'area': area,
                    'nombre_legible': self._obtener_nombre_area(area),
                    'frecuencia_problemas': cantidad,
                    'prioridad': self._calcular_prioridad(cantidad, len(feedbacks_problema)),
                    'comentarios_relacionados': comentarios_por_area.get(area, []),
                    'sugerencias': self._generar_sugerencias_area(area)
                })
            
            self.logger.info(f"Áreas de mejora identificadas: {len(areas_mejora)}")
            return areas_mejora
            
        except Exception as e:
            self.logger.error(f"Error identificando áreas de mejora: {e}")
            return []
    
    def _generar_resumen_general(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera un resumen general del feedback"""
        total = len(feedbacks)
        positivos = sum(1 for f in feedbacks if f.get('tipo_feedback') == 'positivo')
        negativos = sum(1 for f in feedbacks if f.get('tipo_feedback') == 'negativo')
        correcciones = sum(1 for f in feedbacks if f.get('tipo_feedback') == 'correccion')
        
        return {
            'total_feedbacks': total,
            'positivos': positivos,
            'negativos': negativos,
            'correcciones': correcciones,
            'porcentaje_positivo': round((positivos / total) * 100, 2) if total > 0 else 0
        }
    
    def _detectar_problemas_frecuentes(self, feedbacks: List[Dict[str, Any]]) -> List[str]:
        """Detecta problemas frecuentes mencionados en el feedback"""
        palabras_problema = []
        
        for feedback in feedbacks:
            comentario = feedback.get('comentario', '').lower()
            if any(palabra in comentario for palabra in ['error', 'incorrecto', 'mal', 'fallo']):
                palabras_problema.append('errores_generales')
            if any(palabra in comentario for palabra in ['lento', 'demora', 'tardado']):
                palabras_problema.append('problemas_rendimiento')
            if any(palabra in comentario for palabra in ['confuso', 'difícil', 'complicado']):
                palabras_problema.append('problemas_usabilidad')
        
        return list(set(palabras_problema))
    
    def _analizar_tendencias_calificaciones(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analiza tendencias en las calificaciones"""
        calificaciones = [f.get('calificacion') for f in feedbacks if f.get('calificacion') is not None]
        
        if not calificaciones:
            return {'tendencia': 'sin_datos'}
        
        # Agrupar por períodos (últimos 7 días vs anteriores)
        ahora = datetime.utcnow()
        hace_7_dias = ahora - timedelta(days=7)
        
        calificaciones_recientes = []
        calificaciones_anteriores = []
        
        for feedback in feedbacks:
            if feedback.get('calificacion') is None:
                continue
            
            fecha_str = feedback.get('fecha')
            if fecha_str:
                try:
                    fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    if fecha >= hace_7_dias:
                        calificaciones_recientes.append(feedback.get('calificacion'))
                    else:
                        calificaciones_anteriores.append(feedback.get('calificacion'))
                except:
                    continue
        
        tendencia = 'estable'
        if calificaciones_recientes and calificaciones_anteriores:
            promedio_reciente = statistics.mean(calificaciones_recientes)
            promedio_anterior = statistics.mean(calificaciones_anteriores)
            
            if promedio_reciente > promedio_anterior + 0.5:
                tendencia = 'mejorando'
            elif promedio_reciente < promedio_anterior - 0.5:
                tendencia = 'empeorando'
        
        return {
            'tendencia': tendencia,
            'promedio_reciente': round(statistics.mean(calificaciones_recientes), 2) if calificaciones_recientes else None,
            'promedio_anterior': round(statistics.mean(calificaciones_anteriores), 2) if calificaciones_anteriores else None
        }
    
    def _analizar_tipos_feedback(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analiza la distribución de tipos de feedback"""
        tipos = Counter(f.get('tipo_feedback', 'desconocido') for f in feedbacks)
        return dict(tipos)
    
    def _generar_sugerencias_mejora(self, feedbacks: List[Dict[str, Any]]) -> List[str]:
        """Genera sugerencias de mejora basadas en el feedback"""
        sugerencias = []
        
        # Analizar feedback negativo
        negativos = [f for f in feedbacks if f.get('tipo_feedback') == 'negativo']
        if len(negativos) > len(feedbacks) * 0.3:  # Más del 30% negativo
            sugerencias.append("Revisar la precisión general del análisis de menús")
        
        # Analizar calificaciones bajas
        calificaciones_bajas = [f for f in feedbacks if f.get('calificacion', 5) <= 2]
        if len(calificaciones_bajas) > len(feedbacks) * 0.2:  # Más del 20% con calificación baja
            sugerencias.append("Mejorar la calidad de las recomendaciones")
        
        # Analizar correcciones
        correcciones = [f for f in feedbacks if f.get('tipo_feedback') == 'correccion']
        if correcciones:
            sugerencias.append("Actualizar prompts para reducir errores de detección")
        
        return sugerencias
    
    def _obtener_nombre_area(self, area: str) -> str:
        """Obtiene el nombre legible de un área"""
        nombres = {
            'deteccion_ingredientes': 'Detección de Ingredientes',
            'deteccion_alergenos': 'Detección de Alérgenos',
            'clasificacion_platos': 'Clasificación de Platos',
            'estimacion_precios': 'Estimación de Precios',
            'recomendaciones': 'Recomendaciones Personalizadas'
        }
        return nombres.get(area, area)
    
    def _calcular_prioridad(self, cantidad: int, total: int) -> str:
        """Calcula la prioridad de un área de mejora"""
        porcentaje = (cantidad / total) * 100 if total > 0 else 0
        
        if porcentaje >= 50:
            return 'alta'
        elif porcentaje >= 25:
            return 'media'
        else:
            return 'baja'
    
    def _generar_sugerencias_area(self, area: str) -> List[str]:
        """Genera sugerencias específicas para un área"""
        sugerencias = {
            'deteccion_ingredientes': [
                'Mejorar el prompt para incluir más sinónimos de ingredientes',
                'Agregar validación cruzada con bases de datos de ingredientes',
                'Implementar aprendizaje de nuevos ingredientes'
            ],
            'deteccion_alergenos': [
                'Actualizar lista de alérgenos comunes',
                'Mejorar detección de alérgenos ocultos',
                'Agregar validación de seguridad alimentaria'
            ],
            'clasificacion_platos': [
                'Refinar criterios de clasificación',
                'Mejorar detección de categorías regionales',
                'Agregar subcategorías más específicas'
            ],
            'estimacion_precios': [
                'Integrar datos de precios actuales',
                'Considerar variaciones regionales',
                'Mejorar algoritmos de estimación'
            ],
            'recomendaciones': [
                'Personalizar más las recomendaciones',
                'Considerar preferencias culturales',
                'Mejorar integración con restricciones dietéticas'
            ]
        }
        return sugerencias.get(area, ['Revisar y mejorar el área específica'])
