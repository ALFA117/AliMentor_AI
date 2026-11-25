/**
 * Feedback Panel Component
 * Maneja el panel de feedback con modal y animaciones
 */

class FeedbackPanelComponent {
    constructor() {
        this.feedbackContainer = null;
        this.currentPlatoId = null;
        this.currentUserId = null;
        this.init();
    }

    init() {
        this.feedbackContainer = document.getElementById('feedback-container');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Event listener para cerrar modal
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('close-feedback-modal') || 
                e.target.classList.contains('modal-overlay')) {
                this.closeFeedbackModal();
            }
        });

        // Event listener para enviar feedback
        document.addEventListener('click', (e) => {
            if (e.target.id === 'submit-feedback-btn') {
                this.submitFeedback();
            }
        });

        // Event listener para estrellas de calificación
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('rating-star')) {
                const rating = parseInt(e.target.dataset.rating);
                this.setRating(rating);
            }
        });

        // Event listener para tipo de feedback
        document.addEventListener('change', (e) => {
            if (e.target.id === 'feedback-type') {
                this.updateFeedbackType(e.target.value);
            }
        });
    }

    showModal(platoId, userId = null) {
        this.currentPlatoId = platoId;
        this.currentUserId = userId || this.getCurrentUserId();
        
        if (!this.currentUserId) {
            this.showError('Debes iniciar sesión para dar feedback');
            return;
        }

        this.renderFeedbackModal();
        this.showFeedbackModal();
    }

    renderFeedbackModal() {
        const modalHTML = `
            <div class="feedback-modal">
                <div class="modal-overlay"></div>
                <div class="modal-content feedback-modal-content">
                    <div class="modal-header">
                        <h2>💬 Dar Feedback</h2>
                        <button class="modal-close close-feedback-modal">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div class="feedback-modal-body">
                        <div class="feedback-form">
                            <div class="feedback-rating-section">
                                <h3>⭐ Calificación</h3>
                                <div class="rating-stars">
                                    <i class="fas fa-star rating-star" data-rating="1"></i>
                                    <i class="fas fa-star rating-star" data-rating="2"></i>
                                    <i class="fas fa-star rating-star" data-rating="3"></i>
                                    <i class="fas fa-star rating-star" data-rating="4"></i>
                                    <i class="fas fa-star rating-star" data-rating="5"></i>
                                </div>
                                <p class="rating-text">Selecciona una calificación</p>
                            </div>

                            <div class="feedback-type-section">
                                <h3>📝 Tipo de Feedback</h3>
                                <select id="feedback-type" class="feedback-type-select">
                                    <option value="positivo">👍 Positivo</option>
                                    <option value="negativo">👎 Negativo</option>
                                    <option value="correccion">🔧 Corrección</option>
                                    <option value="sugerencia">💡 Sugerencia</option>
                                </select>
                            </div>

                            <div class="feedback-comment-section">
                                <h3>💭 Comentario</h3>
                                <textarea 
                                    id="feedback-comment" 
                                    class="feedback-comment-textarea"
                                    placeholder="Comparte tu experiencia con este plato..."
                                    rows="4"
                                    maxlength="500"
                                ></textarea>
                                <div class="character-count">
                                    <span id="char-count">0</span>/500 caracteres
                                </div>
                            </div>

                            <div class="feedback-actions">
                                <button id="submit-feedback-btn" class="btn btn-primary">
                                    <i class="fas fa-paper-plane"></i> Enviar Feedback
                                </button>
                                <button class="btn btn-secondary close-feedback-modal">
                                    <i class="fas fa-times"></i> Cancelar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Crear modal si no existe
        let modal = document.querySelector('.feedback-modal');
        if (modal) {
            modal.remove();
        }

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Configurar contador de caracteres
        this.setupCharacterCounter();
    }

    setupCharacterCounter() {
        const textarea = document.getElementById('feedback-comment');
        const counter = document.getElementById('char-count');
        
        if (textarea && counter) {
            textarea.addEventListener('input', () => {
                const count = textarea.value.length;
                counter.textContent = count;
                
                if (count > 450) {
                    counter.style.color = 'var(--warning-color)';
                } else if (count > 400) {
                    counter.style.color = 'var(--primary-color)';
                } else {
                    counter.style.color = 'var(--text-secondary)';
                }
            });
        }
    }

    showFeedbackModal() {
        const modal = document.querySelector('.feedback-modal');
        if (modal) {
            modal.style.display = 'flex';
            modal.classList.add('modal-fade-in');
            
            // Animar el contenido
            const content = modal.querySelector('.modal-content');
            content.classList.add('modal-slide-up');
        }
    }

    closeFeedbackModal() {
        const modal = document.querySelector('.feedback-modal');
        if (modal) {
            modal.classList.remove('modal-fade-in');
            modal.classList.add('modal-fade-out');
            
            setTimeout(() => {
                modal.remove();
            }, 300);
        }
    }

    setRating(rating) {
        const stars = document.querySelectorAll('.rating-star');
        const ratingText = document.querySelector('.rating-text');
        
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });

        // Actualizar texto de calificación
        const ratingTexts = {
            1: 'Muy malo',
            2: 'Malo',
            3: 'Regular',
            4: 'Bueno',
            5: 'Excelente'
        };
        
        if (ratingText) {
            ratingText.textContent = ratingTexts[rating] || 'Selecciona una calificación';
        }
    }

    updateFeedbackType(type) {
        const typeEmojis = {
            'positivo': '👍',
            'negativo': '👎',
            'correccion': '🔧',
            'sugerencia': '💡'
        };
        
        const emoji = typeEmojis[type] || '💬';
        console.log(`Tipo de feedback seleccionado: ${emoji} ${type}`);
    }

    async submitFeedback() {
        try {
            const rating = document.querySelectorAll('.rating-star.active').length;
            const type = document.getElementById('feedback-type').value;
            const comment = document.getElementById('feedback-comment').value.trim();

            // Validar datos
            if (rating === 0) {
                this.showError('Por favor selecciona una calificación');
                return;
            }

            if (comment.length < 10) {
                this.showError('El comentario debe tener al menos 10 caracteres');
                return;
            }

            // Mostrar loading
            const submitBtn = document.getElementById('submit-feedback-btn');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
            submitBtn.disabled = true;

            // Enviar feedback
            const response = await fetch(`${window.API_BASE_URL}/feedback`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    usuario_id: this.currentUserId,
                    plato_id: this.currentPlatoId,
                    calificacion: rating,
                    tipo_feedback: type,
                    comentario: comment
                })
            });

            if (response.ok) {
                const data = await response.json();
                
                // Mostrar mensaje de éxito animado
                this.showSuccessMessage();
                
                // Cerrar modal después de un delay
                setTimeout(() => {
                    this.closeFeedbackModal();
                }, 2000);
                
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Error enviando feedback');
            }

        } catch (error) {
            console.error('Error enviando feedback:', error);
            this.showError('Error enviando feedback: ' + error.message);
            
            // Restaurar botón
            const submitBtn = document.getElementById('submit-feedback-btn');
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Feedback';
            submitBtn.disabled = false;
        }
    }

    showSuccessMessage() {
        const modal = document.querySelector('.feedback-modal');
        if (!modal) return;

        const successHTML = `
            <div class="feedback-success">
                <div class="success-animation">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h3>¡Gracias por tu aporte! 🍽️</h3>
                <p>Tu feedback ha sido enviado correctamente</p>
            </div>
        `;

        const body = modal.querySelector('.feedback-modal-body');
        body.innerHTML = successHTML;
        body.classList.add('success-animation');
    }

    getCurrentUserId() {
        // Intentar obtener el ID del usuario desde localStorage
        const userData = localStorage.getItem('userData');
        if (userData) {
            try {
                const user = JSON.parse(userData);
                return user.id_usuario;
            } catch (error) {
                console.error('Error parsing user data:', error);
            }
        }
        return null;
    }

    showError(message) {
        if (window.Utils) {
            window.Utils.showNotification(message, 'error');
        } else {
            alert(message);
        }
    }

    // Método para mostrar feedback existente
    async loadFeedback(platoId, userId = null) {
        try {
            const params = new URLSearchParams();
            if (platoId) params.append('plato_id', platoId);
            if (userId) params.append('usuario_id', userId);

            const response = await fetch(`${window.API_BASE_URL}/feedback?${params}`);
            
            if (response.ok) {
                const data = await response.json();
                return data.feedback || [];
            } else {
                console.error('Error cargando feedback:', response.statusText);
                return [];
            }
        } catch (error) {
            console.error('Error cargando feedback:', error);
            return [];
        }
    }
}

// Exportar para uso global
window.FeedbackPanelComponent = FeedbackPanelComponent;
