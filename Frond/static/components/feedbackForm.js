/**
 * Feedback Form Component
 * Maneja el formulario de feedback con calificación por estrellas
 */

class FeedbackFormComponent {
    constructor() {
        this.form = null;
        this.dishSelect = null;
        this.typeSelect = null;
        this.ratingStars = null;
        this.commentTextarea = null;
        this.submitButton = null;
        this.successMessage = null;
        this.init();
    }

    init() {
        this.form = document.getElementById('feedback-form');
        this.dishSelect = document.getElementById('feedback-dish');
        this.typeSelect = document.getElementById('feedback-type');
        this.ratingStars = document.querySelectorAll('.rating-stars i');
        this.commentTextarea = document.getElementById('feedback-comment');
        this.submitButton = document.querySelector('#feedback-form button[type="submit"]');
        this.successMessage = document.getElementById('feedback-success');
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Manejar estrellas de calificación
        this.ratingStars.forEach((star, index) => {
            star.addEventListener('click', () => {
                this.setRating(index + 1);
            });
            
            star.addEventListener('mouseenter', () => {
                this.highlightStars(index + 1);
            });
        });

        // Resetear estrellas al salir del área
        const starsContainer = document.querySelector('.rating-stars');
        if (starsContainer) {
            starsContainer.addEventListener('mouseleave', () => {
                this.highlightStars(this.getCurrentRating());
            });
        }

        // Manejar envío del formulario
        if (this.form) {
            this.form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSubmit();
            });
        }
    }

    selectDish(dishName, dishId) {
        if (this.dishSelect) {
            this.dishSelect.value = dishName;
        }
        
        // Scroll al formulario
        const feedbackSection = document.querySelector('.feedback-section');
        if (feedbackSection) {
            feedbackSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Resaltar el platillo en los resultados
        if (window.AnalysisResultComponent) {
            const analysisComponent = new window.AnalysisResultComponent();
            analysisComponent.highlightPlato(dishName);
        }
    }

    updateDishOptions(platos) {
        if (!this.dishSelect) return;
        
        // Limpiar opciones existentes
        this.dishSelect.innerHTML = '<option value="">Selecciona un platillo</option>';
        
        // Agregar opciones de platillos
        platos.forEach(plato => {
            const option = document.createElement('option');
            option.value = plato.nombre;
            option.textContent = plato.nombre;
            option.dataset.platoId = plato.id || '';
            this.dishSelect.appendChild(option);
        });
    }

    setRating(rating) {
        this.ratingStars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    highlightStars(rating) {
        this.ratingStars.forEach((star, index) => {
            if (index < rating) {
                star.style.color = '#ffd700';
            } else {
                star.style.color = '#e0e0e0';
            }
        });
    }

    getCurrentRating() {
        return document.querySelectorAll('.rating-stars i.active').length;
    }

    async handleSubmit() {
        const formData = this.getFormData();
        
        // Validar datos
        if (!this.validateForm(formData)) {
            return;
        }

        try {
            this.showLoading(true);
            
            const result = await this.submitFeedback(formData);
            
            this.showSuccessMessage();
            this.resetForm();
            
            console.log('Feedback enviado:', result);
            
        } catch (error) {
            console.error('Error enviando feedback:', error);
            this.showError('Error al enviar feedback. Por favor, intenta de nuevo.');
        } finally {
            this.showLoading(false);
        }
    }

    getFormData() {
        const userData = this.getCurrentUser();
        const selectedOption = this.dishSelect?.selectedOptions[0];
        
        return {
            usuario_id: userData?.id_usuario || null,
            plato_id: selectedOption?.dataset.platoId || null,
            plato_nombre: this.dishSelect?.value || '',
            tipo_feedback: this.typeSelect?.value || '',
            calificacion: this.getCurrentRating(),
            comentario: this.commentTextarea?.value || ''
        };
    }

    validateForm(formData) {
        if (!formData.plato_nombre) {
            this.showError('Por favor, selecciona un platillo');
            return false;
        }
        
        if (!formData.tipo_feedback) {
            this.showError('Por favor, selecciona el tipo de feedback');
            return false;
        }
        
        if (formData.calificacion === 0) {
            this.showError('Por favor, califica con estrellas');
            return false;
        }
        
        if (!formData.usuario_id) {
            this.showError('Debes estar autenticado para enviar feedback');
            return false;
        }
        
        return true;
    }

    async submitFeedback(formData) {
        try {
            const response = await fetch(`${window.API_BASE_URL}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error en API feedback:', error);
            throw error;
        }
    }

    showLoading(show) {
        if (this.submitButton) {
            this.submitButton.disabled = show;
            this.submitButton.innerHTML = show ? 
                '<i class="fas fa-spinner fa-spin"></i> Enviando...' : 
                '<i class="fas fa-paper-plane"></i> Enviar Feedback';
        }
    }

    showSuccessMessage() {
        if (this.successMessage) {
            this.successMessage.style.display = 'flex';
            
            // Ocultar después de 3 segundos
            setTimeout(() => {
                if (this.successMessage) {
                    this.successMessage.style.display = 'none';
                }
            }, 3000);
        }
    }

    showError(message) {
        // Crear o actualizar mensaje de error
        let errorDiv = document.getElementById('feedback-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'feedback-error';
            errorDiv.className = 'error-message';
            
            // Insertar después del formulario
            if (this.form && this.form.parentNode) {
                this.form.parentNode.insertBefore(errorDiv, this.form.nextSibling);
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

    resetForm() {
        if (this.form) {
            this.form.reset();
        }
        
        // Resetear estrellas
        this.ratingStars.forEach(star => {
            star.classList.remove('active');
            star.style.color = '#e0e0e0';
        });
    }

    // Método para obtener usuario actual
    getCurrentUser() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    }

    // Método para obtener platillos disponibles
    getAvailablePlatos() {
        const options = this.dishSelect?.querySelectorAll('option');
        if (!options) return [];

        return Array.from(options).slice(1).map(option => ({
            id: option.dataset.platoId,
            nombre: option.value
        }));
    }
}

// Exportar para uso global
window.FeedbackFormComponent = FeedbackFormComponent;

