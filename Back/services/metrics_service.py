"""
Servicio de Métricas para AliMentor AI
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import statistics

logger = logging.getLogger(__name__)

class MetricsService:
    """
    Servicio para calcular y gestionar métricas del sistema
    """
    
    def __init__(self, db_service):
        """
        Inicializa el servicio de métricas
        
        Args:
            db_service: Instancia del servicio de base de datos
        """
        self.db_service = db_service
        self.logger = logger
    
    def calcular_metricas_generales(self) -> Dict[str, Any]:
        """
        Calcula métricas generales del sistema
        
        Returns:
            Diccionario con métricas generales
        """
        try:
            # Obtener estadísticas básicas
            stats = self.db_service.obtener_estadisticas_generales()
            
            # Calcular métricas adicionales
            metricas = {
                'fecha_calculo': datetime.utcnow().isoformat(),
                'estadisticas_basicas': stats,
                'metricas_rendimiento': self._calcular_metricas_rendimiento(),
                'metricas_satisfaccion': self._calcular_metricas_satisfaccion(),
                'metricas_mejora_ia': self._calcular_metricas_mejora_ia(),
                'tendencias': self._calcular_tendencias()
            }
            
            self.logger.info("Métricas generales calculadas exitosamente")
            return metricas
            
        except Exception as e:
            self.logger.error(f"Error calculando métricas generales: {e}")
            return {'error': f'Error calculando métricas: {str(e)}'}
    
    def calcular_precision_ia(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Calcula la precisión de la IA basándose en feedback
        
        Args:
            periodo_dias: Período en días para el cálculo
            
        Returns:
            Diccionario con métricas de precisión
        """
        try:
            # Obtener feedback del período
            fecha_limite = datetime.utcnow() - timedelta(days=periodo_dias)
            
            with self.db_service.get_session() as session:
                from models.feedback import Feedback
                from models.acciones_ia import AccionIA
                
                # Obtener feedbacks del período
                feedbacks = session.query(Feedback).filter(
                    Feedback.fecha >= fecha_limite
                ).all()
                
                # Obtener acciones de IA del período
                acciones = session.query(AccionIA).filter(
                    AccionIA.fecha >= fecha_limite
                ).all()
                
                # Calcular precisión basada en feedback
                total_feedbacks = len(feedbacks)
                feedbacks_positivos = sum(1 for f in feedbacks if f.calificacion and f.calificacion >= 4)
                feedbacks_correccion = sum(1 for f in feedbacks if f.tipo_feedback.value == 'correccion')
                
                precision_por_calificacion = (feedbacks_positivos / total_feedbacks * 100) if total_feedbacks > 0 else 0
                tasa_correccion = (feedbacks_correccion / total_feedbacks * 100) if total_feedbacks > 0 else 0
                
                # Calcular precisión por tipo de acción
                precision_por_tipo = self._calcular_precision_por_tipo_accion(acciones, feedbacks)
                
                return {
                    'periodo_dias': periodo_dias,
                    'fecha_calculo': datetime.utcnow().isoformat(),
                    'total_feedbacks': total_feedbacks,
                    'total_acciones_ia': len(acciones),
                    'precision_por_calificacion': round(precision_por_calificacion, 2),
                    'tasa_correccion': round(tasa_correccion, 2),
                    'precision_por_tipo': precision_por_tipo,
                    'precision_general': round((100 - tasa_correccion), 2)
                }
                
        except Exception as e:
            self.logger.error(f"Error calculando precisión de IA: {e}")
            return {'error': f'Error calculando precisión: {str(e)}'}
    
    def calcular_satisfaccion_promedio(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Calcula la satisfacción promedio de los usuarios
        
        Args:
            periodo_dias: Período en días para el cálculo
            
        Returns:
            Diccionario con métricas de satisfacción
        """
        try:
            fecha_limite = datetime.utcnow() - timedelta(days=periodo_dias)
            
            with self.db_service.get_session() as session:
                from models.feedback import Feedback
                
                # Obtener calificaciones del período
                calificaciones = session.query(Feedback.calificacion).filter(
                    Feedback.fecha >= fecha_limite,
                    Feedback.calificacion.isnot(None)
                ).all()
                
                if not calificaciones:
                    return {
                        'periodo_dias': periodo_dias,
                        'fecha_calculo': datetime.utcnow().isoformat(),
                        'satisfaccion_promedio': 0,
                        'total_calificaciones': 0,
                        'distribucion': {},
                        'tendencia': 'sin_datos'
                    }
                
                calificaciones_lista = [c[0] for c in calificaciones]
                
                # Calcular métricas
                satisfaccion_promedio = statistics.mean(calificaciones_lista)
                mediana = statistics.median(calificaciones_lista)
                desviacion = statistics.stdev(calificaciones_lista) if len(calificaciones_lista) > 1 else 0
                
                # Distribución de calificaciones
                distribucion = Counter(calificaciones_lista)
                
                # Calcular tendencia (comparar con período anterior)
                tendencia = self._calcular_tendencia_satisfaccion(periodo_dias, calificaciones_lista)
                
                return {
                    'periodo_dias': periodo_dias,
                    'fecha_calculo': datetime.utcnow().isoformat(),
                    'satisfaccion_promedio': round(satisfaccion_promedio, 2),
                    'mediana': round(mediana, 2),
                    'desviacion_estandar': round(desviacion, 2),
                    'total_calificaciones': len(calificaciones_lista),
                    'distribucion': dict(distribucion),
                    'tendencia': tendencia,
                    'calificacion_mas_frecuente': distribucion.most_common(1)[0][0] if distribucion else None
                }
                
        except Exception as e:
            self.logger.error(f"Error calculando satisfacción promedio: {e}")
            return {'error': f'Error calculando satisfacción: {str(e)}'}
    
    def calcular_tasa_mejora_ia(self, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Calcula la tasa de mejora de la IA
        
        Args:
            periodo_dias: Período en días para el cálculo
            
        Returns:
            Diccionario con métricas de mejora
        """
        try:
            fecha_limite = datetime.utcnow() - timedelta(days=periodo_dias)
            
            with self.db_service.get_session() as session:
                from models.acciones_ia import AccionIA
                from models.mejora_prompt import MejoraPrompt
                
                # Obtener acciones y mejoras del período
                acciones = session.query(AccionIA).filter(
                    AccionIA.fecha >= fecha_limite
                ).all()
                
                mejoras = session.query(MejoraPrompt).filter(
                    MejoraPrompt.fecha >= fecha_limite
                ).all()
                
                # Calcular métricas
                total_acciones = len(acciones)
                total_mejoras = len(mejoras)
                acciones_con_mejoras = len(set(m.id_accion for m in mejoras))
                
                tasa_mejora = (total_mejoras / total_acciones * 100) if total_acciones > 0 else 0
                cobertura_mejora = (acciones_con_mejoras / total_acciones * 100) if total_acciones > 0 else 0
                
                # Calcular confianza promedio de mejoras
                confianzas = [float(m.confianza) for m in mejoras if m.confianza is not None]
                confianza_promedio = statistics.mean(confianzas) if confianzas else 0
                
                # Calcular mejoras por tipo de acción
                mejoras_por_tipo = self._calcular_mejoras_por_tipo(acciones, mejoras)
                
                return {
                    'periodo_dias': periodo_dias,
                    'fecha_calculo': datetime.utcnow().isoformat(),
                    'total_acciones': total_acciones,
                    'total_mejoras': total_mejoras,
                    'acciones_con_mejoras': acciones_con_mejoras,
                    'tasa_mejora': round(tasa_mejora, 2),
                    'cobertura_mejora': round(cobertura_mejora, 2),
                    'confianza_promedio': round(confianza_promedio, 2),
                    'mejoras_por_tipo': mejoras_por_tipo
                }
                
        except Exception as e:
            self.logger.error(f"Error calculando tasa de mejora IA: {e}")
            return {'error': f'Error calculando mejora: {str(e)}'}
    
    def generar_reporte_completo(self) -> Dict[str, Any]:
        """
        Genera un reporte completo con todas las métricas
        
        Returns:
            Diccionario con reporte completo
        """
        try:
            reporte = {
                'fecha_generacion': datetime.utcnow().isoformat(),
                'metricas_generales': self.calcular_metricas_generales(),
                'precision_ia_30_dias': self.calcular_precision_ia(30),
                'precision_ia_7_dias': self.calcular_precision_ia(7),
                'satisfaccion_30_dias': self.calcular_satisfaccion_promedio(30),
                'satisfaccion_7_dias': self.calcular_satisfaccion_promedio(7),
                'mejora_ia_30_dias': self.calcular_tasa_mejora_ia(30),
                'mejora_ia_7_dias': self.calcular_tasa_mejora_ia(7),
                'resumen_ejecutivo': self._generar_resumen_ejecutivo()
            }
            
            self.logger.info("Reporte completo generado exitosamente")
            return reporte
            
        except Exception as e:
            self.logger.error(f"Error generando reporte completo: {e}")
            return {'error': f'Error generando reporte: {str(e)}'}
    
    def _calcular_metricas_rendimiento(self) -> Dict[str, Any]:
        """Calcula métricas de rendimiento del sistema"""
        try:
            with self.db_service.get_session() as session:
                from models.acciones_ia import AccionIA
                
                # Obtener acciones de los últimos 7 días
                fecha_limite = datetime.utcnow() - timedelta(days=7)
                acciones = session.query(AccionIA).filter(
                    AccionIA.fecha >= fecha_limite
                ).all()
                
                if not acciones:
                    return {'total_acciones': 0, 'tasa_exito': 0}
                
                acciones_exitosas = sum(1 for a in acciones if a.exito)
                tasa_exito = (acciones_exitosas / len(acciones)) * 100
                
                return {
                    'total_acciones_7_dias': len(acciones),
                    'tasa_exito': round(tasa_exito, 2),
                    'acciones_exitosas': acciones_exitosas,
                    'acciones_fallidas': len(acciones) - acciones_exitosas
                }
                
        except Exception as e:
            self.logger.error(f"Error calculando métricas de rendimiento: {e}")
            return {'error': str(e)}
    
    def _calcular_metricas_satisfaccion(self) -> Dict[str, Any]:
        """Calcula métricas de satisfacción"""
        return self.calcular_satisfaccion_promedio(7)
    
    def _calcular_metricas_mejora_ia(self) -> Dict[str, Any]:
        """Calcula métricas de mejora de IA"""
        return self.calcular_tasa_mejora_ia(7)
    
    def _calcular_tendencias(self) -> Dict[str, Any]:
        """Calcula tendencias del sistema"""
        try:
            # Comparar últimos 7 días vs 7 días anteriores
            ahora = datetime.utcnow()
            ultimos_7 = ahora - timedelta(days=7)
            anteriores_7 = ahora - timedelta(days=14)
            
            with self.db_service.get_session() as session:
                from models.feedback import Feedback
                from models.acciones_ia import AccionIA
                
                # Feedbacks
                feedbacks_recientes = session.query(Feedback).filter(
                    Feedback.fecha >= ultimos_7
                ).count()
                
                feedbacks_anteriores = session.query(Feedback).filter(
                    Feedback.fecha >= anteriores_7,
                    Feedback.fecha < ultimos_7
                ).count()
                
                # Acciones IA
                acciones_recientes = session.query(AccionIA).filter(
                    AccionIA.fecha >= ultimos_7
                ).count()
                
                acciones_anteriores = session.query(AccionIA).filter(
                    AccionIA.fecha >= anteriores_7,
                    AccionIA.fecha < ultimos_7
                ).count()
                
                return {
                    'feedbacks': {
                        'recientes': feedbacks_recientes,
                        'anteriores': feedbacks_anteriores,
                        'tendencia': 'creciendo' if feedbacks_recientes > feedbacks_anteriores else 'decreciendo'
                    },
                    'acciones_ia': {
                        'recientes': acciones_recientes,
                        'anteriores': acciones_anteriores,
                        'tendencia': 'creciendo' if acciones_recientes > acciones_anteriores else 'decreciendo'
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error calculando tendencias: {e}")
            return {'error': str(e)}
    
    def _calcular_precision_por_tipo_accion(self, acciones: List, feedbacks: List) -> Dict[str, Any]:
        """Calcula precisión por tipo de acción"""
        try:
            precision_por_tipo = {}
            
            for accion in acciones:
                tipo = accion.tipo_accion
                if tipo not in precision_por_tipo:
                    precision_por_tipo[tipo] = {'total': 0, 'exitosas': 0}
                
                precision_por_tipo[tipo]['total'] += 1
                if accion.exito:
                    precision_por_tipo[tipo]['exitosas'] += 1
            
            # Calcular porcentajes
            for tipo in precision_por_tipo:
                total = precision_por_tipo[tipo]['total']
                exitosas = precision_por_tipo[tipo]['exitosas']
                precision_por_tipo[tipo]['precision'] = round((exitosas / total) * 100, 2) if total > 0 else 0
            
            return precision_por_tipo
            
        except Exception as e:
            self.logger.error(f"Error calculando precisión por tipo: {e}")
            return {}
    
    def _calcular_tendencia_satisfaccion(self, periodo_dias: int, calificaciones_actuales: List[float]) -> str:
        """Calcula la tendencia de satisfacción"""
        try:
            # Obtener calificaciones del período anterior
            fecha_actual = datetime.utcnow()
            fecha_inicio_actual = fecha_actual - timedelta(days=periodo_dias)
            fecha_inicio_anterior = fecha_actual - timedelta(days=periodo_dias * 2)
            
            with self.db_service.get_session() as session:
                from models.feedback import Feedback
                
                calificaciones_anteriores = session.query(Feedback.calificacion).filter(
                    Feedback.fecha >= fecha_inicio_anterior,
                    Feedback.fecha < fecha_inicio_actual,
                    Feedback.calificacion.isnot(None)
                ).all()
                
                if not calificaciones_anteriores:
                    return 'sin_datos_anteriores'
                
                calificaciones_anteriores_lista = [c[0] for c in calificaciones_anteriores]
                
                promedio_actual = statistics.mean(calificaciones_actuales)
                promedio_anterior = statistics.mean(calificaciones_anteriores_lista)
                
                diferencia = promedio_actual - promedio_anterior
                
                if diferencia > 0.5:
                    return 'mejorando'
                elif diferencia < -0.5:
                    return 'empeorando'
                else:
                    return 'estable'
                    
        except Exception as e:
            self.logger.error(f"Error calculando tendencia de satisfacción: {e}")
            return 'error'
    
    def _calcular_mejoras_por_tipo(self, acciones: List, mejoras: List) -> Dict[str, Any]:
        """Calcula mejoras por tipo de acción"""
        try:
            mejoras_por_tipo = {}
            
            # Crear diccionario de acciones por ID
            acciones_dict = {a.id_accion: a for a in acciones}
            
            for mejora in mejoras:
                accion = acciones_dict.get(mejora.id_accion)
                if accion:
                    tipo = accion.tipo_accion
                    if tipo not in mejoras_por_tipo:
                        mejoras_por_tipo[tipo] = {'total': 0, 'mejoras': 0}
                    
                    mejoras_por_tipo[tipo]['total'] += 1
                    mejoras_por_tipo[tipo]['mejoras'] += 1
            
            # Calcular porcentajes
            for tipo in mejoras_por_tipo:
                total = mejoras_por_tipo[tipo]['total']
                mejoras_count = mejoras_por_tipo[tipo]['mejoras']
                mejoras_por_tipo[tipo]['porcentaje'] = round((mejoras_count / total) * 100, 2) if total > 0 else 0
            
            return mejoras_por_tipo
            
        except Exception as e:
            self.logger.error(f"Error calculando mejoras por tipo: {e}")
            return {}
    
    def _generar_resumen_ejecutivo(self) -> Dict[str, Any]:
        """Genera un resumen ejecutivo de las métricas"""
        try:
            metricas_generales = self.calcular_metricas_generales()
            precision_30 = self.calcular_precision_ia(30)
            satisfaccion_30 = self.calcular_satisfaccion_promedio(30)
            mejora_30 = self.calcular_tasa_mejora_ia(30)
            
            return {
                'estado_general': self._determinar_estado_general(metricas_generales, precision_30, satisfaccion_30),
                'puntos_fuertes': self._identificar_puntos_fuertes(metricas_generales, precision_30, satisfaccion_30),
                'areas_mejora': self._identificar_areas_mejora(metricas_generales, precision_30, satisfaccion_30),
                'recomendaciones': self._generar_recomendaciones(metricas_generales, precision_30, satisfaccion_30, mejora_30)
            }
            
        except Exception as e:
            self.logger.error(f"Error generando resumen ejecutivo: {e}")
            return {'error': str(e)}
    
    def _determinar_estado_general(self, metricas: Dict, precision: Dict, satisfaccion: Dict) -> str:
        """Determina el estado general del sistema"""
        try:
            precision_val = precision.get('precision_general', 0)
            satisfaccion_val = satisfaccion.get('satisfaccion_promedio', 0)
            
            if precision_val >= 80 and satisfaccion_val >= 4.0:
                return 'excelente'
            elif precision_val >= 70 and satisfaccion_val >= 3.5:
                return 'bueno'
            elif precision_val >= 60 and satisfaccion_val >= 3.0:
                return 'regular'
            else:
                return 'necesita_mejora'
                
        except Exception as e:
            self.logger.error(f"Error determinando estado general: {e}")
            return 'error'
    
    def _identificar_puntos_fuertes(self, metricas: Dict, precision: Dict, satisfaccion: Dict) -> List[str]:
        """Identifica puntos fuertes del sistema"""
        puntos = []
        
        try:
            if precision.get('precision_general', 0) >= 80:
                puntos.append("Alta precisión en análisis de menús")
            
            if satisfaccion.get('satisfaccion_promedio', 0) >= 4.0:
                puntos.append("Alta satisfacción de usuarios")
            
            if metricas.get('estadisticas_basicas', {}).get('total_usuarios', 0) > 100:
                puntos.append("Base de usuarios sólida")
            
            if metricas.get('estadisticas_basicas', {}).get('total_platos', 0) > 500:
                puntos.append("Amplia base de datos de platos")
            
        except Exception as e:
            self.logger.error(f"Error identificando puntos fuertes: {e}")
        
        return puntos
    
    def _identificar_areas_mejora(self, metricas: Dict, precision: Dict, satisfaccion: Dict) -> List[str]:
        """Identifica áreas que necesitan mejora"""
        areas = []
        
        try:
            if precision.get('precision_general', 0) < 70:
                areas.append("Mejorar precisión del análisis de menús")
            
            if satisfaccion.get('satisfaccion_promedio', 0) < 3.5:
                areas.append("Mejorar satisfacción del usuario")
            
            if precision.get('tasa_correccion', 0) > 20:
                areas.append("Reducir tasa de correcciones necesarias")
            
            if satisfaccion.get('total_calificaciones', 0) < 10:
                areas.append("Aumentar participación de usuarios en feedback")
            
        except Exception as e:
            self.logger.error(f"Error identificando áreas de mejora: {e}")
        
        return areas
    
    def _generar_recomendaciones(self, metricas: Dict, precision: Dict, satisfaccion: Dict, mejora: Dict) -> List[str]:
        """Genera recomendaciones basadas en las métricas"""
        recomendaciones = []
        
        try:
            if precision.get('precision_general', 0) < 80:
                recomendaciones.append("Implementar mejoras en los prompts de análisis")
            
            if satisfaccion.get('satisfaccion_promedio', 0) < 4.0:
                recomendaciones.append("Mejorar la experiencia de usuario")
            
            if mejora.get('tasa_mejora', 0) < 50:
                recomendaciones.append("Aumentar la frecuencia de mejoras automáticas")
            
            if satisfaccion.get('total_calificaciones', 0) < 20:
                recomendaciones.append("Implementar incentivos para feedback de usuarios")
            
        except Exception as e:
            self.logger.error(f"Error generando recomendaciones: {e}")
        
        return recomendaciones
    
    def calcular_metricas_auto_mejora(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Calcula métricas de auto-mejora entre Run 1 y Run 2
        
        Args:
            period_days: Período en días para el cálculo
            
        Returns:
            Diccionario con métricas de auto-mejora
        """
        try:
            with self.db_service.get_session() as session:
                fecha_limite = datetime.utcnow() - timedelta(days=period_days)
                
                # Obtener acciones de IA del período
                acciones = session.query(AccionIA).filter(
                    AccionIA.fecha >= fecha_limite
                ).all()
                
                # Separar Run 1 y Run 2 basándose en mejoras aplicadas
                run1_acciones = []
                run2_acciones = []
                
                for accion in acciones:
                    # Si tiene mejoras asociadas, es Run 2
                    if hasattr(accion, 'mejoras') and accion.mejoras:
                        run2_acciones.append(accion)
                    else:
                        run1_acciones.append(accion)
                
                # Calcular métricas Run 1
                run1_metricas = self._calcular_metricas_run(run1_acciones, "Run 1")
                
                # Calcular métricas Run 2
                run2_metricas = self._calcular_metricas_run(run2_acciones, "Run 2")
                
                # Calcular mejoras
                mejoras = self._calcular_mejoras_entre_runs(run1_metricas, run2_metricas)
                
                return {
                    'run1_metricas': run1_metricas,
                    'run2_metricas': run2_metricas,
                    'mejoras': mejoras,
                    'periodo_dias': period_days,
                    'fecha_calculo': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error calculando métricas de auto-mejora: {e}")
            return {
                'run1_metricas': {'precision': 0.0, 'satisfaccion': 0.0, 'tiempo_respuesta': 0.0},
                'run2_metricas': {'precision': 0.0, 'satisfaccion': 0.0, 'tiempo_respuesta': 0.0},
                'mejoras': {'precision_mejora': 0.0, 'satisfaccion_mejora': 0.0, 'tiempo_mejora': 0.0},
                'error': str(e)
            }
    
    def _calcular_metricas_run(self, acciones: List[Any], run_name: str) -> Dict[str, float]:
        """
        Calcula métricas para un run específico
        
        Args:
            acciones: Lista de acciones del run
            run_name: Nombre del run
            
        Returns:
            Diccionario con métricas del run
        """
        if not acciones:
            return {'precision': 0.0, 'satisfaccion': 0.0, 'tiempo_respuesta': 0.0}
        
        # Calcular precisión (tasa de éxito)
        acciones_exitosas = sum(1 for a in acciones if a.exito)
        precision = acciones_exitosas / len(acciones) if acciones else 0.0
        
        # Calcular satisfacción promedio (simulado)
        satisfaccion = min(5.0, precision * 5.0)  # Escalar a 1-5
        
        # Calcular tiempo de respuesta promedio (simulado)
        tiempo_respuesta = 2.0 - (precision * 1.0)  # Mejor precisión = menor tiempo
        
        return {
            'precision': round(precision * 100, 1),  # Porcentaje
            'satisfaccion': round(satisfaccion, 1),
            'tiempo_respuesta': round(tiempo_respuesta, 1)
        }
    
    def _calcular_mejoras_entre_runs(self, run1: Dict[str, float], run2: Dict[str, float]) -> Dict[str, float]:
        """
        Calcula las mejoras entre Run 1 y Run 2
        
        Args:
            run1: Métricas del Run 1
            run2: Métricas del Run 2
            
        Returns:
            Diccionario con las mejoras
        """
        return {
            'precision_mejora': round(run2['precision'] - run1['precision'], 1),
            'satisfaccion_mejora': round(run2['satisfaccion'] - run1['satisfaccion'], 1),
            'tiempo_mejora': round(run1['tiempo_respuesta'] - run2['tiempo_respuesta'], 1)
        }
    
    def obtener_metricas_acciones_ia(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Obtiene métricas de acciones de IA
        
        Args:
            period_days: Período en días
            
        Returns:
            Diccionario con métricas de acciones
        """
        try:
            with self.db_service.get_session() as session:
                fecha_limite = datetime.utcnow() - timedelta(days=period_days)
                
                total_acciones = session.query(AccionIA).filter(
                    AccionIA.fecha >= fecha_limite
                ).count()
                
                acciones_exitosas = session.query(AccionIA).filter(
                    AccionIA.fecha >= fecha_limite,
                    AccionIA.exito == True
                ).count()
                
                tasa_exito = (acciones_exitosas / total_acciones * 100) if total_acciones > 0 else 0
                
                return {
                    'total_acciones': total_acciones,
                    'acciones_exitosas': acciones_exitosas,
                    'tasa_exito': round(tasa_exito, 1)
                }
                
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas de acciones: {e}")
            return {
                'total_acciones': 0,
                'acciones_exitosas': 0,
                'tasa_exito': 0.0,
                'error': str(e)
            }
    
    def obtener_metricas_mejoras_prompt(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Obtiene métricas de mejoras de prompt
        
        Args:
            period_days: Período en días
            
        Returns:
            Diccionario con métricas de mejoras
        """
        try:
            with self.db_service.get_session() as session:
                fecha_limite = datetime.utcnow() - timedelta(days=period_days)
                
                # Obtener mejoras de prompt del período
                total_mejoras = session.query(MejoraPrompt).join(AccionIA).filter(
                    AccionIA.fecha >= fecha_limite
                ).count()
                
                # Contar mejoras aplicadas (acciones exitosas con mejoras)
                mejoras_aplicadas = session.query(MejoraPrompt).join(AccionIA).filter(
                    AccionIA.fecha >= fecha_limite,
                    AccionIA.exito == True
                ).count()
                
                tasa_aplicacion = (mejoras_aplicadas / total_mejoras * 100) if total_mejoras > 0 else 0
                
                return {
                    'total_mejoras': total_mejoras,
                    'mejoras_aplicadas': mejoras_aplicadas,
                    'tasa_aplicacion': round(tasa_aplicacion, 1)
                }
                
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas de mejoras: {e}")
            return {
                'total_mejoras': 0,
                'mejoras_aplicadas': 0,
                'tasa_aplicacion': 0.0,
                'error': str(e)
            }
