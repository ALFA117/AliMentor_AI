/**
 * Navbar Component
 * Barra de navegación con información del usuario y logout
 */

class NavbarComponent {
    constructor() {
        this.navbarElement = null;
        this.userInfoElement = null;
        this.init();
    }

    init() {
        this.navbarElement = document.getElementById('navbar');
        this.userInfoElement = document.getElementById('user-info');
    }

    updateUserInfo(userData) {
        if (!this.userInfoElement) return;

        const { nombre, id_usuario } = userData;
        
        // Crear avatar con iniciales
        const initials = nombre.split(' ').map(n => n[0]).join('').toUpperCase();
        
        this.userInfoElement.innerHTML = `
            <div class="user-profile">
                <div class="user-avatar">
                    ${initials}
                </div>
                <div class="user-details">
                    <span class="user-name">${nombre}</span>
                    <span class="user-email">ID: ${id_usuario}</span>
                </div>
                <button id="logout-btn" class="btn btn-outline">
                    <i class="fas fa-sign-out-alt"></i> Cerrar Sesión
                </button>
            </div>
        `;

        // Configurar event listener para logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.handleLogout();
            });
        }
    }

    async handleLogout() {
        try {
            // Mostrar confirmación
            const confirmed = confirm('¿Estás seguro de que quieres cerrar sesión?');
            if (!confirmed) return;

            // Llamar al componente de login para hacer logout
            if (window.LoginComponent) {
                const loginComponent = new window.LoginComponent();
                await loginComponent.logout();
            } else {
                // Fallback: limpiar localStorage y recargar
                localStorage.removeItem('userData');
                location.reload();
            }
        } catch (error) {
            console.error('Error en logout:', error);
            alert('Error al cerrar sesión. Por favor, intenta de nuevo.');
        }
    }

    // Método para mostrar/ocultar navbar
    show() {
        if (this.navbarElement) {
            this.navbarElement.style.display = 'block';
        }
    }

    hide() {
        if (this.navbarElement) {
            this.navbarElement.style.display = 'none';
        }
    }

    // Método para actualizar el estado de autenticación
    updateAuthState(isAuthenticated, userData = null) {
        if (isAuthenticated && userData) {
            this.updateUserInfo(userData);
            this.show();
        } else {
            this.hide();
        }
    }

    // Método para obtener información del usuario actual
    getCurrentUserInfo() {
        const userData = localStorage.getItem('userData');
        return userData ? JSON.parse(userData) : null;
    }
}

// Exportar para uso global
window.NavbarComponent = NavbarComponent;

