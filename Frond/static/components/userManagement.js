/**
 * User Management Component
 * Maneja la gestión de usuarios (agregar, listar, etc.)
 */

class UserManagementComponent {
    constructor() {
        this.usersList = [];
        this.init();
    }

    init() {
        this.loadUsers();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Event listener para el botón de agregar usuario
        const addUserBtn = document.getElementById('add-user-btn');
        if (addUserBtn) {
            addUserBtn.addEventListener('click', () => this.showAddUserForm());
        }

        // Event listener para el formulario de agregar usuario
        const addUserForm = document.getElementById('add-user-form');
        if (addUserForm) {
            addUserForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addUser();
            });
        }
    }

    async loadUsers() {
        try {
            const response = await fetch(`${window.API_BASE_URL}/users`);
            if (response.ok) {
                const data = await response.json();
                this.usersList = data.usuarios || [];
                this.displayUsers();
                console.log('✅ Usuarios cargados:', this.usersList.length);
            } else {
                console.error('❌ Error cargando usuarios:', response.statusText);
            }
        } catch (error) {
            console.error('❌ Error cargando usuarios:', error);
        }
    }

    displayUsers() {
        const usersContainer = document.getElementById('users-list');
        if (!usersContainer) return;

        if (this.usersList.length === 0) {
            usersContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-users"></i>
                    <p>No hay usuarios registrados</p>
                </div>
            `;
            return;
        }

        usersContainer.innerHTML = this.usersList.map(user => `
            <div class="user-card">
                <div class="user-info">
                    <div class="user-avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="user-details">
                        <h3>${user.nombre}</h3>
                        <p>ID: ${user.id_usuario}</p>
                        <p>Edad: ${user.edad} años</p>
                        <p>Género: ${user.genero}</p>
                    </div>
                </div>
                <div class="user-actions">
                    <button class="btn btn-sm btn-primary" onclick="userManagement.loginAsUser('${user.nombre}')">
                        <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
                    </button>
                </div>
            </div>
        `).join('');
    }

    showAddUserForm() {
        // Crear modal para agregar usuario
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2><i class="fas fa-user-plus"></i> Agregar Usuario</h2>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="add-user-form">
                        <div class="form-group">
                            <label for="user-name">Nombre:</label>
                            <input type="text" id="user-name" name="nombre" required>
                        </div>
                        <div class="form-group">
                            <label for="user-age">Edad:</label>
                            <input type="number" id="user-age" name="edad" min="1" max="120" value="25">
                        </div>
                        <div class="form-group">
                            <label for="user-gender">Género:</label>
                            <select id="user-gender" name="genero">
                                <option value="Masculino">Masculino</option>
                                <option value="Femenino">Femenino</option>
                                <option value="No especificado">No especificado</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="user-restrictions">Restricciones (separadas por comas):</label>
                            <input type="text" id="user-restrictions" name="restricciones" placeholder="Ej: sin gluten, vegetariano">
                        </div>
                        <div class="form-group">
                            <label for="user-allergies">Alergias (separadas por comas):</label>
                            <input type="text" id="user-allergies" name="alergias" placeholder="Ej: nuez, mariscos">
                        </div>
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                                Cancelar
                            </button>
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-plus"></i> Agregar Usuario
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Configurar event listener para el formulario
        const form = modal.querySelector('#add-user-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addUser();
            modal.remove();
        });
    }

    async addUser() {
        try {
            const form = document.getElementById('add-user-form');
            const formData = new FormData(form);
            
            const userData = {
                nombre: formData.get('nombre'),
                edad: parseInt(formData.get('edad')),
                genero: formData.get('genero'),
                restricciones: formData.get('restricciones').split(',').map(r => r.trim()).filter(r => r),
                alergias: formData.get('alergias').split(',').map(a => a.trim()).filter(a => a),
                enfermedades: []
            };

            const response = await fetch(`${window.API_BASE_URL}/users`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                const result = await response.json();
                console.log('✅ Usuario agregado:', result);
                
                if (window.Utils) {
                    window.Utils.showNotification('Usuario agregado correctamente', 'success');
                }
                
                // Recargar lista de usuarios
                this.loadUsers();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Error agregando usuario');
            }
        } catch (error) {
            console.error('❌ Error agregando usuario:', error);
            if (window.Utils) {
                window.Utils.showNotification('Error agregando usuario: ' + error.message, 'error');
            }
        }
    }

    async loginAsUser(nombre) {
        try {
            // Usar el componente de login existente
            if (window.LoginComponent) {
                const loginComponent = new window.LoginComponent();
                // Simular el login
                document.getElementById('username').value = nombre;
                await loginComponent.handleLogin();
            }
        } catch (error) {
            console.error('❌ Error iniciando sesión:', error);
            if (window.Utils) {
                window.Utils.showNotification('Error iniciando sesión: ' + error.message, 'error');
            }
        }
    }

    // Método para mostrar la interfaz de gestión de usuarios
    showUserManagement() {
        const container = document.getElementById('user-management-container');
        if (!container) return;

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h2><i class="fas fa-users"></i> Gestión de Usuarios</h2>
                    <button id="add-user-btn" class="btn btn-primary">
                        <i class="fas fa-plus"></i> Agregar Usuario
                    </button>
                </div>
                <div class="card-body">
                    <div id="users-list">
                        <!-- Se llena dinámicamente -->
                    </div>
                </div>
            </div>
        `;

        // Recargar usuarios y configurar event listeners
        this.loadUsers();
        this.setupEventListeners();
    }
}

// Exportar para uso global
window.UserManagementComponent = UserManagementComponent;
