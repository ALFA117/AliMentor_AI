/**
 * AliMentor AI - Main Application
 * Configuración principal y inicialización de la aplicación
 */

// Configuración de la API
window.API_BASE_URL = window.location.origin; // Usar la misma URL del servidor actual

// Estado global de la aplicación
window.AppState = {
    currentUser: null,
    isAuthenticated: false,
    currentAnalysis: null,
    currentRun: 1
};

// Inicialización de la aplicación
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 AliMentor AI - Inicializando aplicación...');
    console.log('📡 API Base URL:', window.API_BASE_URL);
    
    // Inicializar componentes
    try {
        // Inicializar login
        if (window.LoginComponent) {
            window.loginComponent = new window.LoginComponent();
            console.log('✅ LoginComponent inicializado');
        }
        
        // Inicializar navbar
        if (window.NavbarComponent) {
            window.navbarComponent = new window.NavbarComponent();
            console.log('✅ NavbarComponent inicializado');
        }
        
        // Inicializar upload menu
        if (window.UploadMenuComponent) {
            window.uploadMenuComponent = new window.UploadMenuComponent();
            console.log('✅ UploadMenuComponent inicializado');
        }
        
        // Inicializar analysis result
        if (window.AnalysisResultComponent) {
            window.analysisResultComponent = new window.AnalysisResultComponent();
            console.log('✅ AnalysisResultComponent inicializado');
        }
        
        // Inicializar feedback form
        if (window.FeedbackFormComponent) {
            window.feedbackFormComponent = new window.FeedbackFormComponent();
            console.log('✅ FeedbackFormComponent inicializado');
        }
        
        // Inicializar metrics dashboard
        if (window.MetricsDashboardComponent) {
            window.metricsDashboardComponent = new window.MetricsDashboardComponent();
            console.log('✅ MetricsDashboardComponent inicializado');
        }
        
        // Inicializar profile
        if (window.ProfileComponent) {
            window.profileComponent = new window.ProfileComponent();
            console.log('✅ ProfileComponent inicializado');
        }
        
        // Inicializar user management
        if (window.UserManagementComponent) {
            window.userManagement = new window.UserManagementComponent();
            console.log('✅ UserManagementComponent inicializado');
        }
        
        // Inicializar JSON field handler
        if (window.JsonFieldHandler) {
            window.jsonFieldHandler = new window.JsonFieldHandler();
            console.log('✅ JsonFieldHandler inicializado');
        }
        
        // Inicializar user profile
        if (window.UserProfileComponent) {
            window.userProfile = new window.UserProfileComponent();
            console.log('✅ UserProfileComponent inicializado');
        }
        
        // Inicializar dishes listing
        if (window.DishesListingComponent) {
            window.dishesListing = new window.DishesListingComponent();
            console.log('✅ DishesListingComponent inicializado');
        }
        
        // Inicializar dish detail
        if (window.DishDetailComponent) {
            window.dishDetail = new window.DishDetailComponent();
            console.log('✅ DishDetailComponent inicializado');
        }
        
        // Inicializar feedback panel
        if (window.FeedbackPanelComponent) {
            window.feedbackPanel = new window.FeedbackPanelComponent();
            console.log('✅ FeedbackPanelComponent inicializado');
        }
        
        // Inicializar AI history view
        if (window.AIHistoryViewComponent) {
            window.aiHistoryView = new window.AIHistoryViewComponent();
            console.log('✅ AIHistoryViewComponent inicializado');
        }
        
        // Inicializar validation handler
        if (window.ValidationHandler) {
            window.validationHandler = new window.ValidationHandler();
            console.log('✅ ValidationHandler inicializado');
        }
        
        console.log('🎉 Todos los componentes inicializados correctamente');
        
    } catch (error) {
        console.error('❌ Error inicializando componentes:', error);
    }
});

// Funciones de utilidad globales
window.Utils = {
    // Mostrar notificación
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        // Mostrar notificación
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    },
    
    // Formatear fecha
    formatDate: function(date) {
        return new Date(date).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Validar email
    isValidEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
};

console.log('📚 AliMentor AI - Aplicación cargada correctamente');
