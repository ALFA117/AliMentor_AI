/**
 * Login Component
 * Maneja la autenticación con la base de datos SQLAlchemy
 */

class LoginComponent {
    constructor() {
        this.loginContainer = null;
        this.dashboardContainer = null;
        this.loginForm = null;
        this.init();
    }

    init() {
        this.loginContainer = document.getElementById('login-container');
        this.dashboardContainer = document.getElementById('dashboard-container');
        this.loginForm = document.getElementById('login-form');
        
        // Verificar si hay sesión activa
        this.checkAuthState();
        
        // Configurar event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }
    }

    checkAuthState() {
        // Verificar localStorage para sesión persistente
        const userData = localStorage.getItem('userData');
        if (userData) {
            try {
                const user = JSON.parse(userData);
                this.showDashboard(user);
            } catch (error) {
                console.error('Error parsing user data:', error);
                this.showLogin();
            }
        } else {
            this.showLogin();
        }
    }

    async handleLogin() {
        const username = document.getElementById('username').value.trim();
        
        if (!username) {
            this.showError('Por favor, ingresa tu nombre de usuario');
            return;
        }

        try {
            this.showLoading(true);
            
            const result = await this.loginUser(username);
            
            // Guardar datos del usuario
            const userData = {
                id_usuario: result.id_usuario,
                nombre: result.nombre,
                token: result.token
            };
            
            localStorage.setItem('userData', JSON.stringify(userData));
            
            // Mostrar dashboard
            this.showDashboard(userData);
            
            console.log('Login exitoso:', result);
            
        } catch (error) {
            console.error('Error en login:', error);
            this.showError('Error al iniciar sesión. Verifica tu nombre de usuario.');
        } finally {
            this.showLoading(false);
        }
    }

    async loginUser(username) {
        try {
            const response = await fetch(`${window.API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    nombre: username
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error en API login:', error);
            throw error;
        }
    }

    showLoading(show) {
        const submitBtn = this.loginForm?.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = show;
            submitBtn.innerHTML = show ? 
                '<i class="fas fa-spinner fa-spin"></i> Iniciando sesión...' : 
                '<i class="fas fa-sign-in-alt"></i> Iniciar Sesión';
        }
    }

    showLogin() {
        if (this.loginContainer) {
            this.loginContainer.style.display = 'block';
        }
        if (this.dashboardContainer) {
            this.dashboardContainer.style.display = 'none';
        }
        
        // Ocultar navbar
        if (window.NavbarComponent) {
            const navbar = new window.NavbarComponent();
            navbar.hide();
        }
    }

    showDashboard(userData) {
        if (this.loginContainer) {
            this.loginContainer.style.display = 'none';
        }
        if (this.dashboardContainer) {
            this.dashboardContainer.style.display = 'block';
        }
        
        // Mostrar navbar
        if (window.NavbarComponent) {
            const navbar = new window.NavbarComponent();
            navbar.show();
            navbar.updateUserInfo(userData);
        }
        
        // Actualizar estado global
        if (window.AppState) {
            window.AppState.currentUser = userData.id_usuario;
            window.AppState.isAuthenticated = true;
        }
        
        // Cargar métricas
        if (window.MetricsDashboardComponent) {
            const metrics = new window.MetricsDashboardComponent();
            metrics.loadMetrics();
        }
    }

    async logout() {
        try {
            // Limpiar localStorage
            localStorage.removeItem('userData');
            
            // Limpiar estado de la aplicación
            if (window.AppState) {
                window.AppState.currentUser = null;
                window.AppState.isAuthenticated = false;
                window.AppState.currentAnalysis = null;
            }
            
            console.log('Logout exitoso');
            this.showLogin();
            
        } catch (error) {
            console.error('Error en logout:', error);
            this.showError('Error al cerrar sesión. Por favor, intenta de nuevo.');
        }
    }

    showError(message) {
        // Crear o actualizar mensaje de error
        let errorDiv = document.getElementById('login-error');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'login-error';
            errorDiv.className = 'error-message';
            this.loginForm?.appendChild(errorDiv);
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

    // Método para verificar si hay sesión activa
    isAuthenticated() {
        return this.getCurrentUser() !== null;
    }

    // Método para obtener token de autenticación
    getAuthToken() {
        const userData = this.getCurrentUser();
        return userData ? userData.token : null;
    }
}

// Exportar para uso global
window.LoginComponent = LoginComponent;

