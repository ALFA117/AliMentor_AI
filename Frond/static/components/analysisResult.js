/**
 * Analysis Result Component
 * Muestra los resultados del análisis con iconos de compatibilidad
 */

class AnalysisResultComponent {
    constructor() {
        this.resultsContainer = null;
        this.init();
    }

    init() {
        this.resultsContainer = document.getElementById('results-container');
    }

    render(analysisData) {
        if (!this.resultsContainer) return;

        this.resultsContainer.innerHTML = '';
        
        if (!analysisData.platos || analysisData.platos.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Crear resumen general si existe
        if (analysisData.resumen) {
            this.createSummary(analysisData.resumen);
        }
        
        // Crear elementos para cada platillo
        analysisData.platos.forEach((plato, index) => {
            const platoElement = this.createPlatoElement(plato, index);
            this.resultsContainer.appendChild(platoElement);
        });
    }

    createSummary(resumen) {
        if (!resumen) return;

        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'analysis-summary';
        
        summaryDiv.innerHTML = `
            <div class="summary-header">
                <h3><i class="fas fa-chart-pie"></i> Resumen del Análisis</h3>
            </div>
            <div class="summary-stats">
                <div class="stat-item safe">
                    <span class="stat-icon">🟢</span>
                    <span class="stat-label">Seguros</span>
                    <span class="stat-value">${resumen.seguros || 0}</span>
                </div>
                <div class="stat-item warning">
                    <span class="stat-icon">🟡</span>
                    <span class="stat-label">Precaución</span>
                    <span class="stat-value">${resumen.precaucion || 0}</span>
                </div>
                <div class="stat-item danger">
                    <span class="stat-icon">🔴</span>
                    <span class="stat-label">Riesgo</span>
                    <span class="stat-value">${resumen.riesgo || 0}</span>
                </div>
            </div>
            ${resumen.recomendaciones ? `
                <div class="summary-recommendations">
                    <h4>Recomendaciones Generales:</h4>
                    <p>${resumen.recomendaciones}</p>
                </div>
            ` : ''}
        `;
        
        this.resultsContainer.appendChild(summaryDiv);
    }

    createPlatoElement(plato, index) {
        const div = document.createElement('div');
        div.className = 'dish-card';
        
        const compatibilityClass = this.getCompatibilityClass(plato.nivel_compatibilidad);
        const compatibilityIcon = this.getCompatibilityIcon(plato.nivel_compatibilidad);
        const dishIcon = this.getDishIcon(plato.nombre);
        
        div.innerHTML = `
            <div class="dish-header">
                <div class="dish-icon ${compatibilityClass} ${this.getDishCategory(plato.nombre)}">
                    ${dishIcon}
                </div>
                <div class="dish-info">
                    <h3>${plato.nombre}</h3>
                    <p>${plato.ingredientes ? plato.ingredientes.join(', ') : 'No especificados'}</p>
                </div>
                <div class="compatibility-badge ${compatibilityClass}">
                    ${compatibilityIcon} ${this.getCompatibilityLabel(plato.nivel_compatibilidad)}
                </div>
            </div>
            <div class="dish-analysis">
                <h4><i class="fas fa-search"></i> Análisis</h4>
                <p>${plato.analisis || 'Sin análisis disponible'}</p>
            </div>
            ${plato.recomendaciones ? `
                <div class="dish-recommendations">
                    <h5><i class="fas fa-lightbulb"></i> Recomendaciones</h5>
                    <p>${plato.recomendaciones}</p>
                </div>
            ` : ''}
            <div class="dish-actions" style="margin-top: 15px;">
                <button class="btn btn-sm btn-primary" onclick="window.FeedbackFormComponent?.selectDish('${plato.nombre}', ${plato.id || index})">
                    <i class="fas fa-comment"></i> Dar Feedback
                </button>
            </div>
        `;
        
        return div;
    }

    getCompatibilityIcon(level) {
        const icons = {
            'seguro': '🟢',
            'precaucion': '🟡', 
            'riesgo': '🔴'
        };
        return icons[level] || '⚪';
    }

    getCompatibilityClass(level) {
        const classes = {
            'seguro': 'safe',
            'precaucion': 'warning',
            'riesgo': 'danger'
        };
        return classes[level] || '';
    }

    getCompatibilityLabel(level) {
        const labels = {
            'seguro': 'Seguro',
            'precaucion': 'Precaución',
            'riesgo': 'Riesgo'
        };
        return labels[level] || 'Desconocido';
    }

    getDishIcon(nombre) {
        const nombreLower = nombre.toLowerCase();
        const iconMap = {
            'pizza': '🍕',
            'ensalada': '🥗',
            'pasta': '🍝',
            'pasta': '🍜',
            'sopa': '🍲',
            'carne': '🥩',
            'pollo': '🍗',
            'pescado': '🐟',
            'salmón': '🐟',
            'postre': '🍰',
            'helado': '🍦',
            'bebida': '🥤',
            'café': '☕',
            'té': '🍵',
            'sandwich': '🥪',
            'hamburguesa': '🍔',
            'tacos': '🌮',
            'sushi': '🍣',
            'arroz': '🍚',
            'pasta': '🍝'
        };
        
        for (const [keyword, icon] of Object.entries(iconMap)) {
            if (nombreLower.includes(keyword)) {
                return icon;
            }
        }
        return '🍽️'; // Ícono por defecto
    }

    getDishCategory(nombre) {
        const nombreLower = nombre.toLowerCase();
        if (nombreLower.includes('ensalada') || nombreLower.includes('vegetal')) return 'ensalada';
        if (nombreLower.includes('carne') || nombreLower.includes('bistec') || nombreLower.includes('chuleta')) return 'carne';
        if (nombreLower.includes('pasta') || nombreLower.includes('espagueti') || nombreLower.includes('fettuccine')) return 'pasta';
        if (nombreLower.includes('pizza')) return 'pizza';
        if (nombreLower.includes('postre') || nombreLower.includes('tarta') || nombreLower.includes('pastel')) return 'postre';
        if (nombreLower.includes('bebida') || nombreLower.includes('jugo') || nombreLower.includes('refresco')) return 'bebida';
        if (nombreLower.includes('sopa') || nombreLower.includes('caldo')) return 'sopa';
        if (nombreLower.includes('pescado') || nombreLower.includes('salmón') || nombreLower.includes('atún')) return 'pescado';
        return 'general';
    }

    showEmptyState() {
        if (!this.resultsContainer) return;
        
        this.resultsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <p>Sube un menú para ver el análisis de compatibilidad</p>
            </div>
        `;
    }

    // Método para actualizar un resultado específico
    updatePlatoResult(platoNombre, newData) {
        const platoElements = this.resultsContainer?.querySelectorAll('.dish-item');
        if (!platoElements) return;

        platoElements.forEach(element => {
            const nameElement = element.querySelector('.dish-name');
            if (nameElement && nameElement.textContent === platoNombre) {
                // Actualizar el elemento con nuevos datos
                const analysisElement = element.querySelector('.dish-analysis p');
                if (analysisElement && newData.analisis) {
                    analysisElement.textContent = newData.analisis;
                }
            }
        });
    }

    // Método para resaltar un platillo específico
    highlightPlato(platoNombre) {
        const platoElements = this.resultsContainer?.querySelectorAll('.dish-item');
        if (!platoElements) return;

        platoElements.forEach(element => {
            const nameElement = element.querySelector('.dish-name');
            if (nameElement && nameElement.textContent === platoNombre) {
                element.classList.add('highlighted');
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                element.classList.remove('highlighted');
            }
        });
    }

    // Método para obtener todos los platillos mostrados
    getDisplayedPlatos() {
        const platoElements = this.resultsContainer?.querySelectorAll('.dish-item');
        if (!platoElements) return [];

        return Array.from(platoElements).map(element => {
            const nameElement = element.querySelector('.dish-name');
            return nameElement ? nameElement.textContent : '';
        });
    }
}

// Exportar para uso global
window.AnalysisResultComponent = AnalysisResultComponent;

