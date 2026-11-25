/**
 * Upload Menu Component
 * Maneja la carga y análisis de menús
 */

class UploadMenuComponent {
    constructor() {
        this.menuTextArea = null;
        this.analyzeButton = null;
        this.loadingSpinner = null;
        this.init();
    }

    init() {
        this.menuTextArea = document.getElementById('menu-text');
        this.analyzeButton = document.getElementById('analyze-btn');
        this.loadingSpinner = document.getElementById('loading-spinner');
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.analyzeButton) {
            this.analyzeButton.addEventListener('click', () => {
                this.handleAnalyzeMenu();
            });
        }

        // Permitir análisis con Enter + Ctrl
        if (this.menuTextArea) {
            this.menuTextArea.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    this.handleAnalyzeMenu();
                }
            });
        }
    }

    async handleAnalyzeMenu() {
        const menuText = this.menuTextArea ? this.menuTextArea.value.trim() : '';
        
        if (!menuText) {
            this.showError('Por favor, ingresa el texto del menú');
            return;
        }

        // Verificar autenticación
        const userData = this.getCurrentUser();
        if (!userData) {
            this.showError('Debes estar autenticado para analizar menús');
            return;
        }

        try {
            this.showLoading(true);
            
            const result = await this.analyzeMenu(menuText, userData.id_usuario);
            
            // Actualizar estado global
            if (window.AppState) {
                window.AppState.currentAnalysis = result;
            }
            
            // Mostrar resultados
            if (window.AnalysisResultComponent) {
                const analysisComponent = new window.AnalysisResultComponent();
                analysisComponent.render(result);
            }
            
            // Actualizar opciones de feedback
            if (window.FeedbackFormComponent) {
                const feedbackComponent = new window.FeedbackFormComponent();
                feedbackComponent.updateDishOptions(result.platos || []);
            }
            
            console.log('Análisis completado:', result);
            
        } catch (error) {
            console.error('Error analizando menú:', error);
            this.showError('Error al analizar el menú. Por favor, intenta de nuevo.');
        } finally {
            this.showLoading(false);
        }
    }

    async analyzeMenu(menuText, usuarioId) {
        try {
            const response = await fetch(`${window.API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    menu_text: menuText,
                    usuario_id: usuarioId
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error en API analyze:', error);
            throw error;
        }
    }

    showLoading(show) {
        if (this.analyzeButton) {
            this.analyzeButton.style.display = show ? 'none' : 'inline-flex';
        }
        
        if (this.loadingSpinner) {
            this.loadingSpinner.style.display = show ? 'flex' : 'none';
        }
    }

    showError(message) {
        // Crear o actualizar mensaje de error
        let errorDiv = document.getElementById('upload-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'upload-error';
            errorDiv.className = 'error-message';
            
            // Insertar después del textarea
            if (this.menuTextArea && this.menuTextArea.parentNode) {
                this.menuTextArea.parentNode.insertBefore(errorDiv, this.menuTextArea.nextSibling);
            }
        }
        
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            ${message}
        `;
        
        // Ocultar después de 5 segundos
        setTimeout(() => {
            if (errorDiv) {
                errorDiv.style.display = 'none';
            }
        }, 5000);
    }

    // Método para obtener usuario actual
    getCurrentUser() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    }

    // Método para limpiar el formulario
    clearForm() {
        if (this.menuTextArea) {
            this.menuTextArea.value = '';
        }
    }

    // Método para establecer texto del menú
    setMenuText(text) {
        if (this.menuTextArea) {
            this.menuTextArea.value = text;
        }
    }

    // Método para obtener texto del menú
    getMenuText() {
        return this.menuTextArea ? this.menuTextArea.value.trim() : '';
    }
}

// Exportar para uso global
window.UploadMenuComponent = UploadMenuComponent;

