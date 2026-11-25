"""
Templates de prompts para AliMentor AI
"""
import logging
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class PromptTemplates:
    """
    Clase para gestionar templates de prompts para OpenAI
    """
    
    def __init__(self):
        """Inicializa los templates de prompts"""
        self.logger = logger
    
    def get_analisis_menu_prompt(self, menu_text: str) -> str:
        """
        Genera el prompt para análisis de menú
        
        Args:
            menu_text: Texto del menú a analizar
            
        Returns:
            Prompt formateado para análisis
        """
        prompt = f"""
Analiza el siguiente menú de restaurante y extrae información detallada en formato JSON.

MENÚ A ANALIZAR:
{menu_text}

INSTRUCCIONES:
1. Identifica todos los platos mencionados
2. Para cada plato, extrae:
   - Nombre exacto del plato
   - Descripción (si está disponible)
   - Categoría (entrada, plato principal, postre, bebida, etc.)
   - Lista completa de ingredientes detectados
   - Alérgenos potenciales (gluten, lactosa, frutos secos, mariscos, etc.)
   - Precio estimado (si está disponible)

3. Genera recomendaciones nutricionales generales
4. Identifica posibles restricciones dietéticas

FORMATO DE RESPUESTA (JSON):
{{
    "platos_detectados": [
        {{
            "nombre": "Nombre del plato",
            "descripcion": "Descripción del plato",
            "categoria": "categoria",
            "ingredientes": ["ingrediente1", "ingrediente2"],
            "alergenos_detectados": ["alergeno1", "alergeno2"],
            "precio": 15.50
        }}
    ],
    "ingredientes_totales": ["lista", "de", "todos", "los", "ingredientes"],
    "alergenos_detectados": ["lista", "de", "alergenos", "encontrados"],
    "recomendaciones": [
        "Recomendación nutricional 1",
        "Recomendación nutricional 2"
    ],
    "resumen": "Resumen general del análisis del menú"
}}

IMPORTANTE:
- Sé preciso en la detección de ingredientes
- Identifica TODOS los alérgenos potenciales
- Si no puedes determinar algo, usa "no_detectado"
- Mantén el formato JSON válido
- Responde únicamente con el JSON, sin texto adicional
"""
        return prompt.strip()
    
    def get_recomendaciones_prompt(self, restricciones: List[str]) -> str:
        """
        Genera el prompt para recomendaciones personalizadas
        
        Args:
            restricciones: Lista de restricciones del usuario
            
        Returns:
            Prompt formateado para recomendaciones
        """
        restricciones_text = ", ".join(restricciones) if restricciones else "ninguna restricción específica"
        
        prompt = f"""
Genera recomendaciones alimentarias personalizadas basadas en las restricciones del usuario.

RESTRICCIONES DEL USUARIO:
{restricciones_text}

INSTRUCCIONES:
1. Proporciona recomendaciones específicas para cada restricción
2. Sugiere alternativas saludables
3. Incluye consejos nutricionales generales
4. Considera la variedad y el equilibrio nutricional

FORMATO DE RESPUESTA (JSON):
{{
    "recomendaciones_generales": "Recomendaciones generales para el usuario",
    "alimentos_recomendados": [
        "Alimento recomendado 1",
        "Alimento recomendado 2"
    ],
    "alimentos_evitar": [
        "Alimento a evitar 1",
        "Alimento a evitar 2"
    ],
    "consejos_nutricionales": [
        "Consejo nutricional 1",
        "Consejo nutricional 2"
    ],
    "alternativas_saludables": [
        "Alternativa saludable 1",
        "Alternativa saludable 2"
    ]
}}

IMPORTANTE:
- Sé específico y práctico en las recomendaciones
- Considera la seguridad alimentaria
- Proporciona alternativas realistas
- Mantén el formato JSON válido
- Responde únicamente con el JSON, sin texto adicional
"""
        return prompt.strip()
    
    def get_mejora_prompt_prompt(self, feedback_text: str) -> str:
        """
        Genera el prompt para mejorar prompts basándose en feedback
        
        Args:
            feedback_text: Texto del feedback analizado
            
        Returns:
            Prompt formateado para mejora de prompts
        """
        prompt = f"""
Analiza el siguiente feedback de usuarios sobre el análisis de menús y sugiere mejoras específicas para los prompts de IA.

FEEDBACK DE USUARIOS:
{feedback_text}

INSTRUCCIONES:
1. Identifica patrones en los errores reportados
2. Sugiere mejoras específicas para el prompt de análisis de menús
3. Proporciona un prompt mejorado que corrija los problemas identificados
4. Explica las razones de cada mejora

FORMATO DE RESPUESTA (JSON):
{{
    "ajuste_prompt": "Prompt mejorado completo para análisis de menús",
    "observacion": "Observación general sobre las mejoras",
    "patrones_detectados": [
        "Patrón de error 1",
        "Patrón de error 2"
    ],
    "sugerencias_especificas": [
        "Sugerencia específica 1",
        "Sugerencia específica 2"
    ],
    "mejoras_implementadas": [
        "Mejora implementada 1",
        "Mejora implementada 2"
    ]
}}

IMPORTANTE:
- Sé específico en las mejoras sugeridas
- Basa las mejoras en el feedback real
- Proporciona un prompt completo y funcional
- Explica claramente cada mejora
- Mantén el formato JSON válido
- Responde únicamente con el JSON, sin texto adicional
"""
        return prompt.strip()
    
    def get_validacion_plato_prompt(self, plato_data: Dict[str, Any]) -> str:
        """
        Genera el prompt para validar datos de un plato
        
        Args:
            plato_data: Datos del plato a validar
            
        Returns:
            Prompt formateado para validación
        """
        plato_json = json.dumps(plato_data, ensure_ascii=False, indent=2)
        
        prompt = f"""
Valida y mejora los siguientes datos de un plato analizado por IA.

DATOS DEL PLATO:
{plato_json}

INSTRUCCIONES:
1. Verifica la precisión de los ingredientes detectados
2. Valida la detección de alérgenos
3. Corrige errores obvios
4. Sugiere mejoras en la clasificación
5. Asegúrate de que los datos sean coherentes

FORMATO DE RESPUESTA (JSON):
{{
    "datos_validados": {{
        "nombre": "Nombre corregido del plato",
        "descripcion": "Descripción mejorada",
        "categoria": "Categoría corregida",
        "ingredientes": ["ingrediente1", "ingrediente2"],
        "alergenos_detectados": ["alergeno1", "alergeno2"],
        "precio": 15.50
    }},
    "correcciones_realizadas": [
        "Corrección 1",
        "Corrección 2"
    ],
    "confianza_validacion": 0.85,
    "observaciones": "Observaciones sobre la validación"
}}

IMPORTANTE:
- Mantén la estructura original de datos
- Solo corrige errores obvios
- Proporciona una puntuación de confianza (0.0-1.0)
- Explica las correcciones realizadas
- Mantén el formato JSON válido
- Responde únicamente con el JSON, sin texto adicional
"""
        return prompt.strip()
    
    def get_analisis_feedback_prompt(self, feedbacks: List[Dict[str, Any]]) -> str:
        """
        Genera el prompt para análisis de feedback
        
        Args:
            feedbacks: Lista de feedbacks a analizar
            
        Returns:
            Prompt formateado para análisis de feedback
        """
        feedback_text = ""
        for i, feedback in enumerate(feedbacks, 1):
            feedback_text += f"Feedback {i}:\n"
            feedback_text += f"- Tipo: {feedback.get('tipo_feedback', 'N/A')}\n"
            feedback_text += f"- Calificación: {feedback.get('calificacion', 'N/A')}\n"
            feedback_text += f"- Comentario: {feedback.get('comentario', 'N/A')}\n"
            feedback_text += f"- Fecha: {feedback.get('fecha', 'N/A')}\n\n"
        
        prompt = f"""
Analiza el siguiente conjunto de feedbacks de usuarios y proporciona insights para mejorar el sistema.

FEEDBACKS A ANALIZAR:
{feedback_text}

INSTRUCCIONES:
1. Identifica patrones comunes en los feedbacks
2. Detecta problemas recurrentes
3. Sugiere mejoras específicas
4. Calcula métricas de satisfacción
5. Prioriza las mejoras más importantes

FORMATO DE RESPUESTA (JSON):
{{
    "resumen_analisis": "Resumen general del análisis",
    "patrones_identificados": [
        "Patrón 1",
        "Patrón 2"
    ],
    "problemas_recurrentes": [
        "Problema 1",
        "Problema 2"
    ],
    "mejoras_sugeridas": [
        "Mejora 1",
        "Mejora 2"
    ],
    "metricas_calculadas": {{
        "satisfaccion_promedio": 4.2,
        "tasa_feedback_negativo": 15.5,
        "problemas_mas_frecuentes": ["problema1", "problema2"]
    }},
    "prioridades_mejora": [
        "Prioridad alta: mejora 1",
        "Prioridad media: mejora 2"
    ]
}}

IMPORTANTE:
- Sé objetivo en el análisis
- Identifica patrones claros
- Proporciona métricas cuantificables
- Prioriza las mejoras por impacto
- Mantén el formato JSON válido
- Responde únicamente con el JSON, sin texto adicional
"""
        return prompt.strip()
    
    def get_prompt_mejorado_analisis(self, mejoras: Dict[str, Any]) -> str:
        """
        Genera un prompt de análisis mejorado basándose en mejoras previas
        
        Args:
            mejoras: Diccionario con mejoras aplicadas
            
        Returns:
            Prompt mejorado para análisis de menús
        """
        # Prompt base mejorado
        prompt_base = """
Analiza el siguiente menú de restaurante con máxima precisión y extrae información detallada en formato JSON.

MENÚ A ANALIZAR:
{menu_text}

INSTRUCCIONES MEJORADAS:
1. LEE CUIDADOSAMENTE cada palabra del menú
2. Para cada plato, extrae:
   - Nombre exacto del plato (sin modificaciones)
   - Descripción completa (si está disponible)
   - Categoría precisa (entrada, plato principal, postre, bebida, etc.)
   - Lista EXHAUSTIVA de ingredientes (incluyendo salsas, condimentos, guarniciones)
   - Alérgenos potenciales (gluten, lactosa, frutos secos, mariscos, soja, huevos, etc.)
   - Precio exacto (si está disponible)

3. VALIDACIÓN CRUZADA:
   - Verifica que los ingredientes sean coherentes con el nombre del plato
   - Confirma que los alérgenos detectados sean lógicos
   - Asegúrate de que la categoría sea apropiada

4. GENERA recomendaciones nutricionales específicas y útiles
5. IDENTIFICA restricciones dietéticas potenciales

FORMATO DE RESPUESTA (JSON):
{{
    "platos_detectados": [
        {{
            "nombre": "Nombre exacto del plato",
            "descripcion": "Descripción completa",
            "categoria": "categoria_precisa",
            "ingredientes": ["ingrediente1", "ingrediente2", "ingrediente3"],
            "alergenos_detectados": ["alergeno1", "alergeno2"],
            "precio": 15.50,
            "nivel_confianza": 0.95
        }}
    ],
    "ingredientes_totales": ["lista", "completa", "de", "todos", "los", "ingredientes"],
    "alergenos_detectados": ["lista", "completa", "de", "alergenos"],
    "recomendaciones": [
        "Recomendación nutricional específica 1",
        "Recomendación nutricional específica 2"
    ],
    "restricciones_dieteticas": [
        "Restricción 1",
        "Restricción 2"
    ],
    "resumen": "Resumen detallado del análisis",
    "nivel_confianza_general": 0.90
}}

IMPORTANTE:
- MÁXIMA PRECISIÓN en la detección de ingredientes
- IDENTIFICA TODOS los alérgenos potenciales (incluso ocultos)
- Si no puedes determinar algo, usa "no_detectado"
- Mantén el formato JSON válido
- Responde únicamente con el JSON, sin texto adicional
- Incluye nivel de confianza para cada detección
"""
        
        # Aplicar mejoras específicas si están disponibles
        if mejoras.get('patrones_detectados'):
            patrones = mejoras['patrones_detectados']
            if 'ingrediente_no_detectado' in patrones:
                prompt_base += "\n\nATENCIÓN ESPECIAL: Revisa cuidadosamente todos los ingredientes, incluyendo salsas, condimentos y guarniciones que puedan no ser obvios."
            
            if 'alergeno_no_detectado' in patrones:
                prompt_base += "\n\nATENCIÓN ESPECIAL: Identifica TODOS los alérgenos potenciales, incluyendo aquellos que puedan estar ocultos en salsas o condimentos."
        
        return prompt_base.strip()
    
    def get_prompt_especializado_categoria(self, categoria: str) -> str:
        """
        Genera un prompt especializado para una categoría específica de platos
        
        Args:
            categoria: Categoría del plato (entrada, principal, postre, etc.)
            
        Returns:
            Prompt especializado para la categoría
        """
        especializaciones = {
            'entrada': {
                'ingredientes_comunes': ['lechuga', 'tomate', 'cebolla', 'queso', 'pan', 'aceite', 'vinagre'],
                'alergenos_tipicos': ['gluten', 'lactosa', 'frutos_secos'],
                'consideraciones': 'Las entradas suelen tener ingredientes frescos y salsas ligeras'
            },
            'plato_principal': {
                'ingredientes_comunes': ['carne', 'pollo', 'pescado', 'arroz', 'pasta', 'papas', 'vegetales'],
                'alergenos_tipicos': ['gluten', 'lactosa', 'mariscos', 'huevos'],
                'consideraciones': 'Los platos principales suelen tener proteínas, carbohidratos y vegetales'
            },
            'postre': {
                'ingredientes_comunes': ['azucar', 'harina', 'huevos', 'leche', 'mantequilla', 'frutas'],
                'alergenos_tipicos': ['gluten', 'lactosa', 'huevos', 'frutos_secos'],
                'consideraciones': 'Los postres suelen contener azúcares y alérgenos comunes'
            },
            'bebida': {
                'ingredientes_comunes': ['agua', 'azucar', 'frutas', 'hierbas', 'alcohol'],
                'alergenos_tipicos': ['lactosa', 'frutos_secos', 'soja'],
                'consideraciones': 'Las bebidas pueden contener alérgenos ocultos en jarabes o leches'
            }
        }
        
        especializacion = especializaciones.get(categoria.lower(), especializaciones['plato_principal'])
        
        prompt = f"""
Analiza este menú de {categoria} con especial atención a las características típicas de esta categoría.

CATEGORÍA: {categoria.upper()}

CARACTERÍSTICAS ESPECÍFICAS:
- Ingredientes comunes: {', '.join(especializacion['ingredientes_comunes'])}
- Alérgenos típicos: {', '.join(especializacion['alergenos_tipicos'])}
- Consideraciones: {especializacion['consideraciones']}

INSTRUCCIONES ESPECIALIZADAS:
1. Presta especial atención a los ingredientes típicos de {categoria}
2. Verifica cuidadosamente los alérgenos comunes en esta categoría
3. Considera las características nutricionales específicas de {categoria}
4. Aplica el formato JSON estándar pero con enfoque especializado

IMPORTANTE:
- Usa tu conocimiento especializado sobre {categoria}
- Identifica ingredientes que puedan no ser obvios en esta categoría
- Considera las preparaciones típicas de {categoria}
"""
        
        return prompt.strip()
    
    def get_prompt_validacion_cross_reference(self, plato_data: Dict[str, Any], base_conocimiento: List[Dict[str, Any]]) -> str:
        """
        Genera un prompt para validación cruzada con base de conocimiento
        
        Args:
            plato_data: Datos del plato a validar
            base_conocimiento: Base de conocimiento de platos similares
            
        Returns:
            Prompt para validación cruzada
        """
        plato_json = json.dumps(plato_data, ensure_ascii=False, indent=2)
        base_json = json.dumps(base_conocimiento[:5], ensure_ascii=False, indent=2)  # Solo primeros 5 para no sobrecargar
        
        prompt = f"""
Valida los siguientes datos de plato comparándolos con una base de conocimiento de platos similares.

DATOS DEL PLATO A VALIDAR:
{plato_json}

BASE DE CONOCIMIENTO (PLATOS SIMILARES):
{base_json}

INSTRUCCIONES:
1. Compara los ingredientes con platos similares en la base de conocimiento
2. Verifica la coherencia de alérgenos detectados
3. Valida la categorización del plato
4. Sugiere correcciones basadas en patrones de la base de conocimiento
5. Calcula un nivel de confianza basado en la similitud

FORMATO DE RESPUESTA (JSON):
{{
    "datos_validados": {{
        "nombre": "Nombre validado",
        "ingredientes": ["ingrediente1", "ingrediente2"],
        "alergenos_detectados": ["alergeno1", "alergeno2"],
        "categoria": "categoria_validada"
    }},
    "comparacion_base_conocimiento": {{
        "platos_similares_encontrados": 3,
        "similitud_promedio": 0.85,
        "ingredientes_faltantes": ["ingrediente1"],
        "ingredientes_extra": ["ingrediente2"]
    }},
    "correcciones_aplicadas": [
        "Corrección 1",
        "Corrección 2"
    ],
    "nivel_confianza": 0.90,
    "observaciones": "Observaciones sobre la validación cruzada"
}}

IMPORTANTE:
- Usa la base de conocimiento como referencia
- Aplica correcciones solo si son justificadas
- Calcula métricas de similitud
- Mantén el formato JSON válido
- Responde únicamente con el JSON, sin texto adicional
"""
        
        return prompt.strip()
