/**
 * Dishes Listing Component
 * Maneja el listado de platos con filtros y paginación
 */

class DishesListingComponent {
    constructor() {
        this.dishesContainer = null;
        this.dishes = [];
        this.filteredDishes = [];
        this.currentPage = 1;
        this.itemsPerPage = 6;
        this.filters = {
            categoria: '',
            fuente: '',
            alergeno: '',
            search: ''
        };
        this.jsonHandler = null;
        this.init();
    }

    init() {
        this.dishesContainer = document.getElementById('dishes-listing-container');
        this.jsonHandler = new window.JsonFieldHandler();
        this.setupEventListeners();
        this.loadDishes();
    }

    setupEventListeners() {
        // Event listeners para filtros
        document.addEventListener('change', (e) => {
            if (e.target.id === 'categoria-filter') {
                this.filters.categoria = e.target.value;
                this.applyFilters();
            }
            if (e.target.id === 'fuente-filter') {
                this.filters.fuente = e.target.value;
                this.applyFilters();
            }
            if (e.target.id === 'alergeno-filter') {
                this.filters.alergeno = e.target.value;
                this.applyFilters();
            }
        });

        // Event listener para búsqueda
        document.addEventListener('input', (e) => {
            if (e.target.id === 'search-dishes') {
                this.filters.search = e.target.value.toLowerCase();
                this.applyFilters();
            }
        });

        // Event listeners para paginación
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('page-btn')) {
                const page = parseInt(e.target.dataset.page);
                this.goToPage(page);
            }
        });
    }

    async loadDishes() {
        try {
            const response = await fetch(`${window.API_BASE_URL}/platos`);
            
            if (response.ok) {
                const data = await response.json();
                this.dishes = data.platos || [];
                this.filteredDishes = [...this.dishes];
                this.renderDishes();
                this.renderFilters();
            } else {
                console.error('Error cargando platos:', response.statusText);
                this.showError('Error cargando lista de platos');
            }
        } catch (error) {
            console.error('Error cargando platos:', error);
            this.showError('Error de conexión al cargar platos');
        }
    }

    renderFilters() {
        const filtersContainer = document.getElementById('dishes-filters');
        if (!filtersContainer) return;

        // Obtener valores únicos para los filtros
        const categorias = [...new Set(this.dishes.map(d => d.categoria))];
        const fuentes = [...new Set(this.dishes.map(d => d.fuente))];
        const alergenos = [...new Set(this.dishes.flatMap(d => d.alergenos_detectados))];

        filtersContainer.innerHTML = `
            <div class="filters-grid">
                <div class="filter-group">
                    <label for="search-dishes">🔍 Buscar:</label>
                    <input type="text" id="search-dishes" placeholder="Buscar platos...">
                </div>
                
                <div class="filter-group">
                    <label for="categoria-filter">📂 Categoría:</label>
                    <select id="categoria-filter">
                        <option value="">Todas las categorías</option>
                        ${categorias.map(cat => `<option value="${cat}">${cat}</option>`).join('')}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="fuente-filter">🏪 Fuente:</label>
                    <select id="fuente-filter">
                        <option value="">Todas las fuentes</option>
                        ${fuentes.map(fuente => `<option value="${fuente}">${fuente}</option>`).join('')}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label for="alergeno-filter">⚠️ Alérgeno:</label>
                    <select id="alergeno-filter">
                        <option value="">Todos los alérgenos</option>
                        ${alergenos.map(alergeno => `<option value="${alergeno}">${alergeno}</option>`).join('')}
                    </select>
                </div>
            </div>
        `;
    }

    applyFilters() {
        this.filteredDishes = this.dishes.filter(dish => {
            const matchesCategoria = !this.filters.categoria || 
                dish.categoria.toLowerCase().includes(this.filters.categoria.toLowerCase());
            
            const matchesFuente = !this.filters.fuente || 
                dish.fuente.toLowerCase().includes(this.filters.fuente.toLowerCase());
            
            const matchesAlergeno = !this.filters.alergeno || 
                dish.alergenos_detectados.some(a => 
                    a.toLowerCase().includes(this.filters.alergeno.toLowerCase())
                );
            
            const matchesSearch = !this.filters.search || 
                dish.nombre.toLowerCase().includes(this.filters.search) ||
                dish.descripcion.toLowerCase().includes(this.filters.search) ||
                dish.ingredientes.some(i => i.toLowerCase().includes(this.filters.search));
            
            return matchesCategoria && matchesFuente && matchesAlergeno && matchesSearch;
        });

        this.currentPage = 1;
        this.renderDishes();
    }

    renderDishes() {
        if (!this.dishesContainer) return;

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const dishesToShow = this.filteredDishes.slice(startIndex, endIndex);

        if (dishesToShow.length === 0) {
            this.dishesContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-utensils"></i>
                    <h3>No se encontraron platos</h3>
                    <p>Intenta ajustar los filtros de búsqueda</p>
                </div>
            `;
            return;
        }

        this.dishesContainer.innerHTML = `
            <div class="dishes-grid">
                ${dishesToShow.map(dish => this.createDishCard(dish)).join('')}
            </div>
            ${this.renderPagination()}
        `;
    }

    createDishCard(dish) {
        const dishIcon = this.getDishIcon(dish.nombre);
        const compatibilityLevel = this.getCompatibilityLevel(dish);
        const compatibilityClass = this.getCompatibilityClass(compatibilityLevel);
        const compatibilityIcon = this.getCompatibilityIcon(compatibilityLevel);

        return `
            <div class="dish-listing-card ${compatibilityClass}">
                <div class="dish-card-header">
                    <div class="dish-icon ${compatibilityClass}">
                        ${dishIcon}
                    </div>
                    <div class="dish-basic-info">
                        <h3>${dish.nombre}</h3>
                        <p class="dish-category">${dish.categoria}</p>
                        <div class="compatibility-badge ${compatibilityClass}">
                            ${compatibilityIcon} ${compatibilityLevel.toUpperCase()}
                        </div>
                    </div>
                </div>

                <div class="dish-card-body">
                    <p class="dish-description">${dish.descripcion}</p>
                    
                    <div class="dish-ingredients">
                        <h4><i class="fas fa-list"></i> Ingredientes:</h4>
                        <div id="ingredients-${dish.id_plato}" class="chips-container"></div>
                    </div>
                    
                    <div class="dish-allergens">
                        <h4><i class="fas fa-exclamation-triangle"></i> Alérgenos:</h4>
                        <div id="allergens-${dish.id_plato}" class="chips-container"></div>
                    </div>
                    
                    <div class="dish-meta">
                        <div class="dish-price">
                            <i class="fas fa-dollar-sign"></i>
                            <span>$${dish.precio}</span>
                        </div>
                        <div class="dish-source">
                            <i class="fas fa-store"></i>
                            <span>${dish.fuente}</span>
                        </div>
                    </div>
                </div>

                <div class="dish-card-actions">
                    <button class="btn btn-primary" onclick="dishesListing.viewDishDetail(${dish.id_plato})">
                        <i class="fas fa-eye"></i> Ver Detalle
                    </button>
                    <button class="btn btn-secondary" onclick="dishesListing.giveFeedback(${dish.id_plato})">
                        <i class="fas fa-comment"></i> Feedback
                    </button>
                </div>
            </div>
        `;
    }

    renderPagination() {
        const totalPages = Math.ceil(this.filteredDishes.length / this.itemsPerPage);
        
        if (totalPages <= 1) return '';

        let paginationHTML = '<div class="pagination">';
        
        // Botón anterior
        if (this.currentPage > 1) {
            paginationHTML += `
                <button class="page-btn" data-page="${this.currentPage - 1}">
                    <i class="fas fa-chevron-left"></i>
                </button>
            `;
        }

        // Páginas
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                paginationHTML += `<button class="page-btn active">${i}</button>`;
            } else {
                paginationHTML += `<button class="page-btn" data-page="${i}">${i}</button>`;
            }
        }

        // Botón siguiente
        if (this.currentPage < totalPages) {
            paginationHTML += `
                <button class="page-btn" data-page="${this.currentPage + 1}">
                    <i class="fas fa-chevron-right"></i>
                </button>
            `;
        }

        paginationHTML += '</div>';
        return paginationHTML;
    }

    goToPage(page) {
        this.currentPage = page;
        this.renderDishes();
        window.scrollTo({ top: 0, behavior: 'smooth' });
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
        // Lógica simple para determinar compatibilidad
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

    viewDishDetail(platoId) {
        if (window.dishDetail) {
            window.dishDetail.loadDishDetail(platoId);
        } else {
            console.warn('DishDetail component not available');
            this.showError('Funcionalidad de detalle no disponible');
        }
    }

    giveFeedback(platoId) {
        if (window.feedbackPanel) {
            window.feedbackPanel.showModal(platoId);
        } else {
            console.warn('FeedbackPanel component not available');
            this.showError('Funcionalidad de feedback no disponible');
        }
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
window.DishesListingComponent = DishesListingComponent;
