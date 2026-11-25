/**
 * Data Table Component
 * Maneja vistas tipo tabla con búsqueda, ordenamiento y paginación
 */

class DataTableComponent {
    constructor(config) {
        this.config = {
            containerId: config.containerId,
            endpoint: config.endpoint,
            columns: config.columns,
            itemsPerPage: config.itemsPerPage || 10,
            searchable: config.searchable !== false,
            sortable: config.sortable !== false,
            pagination: config.pagination !== false,
            actions: config.actions || []
        };
        
        this.data = [];
        this.filteredData = [];
        this.currentPage = 1;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.searchTerm = '';
        this.jsonHandler = null;
        
        this.init();
    }

    init() {
        this.jsonHandler = new window.JsonFieldHandler();
        this.setupEventListeners();
        this.loadData();
    }

    setupEventListeners() {
        // Event listener para búsqueda
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('data-table-search')) {
                this.searchTerm = e.target.value.toLowerCase();
                this.applyFilters();
            }
        });

        // Event listener para ordenamiento
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('sortable-header')) {
                const column = e.target.dataset.column;
                this.sortBy(column);
            }
        });

        // Event listener para paginación
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('table-page-btn')) {
                const page = parseInt(e.target.dataset.page);
                this.goToPage(page);
            }
        });

        // Event listener para acciones
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('table-action-btn')) {
                const action = e.target.dataset.action;
                const id = e.target.dataset.id;
                this.handleAction(action, id);
            }
        });
    }

    async loadData() {
        try {
            const response = await fetch(`${window.API_BASE_URL}${this.config.endpoint}`);
            
            if (response.ok) {
                const result = await response.json();
                this.data = result[Object.keys(result)[0]] || [];
                this.filteredData = [...this.data];
                this.renderTable();
            } else {
                console.error('Error cargando datos:', response.statusText);
                this.showError('Error cargando datos de la tabla');
            }
        } catch (error) {
            console.error('Error cargando datos:', error);
            this.showError('Error de conexión al cargar datos');
        }
    }

    renderTable() {
        const container = document.getElementById(this.config.containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="data-table-container">
                ${this.renderTableHeader()}
                ${this.renderTableBody()}
                ${this.renderTableFooter()}
            </div>
        `;
    }

    renderTableHeader() {
        const searchHTML = this.config.searchable ? `
            <div class="table-search">
                <input type="text" class="data-table-search" placeholder="Buscar...">
                <i class="fas fa-search"></i>
            </div>
        ` : '';

        return `
            <div class="table-header">
                <h3>${this.config.title || 'Tabla de Datos'}</h3>
                ${searchHTML}
            </div>
        `;
    }

    renderTableBody() {
        const startIndex = (this.currentPage - 1) * this.config.itemsPerPage;
        const endIndex = startIndex + this.config.itemsPerPage;
        const dataToShow = this.filteredData.slice(startIndex, endIndex);

        if (dataToShow.length === 0) {
            return `
                <div class="table-empty-state">
                    <i class="fas fa-inbox"></i>
                    <h4>No hay datos disponibles</h4>
                    <p>No se encontraron registros que coincidan con los criterios de búsqueda</p>
                </div>
            `;
        }

        return `
            <div class="table-wrapper">
                <table class="data-table">
                    <thead>
                        <tr>
                            ${this.config.columns.map(col => `
                                <th class="${col.sortable !== false ? 'sortable-header' : ''}" 
                                    data-column="${col.key}">
                                    ${col.title}
                                    ${col.sortable !== false ? '<i class="fas fa-sort"></i>' : ''}
                                </th>
                            `).join('')}
                            ${this.config.actions.length > 0 ? '<th>Acciones</th>' : ''}
                        </tr>
                    </thead>
                    <tbody>
                        ${dataToShow.map(row => this.renderTableRow(row)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    renderTableRow(row) {
        return `
            <tr>
                ${this.config.columns.map(col => `
                    <td class="table-cell">
                        ${this.renderCellValue(row, col)}
                    </td>
                `).join('')}
                ${this.config.actions.length > 0 ? `
                    <td class="table-actions">
                        ${this.config.actions.map(action => `
                            <button class="btn btn-sm table-action-btn" 
                                    data-action="${action.name}" 
                                    data-id="${row[action.idField] || row.id}">
                                <i class="${action.icon}"></i> ${action.label}
                            </button>
                        `).join('')}
                    </td>
                ` : ''}
            </tr>
        `;
    }

    renderCellValue(row, column) {
        const value = row[column.key];
        
        if (column.type === 'json') {
            return this.renderJsonField(value, column);
        } else if (column.type === 'date') {
            return new Date(value).toLocaleDateString('es-ES');
        } else if (column.type === 'datetime') {
            return new Date(value).toLocaleString('es-ES');
        } else if (column.type === 'boolean') {
            return value ? '✅ Sí' : '❌ No';
        } else if (column.type === 'number') {
            return typeof value === 'number' ? value.toLocaleString() : value;
        } else if (column.type === 'currency') {
            return typeof value === 'number' ? `$${value.toFixed(2)}` : value;
        } else if (column.type === 'status') {
            return this.renderStatusBadge(value);
        } else if (column.type === 'custom' && column.render) {
            return column.render(value, row);
        } else {
            return value || '-';
        }
    }

    renderJsonField(value, column) {
        if (!Array.isArray(value)) {
            return value || '-';
        }

        const maxItems = column.maxItems || 3;
        const items = value.slice(0, maxItems);
        const remaining = value.length - maxItems;

        let html = items.map(item => `
            <span class="json-chip">${item}</span>
        `).join('');

        if (remaining > 0) {
            html += `<span class="json-chip-more">+${remaining} más</span>`;
        }

        return html;
    }

    renderStatusBadge(status) {
        const statusMap = {
            'success': { class: 'success', icon: '✅' },
            'error': { class: 'error', icon: '❌' },
            'warning': { class: 'warning', icon: '⚠️' },
            'info': { class: 'info', icon: 'ℹ️' },
            'pending': { class: 'pending', icon: '⏳' }
        };

        const statusInfo = statusMap[status] || { class: 'default', icon: '📄' };
        
        return `
            <span class="status-badge ${statusInfo.class}">
                ${statusInfo.icon} ${status}
            </span>
        `;
    }

    renderTableFooter() {
        if (!this.config.pagination) return '';

        const totalPages = Math.ceil(this.filteredData.length / this.config.itemsPerPage);
        
        if (totalPages <= 1) return '';

        let paginationHTML = '<div class="table-pagination">';
        
        // Información de paginación
        const startItem = (this.currentPage - 1) * this.config.itemsPerPage + 1;
        const endItem = Math.min(this.currentPage * this.config.itemsPerPage, this.filteredData.length);
        
        paginationHTML += `
            <div class="pagination-info">
                Mostrando ${startItem}-${endItem} de ${this.filteredData.length} registros
            </div>
        `;

        // Botones de paginación
        paginationHTML += '<div class="pagination-buttons">';
        
        // Botón anterior
        if (this.currentPage > 1) {
            paginationHTML += `
                <button class="table-page-btn" data-page="${this.currentPage - 1}">
                    <i class="fas fa-chevron-left"></i>
                </button>
            `;
        }

        // Páginas
        for (let i = 1; i <= totalPages; i++) {
            if (i === this.currentPage) {
                paginationHTML += `<button class="table-page-btn active">${i}</button>`;
            } else {
                paginationHTML += `<button class="table-page-btn" data-page="${i}">${i}</button>`;
            }
        }

        // Botón siguiente
        if (this.currentPage < totalPages) {
            paginationHTML += `
                <button class="table-page-btn" data-page="${this.currentPage + 1}">
                    <i class="fas fa-chevron-right"></i>
                </button>
            `;
        }

        paginationHTML += '</div></div>';
        return paginationHTML;
    }

    applyFilters() {
        this.filteredData = this.data.filter(row => {
            if (!this.searchTerm) return true;
            
            return this.config.columns.some(col => {
                const value = row[col.key];
                if (typeof value === 'string') {
                    return value.toLowerCase().includes(this.searchTerm);
                } else if (Array.isArray(value)) {
                    return value.some(item => 
                        item.toLowerCase().includes(this.searchTerm)
                    );
                }
                return false;
            });
        });

        this.currentPage = 1;
        this.renderTable();
    }

    sortBy(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }

        this.filteredData.sort((a, b) => {
            const aVal = a[column];
            const bVal = b[column];
            
            if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        this.renderTable();
    }

    goToPage(page) {
        this.currentPage = page;
        this.renderTable();
    }

    handleAction(action, id) {
        if (this.config.onAction) {
            this.config.onAction(action, id);
        } else {
            console.log(`Acción ${action} para ID ${id}`);
        }
    }

    showError(message) {
        if (window.Utils) {
            window.Utils.showNotification(message, 'error');
        } else {
            alert(message);
        }
    }

    // Método para actualizar datos
    refresh() {
        this.loadData();
    }

    // Método para exportar datos
    exportToCSV() {
        const csvContent = this.generateCSV();
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.config.title || 'datos'}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    generateCSV() {
        const headers = this.config.columns.map(col => col.title).join(',');
        const rows = this.filteredData.map(row => 
            this.config.columns.map(col => {
                const value = row[col.key];
                return typeof value === 'string' ? `"${value}"` : value;
            }).join(',')
        );
        
        return [headers, ...rows].join('\n');
    }
}

// Exportar para uso global
window.DataTableComponent = DataTableComponent;
