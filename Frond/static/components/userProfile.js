/**
 * User Profile Component
 * Maneja la vista y edición del perfil de usuario
 */

class UserProfileComponent {
    constructor() {
        this.profileContainer = null;
        this.currentUser = null;
        this.jsonHandler = null;
        this.init();
    }

    init() {
        this.profileContainer = document.getElementById('profile-container');
        this.jsonHandler = new window.JsonFieldHandler();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Event listener para guardar perfil
        document.addEventListener('click', (e) => {
            if (e.target.id === 'save-profile-btn') {
                this.saveProfile();
            }
            if (e.target.id === 'edit-profile-btn') {
                this.toggleEditMode();
            }
        });
    }

    async loadProfile(userId) {
        try {
            const response = await fetch(`${window.API_BASE_URL}/usuarios/${userId}`);
            
            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.usuario;
                this.renderProfile();
            } else {
                console.error('Error cargando perfil:', response.statusText);
                this.showError('Error cargando perfil de usuario');
            }
        } catch (error) {
            console.error('Error cargando perfil:', error);
            this.showError('Error de conexión al cargar perfil');
        }
    }

    renderProfile() {
        if (!this.profileContainer || !this.currentUser) return;

        this.profileContainer.innerHTML = `
            <div class="profile-card">
                <div class="profile-header">
                    <div class="profile-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="profile-info">
                        <h2>${this.currentUser.nombre}</h2>
                        <p class="profile-subtitle">Usuario desde ${new Date(this.currentUser.fecha_creacion).toLocaleDateString('es-ES')}</p>
                    </div>
                    <button id="edit-profile-btn" class="btn btn-secondary">
                        <i class="fas fa-edit"></i> Editar Perfil
                    </button>
                </div>

                <div class="profile-content">
                    <div class="profile-section">
                        <h3><i class="fas fa-info-circle"></i> Información Personal</h3>
                        <div class="profile-grid">
                            <div class="profile-field">
                                <label>Edad:</label>
                                <span id="edad-display">${this.currentUser.edad} años</span>
                                <input type="number" id="edad-input" value="${this.currentUser.edad}" style="display: none;" min="1" max="120">
                            </div>
                            <div class="profile-field">
                                <label>Género:</label>
                                <span id="genero-display">${this.currentUser.genero}</span>
                                <select id="genero-input" style="display: none;">
                                    <option value="Masculino" ${this.currentUser.genero === 'Masculino' ? 'selected' : ''}>Masculino</option>
                                    <option value="Femenino" ${this.currentUser.genero === 'Femenino' ? 'selected' : ''}>Femenino</option>
                                    <option value="No especificado" ${this.currentUser.genero === 'No especificado' ? 'selected' : ''}>No especificado</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="profile-section">
                        <h3><i class="fas fa-exclamation-triangle"></i> Restricciones Alimentarias</h3>
                        <div id="restricciones-container" class="chips-container"></div>
                    </div>

                    <div class="profile-section">
                        <h3><i class="fas fa-allergies"></i> Alergias</h3>
                        <div id="alergias-container" class="chips-container"></div>
                    </div>

                    <div class="profile-section">
                        <h3><i class="fas fa-heartbeat"></i> Enfermedades</h3>
                        <div id="enfermedades-container" class="chips-container"></div>
                    </div>

                    <div class="profile-actions" style="display: none;">
                        <button id="save-profile-btn" class="btn btn-primary">
                            <i class="fas fa-save"></i> Guardar Cambios
                        </button>
                        <button id="cancel-edit-btn" class="btn btn-secondary">
                            <i class="fas fa-times"></i> Cancelar
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Renderizar campos JSON como chips
        this.jsonHandler.renderRestrictions(this.currentUser.restricciones, 'restricciones-container', false);
        this.jsonHandler.renderAllergens(this.currentUser.alergias, 'alergias-container', false);
        this.jsonHandler.renderDiseases(this.currentUser.enfermedades, 'enfermedades-container', false);

        // Configurar event listeners para cancelar edición
        document.getElementById('cancel-edit-btn')?.addEventListener('click', () => {
            this.toggleEditMode();
        });
    }

    toggleEditMode() {
        const isEditing = document.getElementById('edad-input').style.display !== 'none';
        
        if (isEditing) {
            // Salir del modo edición
            document.getElementById('edad-display').style.display = 'inline';
            document.getElementById('edad-input').style.display = 'none';
            document.getElementById('genero-display').style.display = 'inline';
            document.getElementById('genero-input').style.display = 'none';
            document.getElementById('edit-profile-btn').style.display = 'inline-flex';
            document.querySelector('.profile-actions').style.display = 'none';
            
            // Hacer chips no editables
            this.jsonHandler.renderRestrictions(this.currentUser.restricciones, 'restricciones-container', false);
            this.jsonHandler.renderAllergens(this.currentUser.alergias, 'alergias-container', false);
            this.jsonHandler.renderDiseases(this.currentUser.enfermedades, 'enfermedades-container', false);
        } else {
            // Entrar al modo edición
            document.getElementById('edad-display').style.display = 'none';
            document.getElementById('edad-input').style.display = 'inline';
            document.getElementById('genero-display').style.display = 'none';
            document.getElementById('genero-input').style.display = 'inline';
            document.getElementById('edit-profile-btn').style.display = 'none';
            document.querySelector('.profile-actions').style.display = 'flex';
            
            // Hacer chips editables
            this.jsonHandler.renderRestrictions(this.currentUser.restricciones, 'restricciones-container', true);
            this.jsonHandler.renderAllergens(this.currentUser.alergias, 'alergias-container', true);
            this.jsonHandler.renderDiseases(this.currentUser.enfermedades, 'enfermedades-container', true);
        }
    }

    async saveProfile() {
        try {
            // Recopilar datos del formulario
            const updatedData = {
                edad: parseInt(document.getElementById('edad-input').value),
                genero: document.getElementById('genero-input').value,
                restricciones: this.jsonHandler.getChipsData('restricciones-container'),
                alergias: this.jsonHandler.getChipsData('alergias-container'),
                enfermedades: this.jsonHandler.getChipsData('enfermedades-container')
            };

            // Validar datos
            const validation = this.validateProfileData(updatedData);
            if (!validation.valid) {
                this.showError(validation.message);
                return;
            }

            // Enviar actualización
            const response = await fetch(`${window.API_BASE_URL}/usuarios/${this.currentUser.id_usuario}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedData)
            });

            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.usuario;
                
                // Salir del modo edición
                this.toggleEditMode();
                
                // Mostrar mensaje de éxito
                if (window.Utils) {
                    window.Utils.showNotification('Perfil actualizado correctamente', 'success');
                }
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Error actualizando perfil');
            }
        } catch (error) {
            console.error('Error guardando perfil:', error);
            this.showError('Error guardando perfil: ' + error.message);
        }
    }

    validateProfileData(data) {
        if (data.edad < 1 || data.edad > 120) {
            return { valid: false, message: 'La edad debe estar entre 1 y 120 años' };
        }

        const restriccionesValidation = this.jsonHandler.validateChipsData(data.restricciones, {
            maxItems: 10,
            maxLength: 50
        });
        if (!restriccionesValidation.valid) {
            return restriccionesValidation;
        }

        const alergiasValidation = this.jsonHandler.validateChipsData(data.alergias, {
            maxItems: 15,
            maxLength: 50
        });
        if (!alergiasValidation.valid) {
            return alergiasValidation;
        }

        const enfermedadesValidation = this.jsonHandler.validateChipsData(data.enfermedades, {
            maxItems: 10,
            maxLength: 100
        });
        if (!enfermedadesValidation.valid) {
            return enfermedadesValidation;
        }

        return { valid: true };
    }

    showError(message) {
        if (window.Utils) {
            window.Utils.showNotification(message, 'error');
        } else {
            alert(message);
        }
    }

    // Método para obtener el usuario actual
    getCurrentUser() {
        return this.currentUser;
    }

    // Método para actualizar datos del usuario
    updateUserData(newData) {
        this.currentUser = { ...this.currentUser, ...newData };
        this.renderProfile();
    }
}

// Exportar para uso global
window.UserProfileComponent = UserProfileComponent;
