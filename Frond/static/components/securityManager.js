/**
 * Security Manager Component
 * Maneja la seguridad y sesiones de usuario
 */

class SecurityManager {
    constructor() {
        this.currentUser = null;
        this.token = null;
        this.sessionTimeout = 30 * 60 * 1000; // 30 minutos
        this.lastActivity = Date.now();
        this.init();
    }

    init() {
        this.loadSession();
        this.setupEventListeners();
        this.startSessionTimer();
    }

    setupEventListeners() {
        // Event listeners para actividad del usuario
        document.addEventListener('click', () => this.updateActivity());
        document.addEventListener('keypress', () => this.updateActivity());
        document.addEventListener('scroll', () => this.updateActivity());
        document.addEventListener('mousemove', () => this.updateActivity());

        // Event listener para antes de cerrar la página
        window.addEventListener('beforeunload', () => {
            this.saveSession();
        });

        // Event listener para visibilidad de la página
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseSession();
            } else {
                this.resumeSession();
            }
        });
    }

    // Métodos de sesión
    loadSession() {
        try {
            const sessionData = localStorage.getItem('userSession');
            if (sessionData) {
                const session = JSON.parse(sessionData);
                
                // Verificar si la sesión no ha expirado
                if (session.expiresAt && Date.now() < session.expiresAt) {
                    this.currentUser = session.user;
                    this.token = session.token;
                    this.lastActivity = session.lastActivity || Date.now();
                    
                    // Actualizar UI si hay usuario logueado
                    this.updateUI();
                    return true;
                } else {
                    // Sesión expirada
                    this.clearSession();
                }
            }
        } catch (error) {
            console.error('Error cargando sesión:', error);
            this.clearSession();
        }
        return false;
    }

    saveSession() {
        try {
            if (this.currentUser && this.token) {
                const sessionData = {
                    user: this.currentUser,
                    token: this.token,
                    lastActivity: this.lastActivity,
                    expiresAt: this.lastActivity + this.sessionTimeout
                };
                
                localStorage.setItem('userSession', JSON.stringify(sessionData));
            }
        } catch (error) {
            console.error('Error guardando sesión:', error);
        }
    }

    clearSession() {
        this.currentUser = null;
        this.token = null;
        this.lastActivity = Date.now();
        
        localStorage.removeItem('userSession');
        this.updateUI();
    }

    // Métodos de autenticación
    async login(credentials) {
        try {
            const response = await fetch(`${window.API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials)
            });

            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.currentUser = data.user;
                    this.token = data.token;
                    this.lastActivity = Date.now();
                    
                    this.saveSession();
                    this.updateUI();
                    
                    return { success: true, user: data.user };
                } else {
                    return { success: false, error: data.error || 'Error de autenticación' };
                }
            } else {
                const errorData = await response.json();
                return { success: false, error: errorData.error || 'Error de conexión' };
            }
        } catch (error) {
            console.error('Error en login:', error);
            return { success: false, error: 'Error de conexión al servidor' };
        }
    }

    async logout() {
        try {
            // Enviar logout al servidor si hay token
            if (this.token) {
                await fetch(`${window.API_BASE_URL}/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.token}`,
                        'Content-Type': 'application/json'
                    }
                });
            }
        } catch (error) {
            console.error('Error en logout:', error);
        } finally {
            this.clearSession();
        }
    }

    // Métodos de autorización
    isAuthenticated() {
        return this.currentUser !== null && this.token !== null;
    }

    hasRole(role) {
        return this.currentUser && this.currentUser.role === role;
    }

    hasPermission(permission) {
        if (!this.currentUser || !this.currentUser.permissions) {
            return false;
        }
        return this.currentUser.permissions.includes(permission);
    }

    getCurrentUser() {
        return this.currentUser;
    }

    getToken() {
        return this.token;
    }

    // Métodos de actividad
    updateActivity() {
        this.lastActivity = Date.now();
        this.saveSession();
    }

    startSessionTimer() {
        setInterval(() => {
            this.checkSessionTimeout();
        }, 60000); // Verificar cada minuto
    }

    checkSessionTimeout() {
        if (this.isAuthenticated()) {
            const timeSinceActivity = Date.now() - this.lastActivity;
            
            if (timeSinceActivity > this.sessionTimeout) {
                this.handleSessionTimeout();
            } else if (timeSinceActivity > this.sessionTimeout * 0.8) {
                // Mostrar advertencia cuando quedan 6 minutos
                this.showSessionWarning();
            }
        }
    }

    handleSessionTimeout() {
        this.showNotification('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning');
        this.logout();
        this.redirectToLogin();
    }

    showSessionWarning() {
        if (!document.querySelector('.session-warning')) {
            this.showNotification('Tu sesión expirará en 6 minutos. ¿Deseas continuar?', 'warning', 10000);
        }
    }

    pauseSession() {
        // Pausar el timer de sesión cuando la página no está visible
        this.sessionPaused = true;
    }

    resumeSession() {
        // Reanudar el timer de sesión
        this.sessionPaused = false;
        this.updateActivity();
    }

    // Métodos de UI
    updateUI() {
        this.updateNavbar();
        this.updatePageContent();
        this.updateLoginState();
    }

    updateNavbar() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        if (this.isAuthenticated()) {
            // Mostrar información del usuario
            const userInfo = navbar.querySelector('.user-info');
            if (userInfo) {
                userInfo.innerHTML = `
                    <span class="user-name">${this.currentUser.nombre}</span>
                    <button class="btn btn-secondary" onclick="securityManager.logout()">
                        <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                    </button>
                `;
            }
        } else {
            // Mostrar botón de login
            const userInfo = navbar.querySelector('.user-info');
            if (userInfo) {
                userInfo.innerHTML = `
                    <button class="btn btn-primary" onclick="showLoginModal()">
                        <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
                    </button>
                `;
            }
        }
    }

    updatePageContent() {
        // Mostrar/ocultar contenido basado en autenticación
        const protectedElements = document.querySelectorAll('[data-requires-auth]');
        protectedElements.forEach(element => {
            if (this.isAuthenticated()) {
                element.style.display = '';
            } else {
                element.style.display = 'none';
            }
        });

        const guestElements = document.querySelectorAll('[data-guest-only]');
        guestElements.forEach(element => {
            if (this.isAuthenticated()) {
                element.style.display = 'none';
            } else {
                element.style.display = '';
            }
        });
    }

    updateLoginState() {
        // Actualizar estado de login en componentes
        if (window.loginComponent) {
            window.loginComponent.updateState(this.isAuthenticated());
        }
        
        if (window.navbarComponent) {
            window.navbarComponent.updateState(this.isAuthenticated());
        }
    }

    // Métodos de navegación
    redirectToLogin() {
        // Redirigir a la página de login o mostrar modal
        if (window.showLoginModal) {
            window.showLoginModal();
        } else {
            window.location.href = '/login';
        }
    }

    redirectToHome() {
        window.location.href = '/';
    }

    // Métodos de API
    async makeAuthenticatedRequest(url, options = {}) {
        if (!this.isAuthenticated()) {
            throw new Error('Usuario no autenticado');
        }

        const defaultOptions = {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            }
        };

        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, mergedOptions);
            
            if (response.status === 401) {
                // Token expirado o inválido
                this.handleSessionTimeout();
                throw new Error('Sesión expirada');
            }
            
            return response;
        } catch (error) {
            if (error.message === 'Sesión expirada') {
                throw error;
            }
            
            console.error('Error en petición autenticada:', error);
            throw new Error('Error de conexión');
        }
    }

    // Métodos de notificación
    showNotification(message, type = 'info', duration = 5000) {
        if (window.Utils && window.Utils.showNotification) {
            window.Utils.showNotification(message, type, duration);
        } else {
            alert(message);
        }
    }

    // Métodos de validación de seguridad
    validateCSRFToken(token) {
        // Implementar validación CSRF si es necesario
        return true;
    }

    sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        
        // Sanitizar entrada para prevenir XSS
        return input
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;');
    }

    // Métodos de configuración
    setSessionTimeout(timeout) {
        this.sessionTimeout = timeout;
    }

    setAPIBaseURL(url) {
        window.API_BASE_URL = url;
    }

    // Métodos de utilidad
    formatUserDisplayName(user) {
        if (!user) return 'Usuario';
        
        if (user.nombre) {
            return user.nombre;
        } else if (user.email) {
            return user.email.split('@')[0];
        } else {
            return `Usuario ${user.id || 'Desconocido'}`;
        }
    }

    getUserAvatar(user) {
        if (user && user.avatar) {
            return user.avatar;
        }
        
        // Generar avatar basado en iniciales
        const name = this.formatUserDisplayName(user);
        const initials = name.split(' ').map(n => n[0]).join('').toUpperCase();
        
        return `https://ui-avatars.com/api/?name=${encodeURIComponent(initials)}&background=00B894&color=fff&size=40`;
    }
}

// Crear instancia global
window.SecurityManager = SecurityManager;
window.securityManager = new SecurityManager();

// Función global para mostrar modal de login
window.showLoginModal = function() {
    if (window.loginComponent) {
        window.loginComponent.showModal();
    }
};
