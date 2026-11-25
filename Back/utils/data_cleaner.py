"""
Utilidades de limpieza y procesamiento de datos para AliMentor AI
"""
import re
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import unicodedata

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Clase para limpiar y procesar datos de menús y platos
    """
    
    def __init__(self):
        """Inicializa el limpiador de datos"""
        self.logger = logger
        
        # Patrones de limpieza
        self.patrones_limpieza = {
            'precios': r'[\$€£¥]\s*(\d+(?:\.\d{2})?)',
            'medidas': r'\b(\d+(?:\.\d+)?)\s*(ml|cl|litros?|kg|g|gramos?|onzas?|libras?)\b',
            'porciones': r'\b(\d+)\s*(porciones?|personas?|servings?)\b',
            'telefonos': r'(\+?[\d\s\-\(\)]{10,})',
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'urls': r'https?://[^\s]+',
            'simbolos_especiales': r'[^\w\s\.,;:!?\-\(\)\[\]\/]'
        }
        
        # Listas de ingredientes comunes para validación
        self.ingredientes_comunes = {
            'vegetales': ['tomate', 'cebolla', 'lechuga', 'zanahoria', 'apio', 'pepino', 'pimiento', 'ajo', 'perejil', 'cilantro'],
            'carnes': ['pollo', 'res', 'cerdo', 'cordero', 'pavo', 'jamón', 'tocino', 'chorizo', 'salchicha'],
            'pescados': ['salmón', 'atún', 'bacalao', 'merluza', 'lenguado', 'trucha', 'camarón', 'langosta', 'cangrejo'],
            'lacteos': ['leche', 'queso', 'mantequilla', 'yogur', 'crema', 'nata', 'mozzarella', 'cheddar', 'parmesano'],
            'cereales': ['arroz', 'pasta', 'pan', 'harina', 'trigo', 'avena', 'quinoa', 'cebada', 'centeno'],
            'frutas': ['manzana', 'plátano', 'naranja', 'limón', 'fresa', 'uva', 'piña', 'mango', 'kiwi'],
            'especias': ['sal', 'pimienta', 'orégano', 'albahaca', 'tomillo', 'romero', 'comino', 'canela', 'nuez_moscada']
        }
        
        # Lista de alérgenos comunes
        self.alergenos_comunes = [
            'gluten', 'trigo', 'cebada', 'centeno', 'avena',
            'lactosa', 'leche', 'queso', 'mantequilla', 'yogur',
            'huevos', 'clara', 'yema',
            'frutos_secos', 'nueces', 'almendras', 'avellanas', 'pistachos',
            'mariscos', 'camarones', 'langosta', 'cangrejo', 'ostras',
            'soja', 'soya', 'tofu', 'miso',
            'mostaza', 'sésamo', 'apio', 'sulfitos'
        ]
    
    def limpiar_texto_menu(self, texto: str) -> str:
        """
        Limpia el texto de un menú eliminando información irrelevante
        
        Args:
            texto: Texto del menú a limpiar
            
        Returns:
            Texto limpio del menú
        """
        try:
            # Normalizar caracteres especiales
            texto = self._normalizar_caracteres(texto)
            
            # Eliminar información de contacto
            texto = self._eliminar_informacion_contacto(texto)
            
            # Limpiar formato y espacios
            texto = self._limpiar_formato(texto)
            
            # Eliminar líneas vacías excesivas
            texto = self._eliminar_lineas_vacias(texto)
            
            self.logger.info("Texto de menú limpiado exitosamente")
            return texto.strip()
            
        except Exception as e:
            self.logger.error(f"Error limpiando texto de menú: {e}")
            return texto
    
    def extraer_platos_del_texto(self, texto: str) -> List[Dict[str, Any]]:
        """
        Extrae platos del texto de menú usando patrones
        
        Args:
            texto: Texto del menú
            
        Returns:
            Lista de platos extraídos
        """
        try:
            platos = []
            lineas = texto.split('\n')
            
            plato_actual = None
            
            for i, linea in enumerate(lineas):
                linea = linea.strip()
                if not linea:
                    continue
                
                # Detectar inicio de plato (patrones comunes)
                if self._es_inicio_plato(linea):
                    # Guardar plato anterior si existe
                    if plato_actual:
                        platos.append(plato_actual)
                    
                    # Crear nuevo plato
                    plato_actual = {
                        'nombre': self._extraer_nombre_plato(linea),
                        'descripcion': '',
                        'precio': self._extraer_precio(linea),
                        'categoria': self._detectar_categoria_plato(linea),
                        'linea_inicio': i
                    }
                
                # Agregar descripción si estamos en un plato
                elif plato_actual and self._es_descripcion_plato(linea):
                    if plato_actual['descripcion']:
                        plato_actual['descripcion'] += ' ' + linea
                    else:
                        plato_actual['descripcion'] = linea
                
                # Detectar fin de plato
                elif plato_actual and self._es_fin_plato(linea):
                    platos.append(plato_actual)
                    plato_actual = None
            
            # Agregar último plato si existe
            if plato_actual:
                platos.append(plato_actual)
            
            self.logger.info(f"Extraídos {len(platos)} platos del texto")
            return platos
            
        except Exception as e:
            self.logger.error(f"Error extrayendo platos del texto: {e}")
            return []
    
    def limpiar_ingredientes(self, ingredientes: List[str]) -> List[str]:
        """
        Limpia y normaliza una lista de ingredientes
        
        Args:
            ingredientes: Lista de ingredientes a limpiar
            
        Returns:
            Lista de ingredientes limpios
        """
        try:
            ingredientes_limpios = []
            
            for ingrediente in ingredientes:
                if not ingrediente or not ingrediente.strip():
                    continue
                
                # Limpiar ingrediente individual
                ingrediente_limpio = self._limpiar_ingrediente_individual(ingrediente)
                
                if ingrediente_limpio and ingrediente_limpio not in ingredientes_limpios:
                    ingredientes_limpios.append(ingrediente_limpio)
            
            self.logger.info(f"Limpieza de ingredientes: {len(ingredientes)} -> {len(ingredientes_limpios)}")
            return ingredientes_limpios
            
        except Exception as e:
            self.logger.error(f"Error limpiando ingredientes: {e}")
            return ingredientes
    
    def detectar_alergenos(self, texto: str) -> List[str]:
        """
        Detecta alérgenos en un texto
        
        Args:
            texto: Texto a analizar
            
        Returns:
            Lista de alérgenos detectados
        """
        try:
            alergenos_detectados = []
            texto_lower = texto.lower()
            
            for alergeno in self.alergenos_comunes:
                if alergeno.lower() in texto_lower:
                    alergenos_detectados.append(alergeno)
            
            # Detectar patrones de alérgenos
            patrones_alergenos = [
                r'\b(?:contiene|incluye|tiene)\s+([^,\.]+)',
                r'\b(?:sin|libre de)\s+([^,\.]+)',
                r'\b(?:alérgeno|alergeno)s?\s*:?\s*([^,\.]+)'
            ]
            
            for patron in patrones_alergenos:
                matches = re.findall(patron, texto_lower, re.IGNORECASE)
                for match in matches:
                    alergenos_encontrados = self._extraer_alergenos_de_texto(match)
                    alergenos_detectados.extend(alergenos_encontrados)
            
            # Eliminar duplicados y normalizar
            alergenos_unicos = list(set(alergenos_detectados))
            alergenos_unicos.sort()
            
            self.logger.info(f"Alérgenos detectados: {alergenos_unicos}")
            return alergenos_unicos
            
        except Exception as e:
            self.logger.error(f"Error detectando alérgenos: {e}")
            return []
    
    def validar_datos_plato(self, plato_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida y corrige datos de un plato
        
        Args:
            plato_data: Datos del plato a validar
            
        Returns:
            Diccionario con datos validados y correcciones
        """
        try:
            datos_validados = plato_data.copy()
            correcciones = []
            
            # Validar nombre
            if not datos_validados.get('nombre') or not datos_validados['nombre'].strip():
                correcciones.append("Nombre de plato vacío o inválido")
                datos_validados['nombre'] = "Plato sin nombre"
            
            # Validar y limpiar ingredientes
            if 'ingredientes' in datos_validados:
                ingredientes_originales = datos_validados['ingredientes']
                ingredientes_limpios = self.limpiar_ingredientes(ingredientes_originales)
                
                if ingredientes_limpios != ingredientes_originales:
                    correcciones.append("Ingredientes limpiados y normalizados")
                    datos_validados['ingredientes'] = ingredientes_limpios
            
            # Validar alérgenos
            if 'alergenos_detectados' in datos_validados:
                alergenos_originales = datos_validados['alergenos_detectados']
                alergenos_validados = self._validar_alergenos(alergenos_originales)
                
                if alergenos_validados != alergenos_originales:
                    correcciones.append("Alérgenos validados y corregidos")
                    datos_validados['alergenos_detectados'] = alergenos_validados
            
            # Validar categoría
            if 'categoria' in datos_validados:
                categoria_original = datos_validados['categoria']
                categoria_validada = self._validar_categoria(categoria_original)
                
                if categoria_validada != categoria_original:
                    correcciones.append(f"Categoría corregida: {categoria_original} -> {categoria_validada}")
                    datos_validados['categoria'] = categoria_validada
            
            # Validar precio
            if 'precio' in datos_validados:
                precio_original = datos_validados['precio']
                precio_validado = self._validar_precio(precio_original)
                
                if precio_validado != precio_original:
                    correcciones.append(f"Precio corregido: {precio_original} -> {precio_validado}")
                    datos_validados['precio'] = precio_validado
            
            return {
                'datos_validados': datos_validados,
                'correcciones': correcciones,
                'valido': len(correcciones) == 0,
                'fecha_validacion': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error validando datos de plato: {e}")
            return {
                'datos_validados': plato_data,
                'correcciones': [f"Error en validación: {str(e)}"],
                'valido': False,
                'fecha_validacion': datetime.utcnow().isoformat()
            }
    
    def normalizar_texto(self, texto: str) -> str:
        """
        Normaliza texto eliminando acentos y caracteres especiales
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            Texto normalizado
        """
        try:
            # Normalizar caracteres Unicode
            texto = unicodedata.normalize('NFD', texto)
            
            # Eliminar acentos
            texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
            
            # Convertir a minúsculas
            texto = texto.lower()
            
            # Eliminar caracteres especiales excepto espacios y puntuación básica
            texto = re.sub(r'[^\w\s\.,;:!?\-\(\)]', '', texto)
            
            # Limpiar espacios múltiples
            texto = re.sub(r'\s+', ' ', texto)
            
            return texto.strip()
            
        except Exception as e:
            self.logger.error(f"Error normalizando texto: {e}")
            return texto
    
    def _normalizar_caracteres(self, texto: str) -> str:
        """Normaliza caracteres especiales en el texto"""
        # Reemplazar caracteres problemáticos
        reemplazos = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',
            '—': '-',
            '…': '...',
            '°': 'o',
            '½': '1/2',
            '¼': '1/4',
            '¾': '3/4'
        }
        
        for original, reemplazo in reemplazos.items():
            texto = texto.replace(original, reemplazo)
        
        return texto
    
    def _eliminar_informacion_contacto(self, texto: str) -> str:
        """Elimina información de contacto del texto"""
        # Eliminar teléfonos
        texto = re.sub(self.patrones_limpieza['telefonos'], '', texto)
        
        # Eliminar emails
        texto = re.sub(self.patrones_limpieza['emails'], '', texto)
        
        # Eliminar URLs
        texto = re.sub(self.patrones_limpieza['urls'], '', texto)
        
        # Eliminar direcciones (patrones básicos)
        patrones_direccion = [
            r'\b\d+\s+[A-Za-z\s]+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard)\b',
            r'\b[A-Za-z\s]+,?\s*\d{5}(?:-\d{4})?\b'  # Códigos postales
        ]
        
        for patron in patrones_direccion:
            texto = re.sub(patron, '', texto, flags=re.IGNORECASE)
        
        return texto
    
    def _limpiar_formato(self, texto: str) -> str:
        """Limpia el formato del texto"""
        # Eliminar caracteres de control
        texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', texto)
        
        # Normalizar saltos de línea
        texto = re.sub(r'\r\n', '\n', texto)
        texto = re.sub(r'\r', '\n', texto)
        
        # Eliminar espacios al inicio y final de líneas
        lineas = [linea.strip() for linea in texto.split('\n')]
        texto = '\n'.join(lineas)
        
        return texto
    
    def _eliminar_lineas_vacias(self, texto: str) -> str:
        """Elimina líneas vacías excesivas"""
        # Reemplazar múltiples saltos de línea con máximo 2
        texto = re.sub(r'\n{3,}', '\n\n', texto)
        return texto
    
    def _es_inicio_plato(self, linea: str) -> bool:
        """Determina si una línea es el inicio de un plato"""
        # Patrones que indican inicio de plato
        patrones_inicio = [
            r'^\d+\.',  # Número seguido de punto
            r'^[A-Z][^.]*$',  # Línea que empieza con mayúscula y no termina en punto
            r'^\*',  # Línea que empieza con asterisco
            r'^[A-Z][a-z]+\s+[A-Z]',  # Dos palabras que empiezan con mayúscula
        ]
        
        for patron in patrones_inicio:
            if re.match(patron, linea.strip()):
                return True
        
        # Verificar si contiene palabras clave de platos
        palabras_plato = ['pizza', 'pasta', 'ensalada', 'sopa', 'sandwich', 'hamburguesa', 'pollo', 'pescado', 'carne']
        linea_lower = linea.lower()
        
        return any(palabra in linea_lower for palabra in palabras_plato)
    
    def _extraer_nombre_plato(self, linea: str) -> str:
        """Extrae el nombre del plato de una línea"""
        # Eliminar números al inicio
        nombre = re.sub(r'^\d+\.\s*', '', linea)
        
        # Eliminar precios al final
        nombre = re.sub(r'\s*[\$€£¥]\s*\d+(?:\.\d{2})?$', '', nombre)
        
        # Eliminar caracteres especiales al final
        nombre = re.sub(r'[^\w\s]$', '', nombre)
        
        return nombre.strip()
    
    def _extraer_precio(self, linea: str) -> Optional[float]:
        """Extrae el precio de una línea"""
        match = re.search(self.patrones_limpieza['precios'], linea)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None
    
    def _detectar_categoria_plato(self, linea: str) -> str:
        """Detecta la categoría de un plato basándose en palabras clave"""
        linea_lower = linea.lower()
        
        categorias = {
            'entrada': ['entrada', 'appetizer', 'aperitivo', 'ensalada', 'sopa'],
            'plato_principal': ['principal', 'main', 'plato', 'pizza', 'pasta', 'carne', 'pollo', 'pescado'],
            'postre': ['postre', 'dessert', 'helado', 'tarta', 'pastel', 'flan'],
            'bebida': ['bebida', 'drink', 'agua', 'refresco', 'café', 'té', 'cerveza', 'vino']
        }
        
        for categoria, palabras in categorias.items():
            if any(palabra in linea_lower for palabra in palabras):
                return categoria
        
        return 'plato_principal'  # Categoría por defecto
    
    def _es_descripcion_plato(self, linea: str) -> bool:
        """Determina si una línea es descripción de un plato"""
        # No es descripción si es inicio de otro plato
        if self._es_inicio_plato(linea):
            return False
        
        # Es descripción si contiene ingredientes o descripción
        palabras_descripcion = ['con', 'de', 'y', 'ingredientes', 'incluye', 'contiene']
        linea_lower = linea.lower()
        
        return any(palabra in linea_lower for palabra in palabras_descripcion)
    
    def _es_fin_plato(self, linea: str) -> bool:
        """Determina si una línea indica el fin de un plato"""
        # Patrones que indican fin de plato
        patrones_fin = [
            r'^\d+\.',  # Siguiente plato numerado
            r'^[A-Z][^.]*$',  # Siguiente plato con mayúscula
            r'^\*',  # Siguiente plato con asterisco
        ]
        
        return any(re.match(patron, linea.strip()) for patron in patrones_fin)
    
    def _limpiar_ingrediente_individual(self, ingrediente: str) -> str:
        """Limpia un ingrediente individual"""
        # Normalizar texto
        ingrediente = self.normalizar_texto(ingrediente)
        
        # Eliminar cantidades y medidas
        ingrediente = re.sub(r'\b\d+(?:\.\d+)?\s*(ml|cl|litros?|kg|g|gramos?|onzas?|libras?)\b', '', ingrediente)
        ingrediente = re.sub(r'\b\d+(?:\.\d+)?\s*(tazas?|cucharadas?|cucharaditas?)\b', '', ingrediente)
        
        # Eliminar palabras comunes que no son ingredientes
        palabras_no_ingrediente = ['y', 'con', 'de', 'en', 'para', 'por', 'al', 'del', 'la', 'el', 'las', 'los']
        palabras = ingrediente.split()
        palabras_limpias = [palabra for palabra in palabras if palabra not in palabras_no_ingrediente]
        
        ingrediente = ' '.join(palabras_limpias)
        
        # Eliminar caracteres especiales al final
        ingrediente = re.sub(r'[^\w\s]$', '', ingrediente)
        
        return ingrediente.strip()
    
    def _extraer_alergenos_de_texto(self, texto: str) -> List[str]:
        """Extrae alérgenos de un texto específico"""
        alergenos_encontrados = []
        texto_lower = texto.lower()
        
        for alergeno in self.alergenos_comunes:
            if alergeno.lower() in texto_lower:
                alergenos_encontrados.append(alergeno)
        
        return alergenos_encontrados
    
    def _validar_alergenos(self, alergenos: List[str]) -> List[str]:
        """Valida y corrige una lista de alérgenos"""
        alergenos_validos = []
        
        for alergeno in alergenos:
            if not alergeno or not alergeno.strip():
                continue
            
            alergeno_limpio = alergeno.strip().lower()
            
            # Buscar coincidencia exacta o similar
            for alergeno_valido in self.alergenos_comunes:
                if alergeno_limpio == alergeno_valido.lower() or alergeno_limpio in alergeno_valido.lower():
                    alergenos_validos.append(alergeno_valido)
                    break
        
        return list(set(alergenos_validos))
    
    def _validar_categoria(self, categoria: str) -> str:
        """Valida y corrige una categoría"""
        if not categoria or not categoria.strip():
            return 'plato_principal'
        
        categoria_lower = categoria.lower().strip()
        
        categorias_validas = {
            'entrada': ['entrada', 'appetizer', 'aperitivo', 'ensalada', 'sopa'],
            'plato_principal': ['principal', 'main', 'plato', 'pizza', 'pasta'],
            'postre': ['postre', 'dessert', 'helado', 'tarta', 'pastel'],
            'bebida': ['bebida', 'drink', 'agua', 'refresco', 'café']
        }
        
        for categoria_valida, variantes in categorias_validas.items():
            if categoria_lower in variantes:
                return categoria_valida
        
        return 'plato_principal'  # Categoría por defecto
    
    def _validar_precio(self, precio: Union[str, int, float]) -> Optional[float]:
        """Valida y corrige un precio"""
        if precio is None:
            return None
        
        try:
            # Convertir a string si es necesario
            precio_str = str(precio)
            
            # Extraer número del precio
            match = re.search(r'(\d+(?:\.\d{2})?)', precio_str)
            if match:
                precio_float = float(match.group(1))
                # Validar rango razonable (0.01 a 1000)
                if 0.01 <= precio_float <= 1000:
                    return round(precio_float, 2)
            
            return None
            
        except (ValueError, TypeError):
            return None
