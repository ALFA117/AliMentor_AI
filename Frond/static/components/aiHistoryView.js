/**
 * AI History View Component
 * Maneja la vista de historial de acciones IA y mejoras
 */

class AIHistoryViewComponent {
    constructor() {
        this.historyContainer = null;
        this.acciones = [];
        this.mejoras = [];
        this.filters = {
            tipo_accion: '',
            usuario_id: '',
            plato_id: '',
            exito: ''
        };
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.init();
    }

    init() {
        this.historyContainer = document.getElementById('ai-history-container');
        this.setupEventListeners();
        this.loadAIHistory();
    }

    setupEventListeners() {
        // Event listeners para filtros
        document.addEventListener('change', (e) => {
            if (e.target.id === 'tipo-accion-filter') {
                this.filters.tipo_accion = e.target.value;
                this.applyFilters();
            }
            if (e.target.id === 'usuario-filter') {
                this.filters.usuario_id = e.target.value;
                this.applyFilters();
            }
            if (e.target.id === 'plato-filter') {
                this.filters.plato_id = e.target.value;
                this.applyFilters();
            }
            if (e.target.id === 'exito-filter') {
                this.filters.exito = e.target.value;
                this.applyFilters();
            }
        });

        // Event listeners para paginación
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('history-page-btn')) {
                const page = parseInt(e.target.dataset.page);
                this.goToPage(page);
            }
        });

        // Event listener para ver mejoras
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('view-mejoras-btn')) {
                const accionId = parseInt(e.target.dataset.accionId);
                this.viewMejoras(accionId);
            }
        });
    }

    async loadAIHistory() {
        try {
            const response = await fetch(`${window.API_BASE_URL}/acciones_ia`);
            
            if (response.ok) {
                const data = await response.json();
                this.acciones = data.acciones || [];
                this.renderAIHistory();
                this.renderFilters();
            } else {
                console.error('Error cargando historial IA:', response.statusText);
                this.showError('Error cargando historial de IA');
            }
        } catch (error) {
            console.error('Error cargando historial IA:', error);
            this.showError('Error de conexión al cargar historial de IA');
        }
    }

    renderFilters() {
        const filtersContainer = document.getElementById('ai-history-filters');
        if (!filtersContainer) return;

        // Obtener valores únicos para los filtros
        const tiposAccion = [...new Set(this.acciones.map(a => a.tipo_accion))];
        const usuarios = [...new Set(this.acciones.map(a => a.usuario_id))];
        const platos = [...new Set(this.acciones.map(a => a.plato_id))];

        filtersContainer.innerHTML = `
            <div class="ai-filters-grid">
                <div class="filter-group">
                    <label for="tipo-accion-filter">🤖 Tipo de Acción:</label>
                    <select id="tipo-accion-filter">
                        <option value="">Todos los tipos</option>
                        ${tiposAccion.map(tipo => `<option value="${tipo}">${tipo.toUpperCase()}</option>`).join('')}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="usuario-filter">👤 Usuario:</label>
                    <select id="usuario-filter">
                        <option value="">Todos los usuarios</option>
                        ${usuarios.map(usuario => `<option value="${usuario}">Usuario ${usuario}</option>`).join('')}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="plato-filter">🍽️ Plato:</label>
                    <select id="plato-filter">
                        <option value="">Todos los platos</option>
                        ${platos.map(plato => `<option value="${plato}">Plato ${plato}</option>`).join('')}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="exito-filter">✅ Estado:</label>
                    <select id="exito-filter">
                        <option value="">Todos los estados</option>
                        <option value="true">Exitoso</option>
                        <option value="false">Fallido</option>
                    </select>
                </div>
            </div>
        `;
    }

    applyFilters() {
        let filteredAcciones = this.acciones;

        if (this.filters.tipo_accion) {
            filteredAcciones = filteredAcciones.filter(a => 
                a.tipo_accion === this.filters.tipo_accion
            );
        }

        if (this.filters.usuario_id) {
            filteredAcciones = filteredAcciones.filter(a => 
                a.usuario_id === parseInt(this.filters.usuario_id)
            );
        }

        if (this.filters.plato_id) {
            filteredAcciones = filteredAcciones.filter(a => 
                a.plato_id === parseInt(this.filters.plato_id)
            );
        }

        if (this.filters.exito !== '') {
            const exito = this.filters.exito === 'true';
            filteredAcciones = filteredAcciones.filter(a => a.exito === exito);
        }

        this.filteredAcciones = filteredAcciones;
        this.currentPage = 1;
        this.renderAIHistory();
    }

    renderAIHistory() {
        if (!this.historyContainer) return;

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const accionesToShow = (this.filteredAcciones || this.acciones).slice(startIndex, endIndex);

        if (accionesToShow.length === 0) {
            this.historyContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-robot"></i>
                    <h3>No hay acciones IA registradas</h3>
                    <p>Las acciones de IA aparecerán aquí cuando se realicen análisis</p>
                </div>
            `;
            return;
        }

        this.historyContainer.innerHTML = `
            <div class="ai-history-grid">
                ${accionesToShow.map(accion => this.createAIActionCard(accion)).join('')}
            </div>
            ${this.renderPagination()}
        `;
    }

    createAIActionCard(accion) {
        const tipoIcon = this.getTipoAccionIcon(accion.tipo_accion);
        const successClass = accion.exito ? 'success' : 'error';
        const successIcon = accion.exito ? '✅' : '❌';
        const fecha = new Date(accion.fecha).toLocaleString('es-ES');

        return `
            <div class="ai-action-history-card ${successClass}">
                <div class="ai-action-header">
                    <div class="ai-action-icon">
                        ${tipoIcon}
                    </div>
                    <div class="ai-action-info">
                        <h4>${accion.tipo_accion.toUpperCase()}</h4>
                        <div class="ai-action-meta">
                            <span class="ai-action-date">${fecha}</span>
                            <span class="ai-action-status ${successClass}">
                                ${successIcon} ${accion.exito ? 'Exitoso' : 'Fallido'}
                            </span>
                        </div>
                    </div>
                </div>

                <div class="ai-action-content">
                    <div class="ai-action-prompt">
                        <strong>Prompt:</strong>
                        <p>${accion.entrada_prompt}</p>
                    </div>
                    <div class="ai-action-result">
                        <strong>Resultado:</strong>
                        <p>${accion.salida_resumen}</p>
                    </div>
                </div>

                <div class="ai-action-footer">
                    <div class="ai-action-details">
                        <span class="detail-item">
                            <i class="fas fa-user"></i>
                            Usuario ${accion.usuario_id || 'Sistema'}
                        </span>
                        <span class="detail-item">
                            <i class="fas fa-utensils"></i>
                            Plato ${accion.plato_id || 'N/A'}
                        </span>
                    </div>
                    <button class="btn btn-secondary view-mejoras-btn" data-accion-id="${accion.id_accion}">
                        <i class="fas fa-cogs"></i> Ver Mejoras
                    </button>
                </div>
            </div>
        `;
    }

    renderPagination() {
        const totalPages = Math.ceil((this.filteredAcciones || this.acciones).length / this.itemsPerPage);
        
        if (totalPages <= 1) return '';

        let paginationHTML = '<div class="ai-history-pagination">';
        
        // Botón anterior
        if (this.currentPage > 1) {
            paginationHTML += `
                <button class="history-page-btn" data-page="${this.currentPage - 1}">
                    <i class="fas fa-chevron-left"></i>
                </button>
            `;
        }

        // Páginas
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                paginationHTML += `<button class="history-page-btn active">${i}</button>`;
            } else {
                paginationHTML += `<button class="history-page-btn" data-page="${i}">${i}</button>`;
            }
        }

        // Botón siguiente
        if (this.currentPage < totalPages) {
            paginationHTML += `
                <button class="history-page-btn" data-page="${this.currentPage + 1}">
                    <i class="fas fa-chevron-right"></i>
                </button>
            `;
        }

        paginationHTML += '</div>';
        return paginationHTML;
    }

    goToPage(page) {
        this.currentPage = page;
        this.renderAIHistory();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async viewMejoras(accionId) {
        try {
            const response = await fetch(`${window.API_BASE_URL}/mejora_ia?accion_id=${accionId}`);
            
            if (response.ok) {
                const data = await response.json();
                this.showMejorasModal(accionId, data.mejoras);
            } else {
                console.error('Error cargando mejoras:', response.statusText);
                this.showError('Error cargando mejoras de IA');
            }
        } catch (error) {
            console.error('Error cargando mejoras:', error);
            this.showError('Error de conexión al cargar mejoras de IA');
        }
    }

    showMejorasModal(accionId, mejoras) {
        const modalHTML = `
            <div class="mejoras-modal">
                <div class="modal-overlay"></div>
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>⚡ Mejoras IA - Acción ${accionId}</h2>
                        <button class="modal-close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        ${mejoras.length === 0 ? 
                            '<p>No hay mejoras registradas para esta acción.</p>' :
                            mejoras.map(mejora => this.createMejoraCard(mejora)).join('')
                        }
                    </div>
                </div>
            </div>
        `;

        // Crear modal
        let modal = document.querySelector('.mejoras-modal');
        if (modal) {
            modal.remove();
        }

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Mostrar modal
        modal = document.querySelector('.mejoras-modal');
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

    createMejoraCard(mejora) {
        const fecha = new Date(mejora.fecha).toLocaleString('es-ES');
        const confianzaPorcentaje = Math.round(mejora.confianza * 100);

        return `
            <div class="mejora-card">
                <div class="mejora-header">
                    <div class="mejora-icon">
                        <i class="fas fa-cogs"></i>
                    </div>
                    <div class="mejora-info">
                        <h4>Mejora ${mejora.id_mejora}</h4>
                        <span class="mejora-date">${fecha}</span>
                        <span class="mejora-confidence">
                            <i class="fas fa-chart-line"></i>
                            ${confianzaPorcentaje}% confianza
                        </span>
                    </div>
                </div>
                <div class="mejora-content">
                    <div class="mejora-prompt">
                        <strong>Ajuste de Prompt:</strong>
                        <p>${mejora.ajuste_prompt}</p>
                    </div>
                    <div class="mejora-observation">
                        <strong>Observación:</strong>
                        <p>${mejora.observacion}</p>
                    </div>
                </div>
            </div>
        `;
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
window.AIHistoryViewComponent = AIHistoryViewComponent;
