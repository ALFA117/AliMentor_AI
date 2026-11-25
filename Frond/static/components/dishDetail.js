/**
 * Dish Detail Component
 * Maneja la vista de detalle de un plato específico
 */

class DishDetailComponent {
    constructor() {
        this.detailContainer = null;
        this.currentDish = null;
        this.jsonHandler = null;
        this.init();
    }

    init() {
        this.detailContainer = document.getElementById('dish-detail-container');
        this.jsonHandler = new window.JsonFieldHandler();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Event listener para cerrar modal
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('close-detail-modal') || 
                e.target.classList.contains('modal-overlay')) {
                this.closeDetailModal();
            }
        });

        // Event listener para dar feedback
        document.addEventListener('click', (e) => {
            if (e.target.id === 'give-feedback-btn') {
                this.openFeedbackModal();
            }
        });

        // Event listener para ver acciones IA
        document.addEventListener('click', (e) => {
            if (e.target.id === 'view-ai-actions-btn') {
                this.viewAIActions();
            }
        });
    }

    async loadDishDetail(platoId) {
        try {
            const response = await fetch(`${window.API_BASE_URL}/platos/${platoId}`);
            
            if (response.ok) {
                const data = await response.json();
                this.currentDish = data.plato;
                this.renderDishDetail();
                this.showDetailModal();
            } else {
                console.error('Error cargando detalle del plato:', response.statusText);
                this.showError('Error cargando detalle del plato');
            }
        } catch (error) {
            console.error('Error cargando detalle del plato:', error);
            this.showError('Error de conexión al cargar detalle del plato');
        }
    }

    renderDishDetail() {
        if (!this.currentDish) return;

        const dishIcon = this.getDishIcon(this.currentDish.nombre);
        const compatibilityLevel = this.getCompatibilityLevel(this.currentDish);
        const compatibilityClass = this.getCompatibilityClass(compatibilityLevel);
        const compatibilityIcon = this.getCompatibilityIcon(compatibilityLevel);

        const detailHTML = `
            <div class="dish-detail-modal">
                <div class="modal-overlay"></div>
                <div class="modal-content dish-detail-content">
                    <div class="modal-header">
                        <h2>🍽️ ${this.currentDish.nombre}</h2>
                        <button class="modal-close close-detail-modal">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div class="dish-detail-body">
                        <div class="dish-detail-header">
                            <div class="dish-detail-icon ${compatibilityClass}">
                                ${dishIcon}
                            </div>
                            <div class="dish-detail-info">
                                <h3>${this.currentDish.nombre}</h3>
                                <p class="dish-detail-category">${this.currentDish.categoria}</p>
                                <div class="compatibility-badge ${compatibilityClass}">
                                    ${compatibilityIcon} ${compatibilityLevel.toUpperCase()}
                                </div>
                            </div>
                        </div>

                        <div class="dish-detail-description">
                            <h4><i class="fas fa-info-circle"></i> Descripción</h4>
                            <p>${this.currentDish.descripcion}</p>
                        </div>

                        <div class="dish-detail-ingredients">
                            <h4><i class="fas fa-list"></i> Ingredientes</h4>
                            <div id="detail-ingredients" class="chips-container"></div>
                        </div>

                        <div class="dish-detail-allergens">
                            <h4><i class="fas fa-exclamation-triangle"></i> Alérgenos Detectados</h4>
                            <div id="detail-allergens" class="chips-container"></div>
                        </div>

                        <div class="dish-detail-meta">
                            <div class="meta-grid">
                                <div class="meta-item">
                                    <i class="fas fa-dollar-sign"></i>
                                    <span class="meta-label">Precio:</span>
                                    <span class="meta-value">$${this.currentDish.precio}</span>
                                </div>
                                <div class="meta-item">
                                    <i class="fas fa-store"></i>
                                    <span class="meta-label">Fuente:</span>
                                    <span class="meta-value">${this.currentDish.fuente}</span>
                                </div>
                                <div class="meta-item">
                                    <i class="fas fa-calendar"></i>
                                    <span class="meta-label">Registrado:</span>
                                    <span class="meta-value">${new Date(this.currentDish.fecha_registro).toLocaleDateString('es-ES')}</span>
                                </div>
                            </div>
                        </div>

                        <div class="dish-detail-actions">
                            <button id="give-feedback-btn" class="btn btn-primary">
                                <i class="fas fa-comment"></i> Dar Feedback
                            </button>
                            <button id="view-ai-actions-btn" class="btn btn-secondary">
                                <i class="fas fa-robot"></i> Ver Acciones IA
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Crear modal si no existe
        let modal = document.querySelector('.dish-detail-modal');
        if (modal) {
            modal.remove();
        }

        document.body.insertAdjacentHTML('beforeend', detailHTML);

        // Renderizar campos JSON como chips
        this.jsonHandler.renderIngredients(this.currentDish.ingredientes, 'detail-ingredients', false);
        this.jsonHandler.renderAllergens(this.currentDish.alergenos_detectados, 'detail-allergens', false);
    }

    showDetailModal() {
        const modal = document.querySelector('.dish-detail-modal');
        if (modal) {
            modal.style.display = 'flex';
            modal.classList.add('modal-fade-in');
            
            // Animar el contenido
            const content = modal.querySelector('.modal-content');
            content.classList.add('modal-slide-up');
        }
    }

    closeDetailModal() {
        const modal = document.querySelector('.dish-detail-modal');
        if (modal) {
            modal.classList.remove('modal-fade-in');
            modal.classList.add('modal-fade-out');
            
            setTimeout(() => {
                modal.remove();
            }, 300);
        }
    }

    openFeedbackModal() {
        if (window.feedbackPanel) {
            window.feedbackPanel.showModal(this.currentDish.id_plato);
        } else {
            console.warn('FeedbackPanel component not available');
            this.showError('Funcionalidad de feedback no disponible');
        }
    }

    async viewAIActions() {
        try {
            const response = await fetch(`${window.API_BASE_URL}/acciones_ia?plato_id=${this.currentDish.id_plato}`);
            
            if (response.ok) {
                const data = await response.json();
                this.showAIActionsModal(data.acciones);
            } else {
                console.error('Error cargando acciones IA:', response.statusText);
                this.showError('Error cargando acciones IA');
            }
        } catch (error) {
            console.error('Error cargando acciones IA:', error);
            this.showError('Error de conexión al cargar acciones IA');
        }
    }

    showAIActionsModal(acciones) {
        const modalHTML = `
            <div class="ai-actions-modal">
                <div class="modal-overlay"></div>
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>🤖 Acciones IA para ${this.currentDish.nombre}</h2>
                        <button class="modal-close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        ${acciones.length === 0 ? 
                            '<p>No hay acciones IA registradas para este plato.</p>' :
                            acciones.map(accion => this.createAIActionCard(accion)).join('')
                        }
                    </div>
                </div>
            </div>
        `;

        // Crear modal
        let modal = document.querySelector('.ai-actions-modal');
        if (modal) {
            modal.remove();
        }

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Mostrar modal
        modal = document.querySelector('.ai-actions-modal');
        modal.style.display = 'flex';
        modal.classList.add('modal-fade-in');

        // Event listeners para cerrar
        modal.querySelector('.modal-close').addEventListener('click', () => {
            modal.remove();
        });
        modal.querySelector('.modal-overlay').addEventListener('click', () => {
            modal.remove();
        });
    }

    createAIActionCard(accion) {
        const successIcon = accion.exito ? '✅' : '❌';
        const tipoIcon = this.getTipoAccionIcon(accion.tipo_accion);
        
        return `
            <div class="ai-action-card">
                <div class="ai-action-header">
                    <div class="ai-action-icon">
                        ${tipoIcon}
                    </div>
                    <div class="ai-action-info">
                        <h4>${accion.tipo_accion.toUpperCase()}</h4>
                        <span class="ai-action-date">${new Date(accion.fecha).toLocaleString('es-ES')}</span>
                        <span class="ai-action-status ${accion.exito ? 'success' : 'error'}">
                            ${successIcon} ${accion.exito ? 'Exitoso' : 'Fallido'}
                        </span>
                    </div>
                </div>
                <div class="ai-action-content">
                    <div class="ai-action-prompt">
                        <strong>Prompt:</strong> ${accion.entrada_prompt}
                    </div>
                    <div class="ai-action-result">
                        <strong>Resultado:</strong> ${accion.salida_resumen}
                    </div>
                </div>
            </div>
        `;
    }

    getDishIcon(nombre) {
        const nombreLower = nombre.toLowerCase();
        const iconMap = {
            'pizza': '🍕',
            'ensalada': '🥗',
            'pasta': '🍝',
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
            'arroz': '🍚'
        };
        
        for (const [keyword, icon] of Object.entries(iconMap)) {
            if (nombreLower.includes(keyword)) {
                return icon;
            }
        }
        return '🍽️';
    }

    getCompatibilityLevel(dish) {
        const hasAllergens = dish.alergenos_detectados && dish.alergenos_detectados.length > 0;
        const hasCommonAllergens = dish.alergenos_detectados.some(a => 
            ['gluten', 'lactosa', 'huevo', 'nuez'].includes(a.toLowerCase())
        );
        
        if (hasCommonAllergens) return 'warning';
        if (hasAllergens) return 'safe';
        return 'safe';
    }

    getCompatibilityClass(level) {
        const classes = {
            'safe': 'safe',
            'warning': 'warning',
            'danger': 'danger'
        };
        return classes[level] || 'safe';
    }

    getCompatibilityIcon(level) {
        const icons = {
            'safe': '🟢',
            'warning': '🟡',
            'danger': '🔴'
        };
        return icons[level] || '🟢';
    }

    getTipoAccionIcon(tipo) {
        const icons = {
            'analisis': '🔍',
            'recomendacion': '💡',
            'mejora': '⚡',
            'feedback': '💬'
        };
        return icons[tipo] || '🤖';
    }

    showError(message) {
        if (window.Utils) {
            window.Utils.showNotification(message, 'error');
        } else {
            alert(message);
        }
    }
}

// Exportar para uso global
window.DishDetailComponent = DishDetailComponent;
