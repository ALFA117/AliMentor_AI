/**
 * Profile Component
 * Muestra información del usuario y historial de feedbacks
 */

class ProfileComponent {
    constructor() {
        this.profileContainer = null;
        this.userData = null;
        this.init();
    }

    init() {
        this.profileContainer = document.getElementById('profile-container');
        this.userData = this.getCurrentUser();
        
        if (this.userData) {
            this.render();
        }
    }

    async render() {
        if (!this.profileContainer || !this.userData) return;

        try {
            // Cargar datos del perfil desde el backend
            const profileData = await this.loadProfileData();
            
            this.profileContainer.innerHTML = `
                <div class="profile-card">
                    <div class="profile-header">
                        <div class="profile-avatar">
                            ${this.getUserInitials()}
                        </div>
                        <div class="profile-info">
                            <h3>${this.userData.nombre}</h3>
                            <p>ID: ${this.userData.id_usuario}</p>
                            <p>Usuario desde: ${new Date().toLocaleDateString('es-ES')}</p>
                        </div>
                    </div>
                    
                    <div class="profile-stats">
                        <div class="stat-item">
                            <span class="stat-value" id="analyses-count">${profileData.total_analisis || 0}</span>
                            <span class="stat-label">Análisis Realizados</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value" id="feedbacks-count">${profileData.total_feedback || 0}</span>
                            <span class="stat-label">Feedbacks Enviados</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value" id="average-rating">${profileData.promedio_calificacion || '0.0'}</span>
                            <span class="stat-label">Calificación Promedio</span>
                        </div>
                    </div>

                    <div class="profile-sections">
                        <div class="section">
                            <h3><i class="fas fa-history"></i> Historial de Feedbacks</h3>
                            <div id="feedback-history" class="feedback-history">
                                ${this.renderFeedbackHistory(profileData.feedbacks || [])}
                            </div>
                        </div>

                        <div class="section">
                            <h3><i class="fas fa-chart-bar"></i> Estadísticas Personales</h3>
                            <div class="personal-stats">
                                <div class="stat-chart">
                                    <canvas id="personal-chart"></canvas>
                                </div>
                            </div>
                        </div>

                        <div class="section">
                            <h3><i class="fas fa-cog"></i> Configuración</h3>
                            <div class="profile-settings">
                                <div class="setting-item">
                                    <label>
                                        <input type="checkbox" id="notifications" checked>
                                        Notificaciones por email
                                    </label>
                                </div>
                                <div class="setting-item">
                                    <label>
                                        <input type="checkbox" id="analytics" checked>
                                        Compartir datos para mejorar el servicio
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            this.setupEventListeners();
            this.createPersonalChart(profileData);
            
        } catch (error) {
            console.error('Error cargando perfil:', error);
            this.showError('Error al cargar el perfil del usuario');
        }
    }

    async loadProfileData() {
        try {
            const response = await fetch(`${window.API_BASE_URL}/profile/${this.userData.id_usuario}`);
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error cargando datos del perfil:', error);
            // Retornar datos por defecto si hay error
            return {
                total_analisis: 0,
                total_feedback: 0,
                promedio_calificacion: 0,
                feedbacks: []
            };
        }
    }

    getUserInitials() {
        return this.userData.nombre.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    renderFeedbackHistory(feedbacks) {
        if (feedbacks.length === 0) {
            return `
                <div class="empty-state">
                    <i class="fas fa-comment-slash"></i>
                    <p>No hay feedbacks registrados</p>
                </div>
            `;
        }

        return feedbacks.map(feedback => `
            <div class="feedback-item">
                <div class="feedback-header">
                    <h4>${feedback.plato_nombre || 'Platillo'}</h4>
                    <div class="feedback-rating">
                        ${this.renderStars(feedback.calificacion || 0)}
                    </div>
                </div>
                <p class="feedback-comment">${feedback.comentario || 'Sin comentario'}</p>
                <span class="feedback-date">${new Date(feedback.fecha_creacion).toLocaleDateString('es-ES')}</span>
            </div>
        `).join('');
    }

    renderStars(rating) {
        return Array.from({ length: 5 }, (_, i) => 
            `<i class="fas fa-star ${i < rating ? 'active' : ''}"></i>`
        ).join('');
    }

    setupEventListeners() {
        // Configurar checkboxes
        const notifications = document.getElementById('notifications');
        const analytics = document.getElementById('analytics');

        if (notifications) {
            notifications.addEventListener('change', (e) => {
                this.updateSetting('notifications', e.target.checked);
            });
        }

        if (analytics) {
            analytics.addEventListener('change', (e) => {
                this.updateSetting('analytics', e.target.checked);
            });
        }
    }

    createPersonalChart(profileData) {
        const ctx = document.getElementById('personal-chart');
        if (!ctx || typeof Chart === 'undefined') return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Análisis', 'Feedbacks', 'Mejoras'],
                datasets: [{
                    data: [
                        profileData.total_analisis || 0,
                        profileData.total_feedback || 0,
                        profileData.total_mejoras || 0
                    ],
                    backgroundColor: ['#4ecdc4', '#45b7aa', '#ff6b6b'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 10,
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }

    updateSetting(setting, value) {
        // Guardar configuración en localStorage
        const settings = JSON.parse(localStorage.getItem('userSettings') || '{}');
        settings[setting] = value;
        localStorage.setItem('userSettings', JSON.stringify(settings));
        
        console.log(`Configuración ${setting} actualizada:`, value);
    }

    // Método para obtener usuario actual
    getCurrentUser() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    }

    // Método para actualizar perfil
    updateProfile(newData) {
        const currentData = this.getCurrentUser();
        const updatedData = { ...currentData, ...newData };
        
        localStorage.setItem('userData', JSON.stringify(updatedData));
        this.userData = updatedData;
        this.render();
    }

    // Método para exportar datos del usuario
    exportUserData() {
        const userData = this.getCurrentUser();
        const settings = JSON.parse(localStorage.getItem('userSettings') || '{}');
        
        const exportData = {
            user: userData,
            settings: settings,
            export_date: new Date().toISOString()
        };

        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `alimentor-profile-${userData.id_usuario}.json`;
        link.click();
    }

    showError(message) {
        if (!this.profileContainer) return;
        
        this.profileContainer.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                ${message}
            </div>
        `;
    }
}

// Exportar para uso global
window.ProfileComponent = ProfileComponent;

