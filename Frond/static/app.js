/* ========================================
   AliMentor AI - Main Application JavaScript
   ======================================== */

// Global Configuration
const API_BASE_URL = 'http://127.0.0.1:5000';
let currentUser = null;
let currentView = 'login';

// Initialize Application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check if user is already logged in
    const savedUser = localStorage.getItem('alimentor_user');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showDashboard();
    } else {
        showLogin();
    }
    
    // Initialize event listeners
    
    // Initialize simulation system
    initializeSimulation();
    initializeEventListeners();
    
    // Initialize chef bot
    initializeChefBot();
}

function initializeEventListeners() {
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // User config form
    const userConfigForm = document.getElementById('user-config-form');
    if (userConfigForm) {
        userConfigForm.addEventListener('submit', handleUserConfigSave);
    }
    
    // Chip inputs
    initializeChipInputs();
    
    // Table search
    initializeTableSearch();
}

function initializeChefBot() {
    const chefBot = document.getElementById('chef-bot');
    if (chefBot) {
        chefBot.addEventListener('click', function() {
            showNotification('¡Hola! Soy tu asistente culinario. ¿En qué puedo ayudarte?', 'info');
        });
    }
}

// ========================================
// VIEW MANAGEMENT
// ========================================

function showLogin() {
    hideAllViews();
    document.getElementById('login-view').style.display = 'flex';
    currentView = 'login';
}

function showDashboard() {
    hideAllViews();
    document.getElementById('dashboard-view').style.display = 'block';
    currentView = 'dashboard';
    
    if (currentUser) {
        updateUserInfo();
        loadDashboardData();
    }
}

function showUserPanel() {
    hideAllViews();
    document.getElementById('user-panel-view').style.display = 'block';
    currentView = 'user-panel';
    
    if (currentUser) {
        loadUserPanelData();
    }
}

function showDishes() {
    hideAllViews();
    document.getElementById('dishes-view').style.display = 'block';
    currentView = 'dishes';
    
    loadDishes();
}

function hideAllViews() {
    const views = ['login-view', 'dashboard-view', 'user-panel-view', 'dishes-view'];
    views.forEach(viewId => {
        const view = document.getElementById(viewId);
        if (view) {
            view.style.display = 'none';
        }
    });
}

// ========================================
// LOGIN FUNCTIONALITY - COMPLETE SYSTEM
// ========================================

// Login validation rules
const LOGIN_VALIDATION = {
    username: {
        minLength: 2,
        maxLength: 50,
        pattern: /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/,
        required: true
    },
    password: {
        minLength: 0, // Optional
        maxLength: 100,
        required: false
    }
};

// Enhanced login form validation
function validateLoginForm(formData) {
    const errors = {};
    const username = formData.get('username')?.trim();
    const password = formData.get('password')?.trim();
    
    // Username validation
    if (!username) {
        errors.username = 'El nombre de usuario es requerido';
    } else if (username.length < LOGIN_VALIDATION.username.minLength) {
        errors.username = `El nombre debe tener al menos ${LOGIN_VALIDATION.username.minLength} caracteres`;
    } else if (username.length > LOGIN_VALIDATION.username.maxLength) {
        errors.username = `El nombre no puede exceder ${LOGIN_VALIDATION.username.maxLength} caracteres`;
    } else if (!LOGIN_VALIDATION.username.pattern.test(username)) {
        errors.username = 'El nombre solo puede contener letras y espacios';
    }
    
    // Password validation (optional but if provided, must meet criteria)
    if (password && password.length > 0) {
        if (password.length < 3) {
            errors.password = 'La contraseña debe tener al menos 3 caracteres';
        } else if (password.length > LOGIN_VALIDATION.password.maxLength) {
            errors.password = `La contraseña no puede exceder ${LOGIN_VALIDATION.password.maxLength} caracteres`;
        }
    }
    
    return {
        isValid: Object.keys(errors).length === 0,
        errors: errors
    };
}

// Show form validation errors
function showFormErrors(errors) {
    // Clear previous errors
    document.querySelectorAll('.form-error').forEach(error => error.remove());
    document.querySelectorAll('.form-group input').forEach(input => {
        input.classList.remove('error');
    });
    
    // Show new errors
    Object.keys(errors).forEach(field => {
        const input = document.getElementById(field === 'username' ? 'username' : 'password');
        if (input) {
            input.classList.add('error');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.textContent = errors[field];
            errorDiv.style.cssText = `
                color: var(--coral-red);
                font-size: 0.8rem;
                margin-top: 0.25rem;
                animation: slideInUp 0.3s ease-out;
            `;
            
            input.parentNode.appendChild(errorDiv);
        }
    });
}

// Enhanced login with comprehensive validation
async function handleLogin(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const username = formData.get('username')?.trim();
    const password = formData.get('password')?.trim();
    
    // Validate form
    const validation = validateLoginForm(formData);
    if (!validation.isValid) {
        showFormErrors(validation.errors);
        return;
    }
    
    // Show loading state
    const submitBtn = event.target.querySelector('.login-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Iniciando sesión...';
    submitBtn.disabled = true;
    
    try {
        showNotification('🔐 Verificando credenciales...', 'info');
        
        // Simulate network delay for better UX
        await new Promise(resolve => setTimeout(resolve, 800));
        
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password || 'default'
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Error en el servidor');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Store user data with additional metadata
            currentUser = {
                ...data.user,
                loginTime: new Date().toISOString(),
                sessionId: generateSessionId(),
                preferences: {
                    theme: 'light',
                    notifications: true,
                    language: 'es'
                }
            };
            
            localStorage.setItem('alimentor_user', JSON.stringify(currentUser));
            localStorage.setItem('alimentor_session', currentUser.sessionId);
            
            // Show success animation
            showLoginSuccessAnimation();
            showNotification(`¡Bienvenido, ${currentUser.nombre}! 🎉`, 'success');
            
            // Track login event
            trackUserEvent('login', {
                userId: currentUser.id_usuario,
                username: currentUser.nombre,
                timestamp: new Date().toISOString()
            });
            
            // Animate transition to dashboard
            setTimeout(() => {
                showDashboard();
            }, 1500);
        } else {
            throw new Error(data.message || 'Error en el login');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        showNotification('❌ Error al iniciar sesión: ' + error.message, 'error');
        
        // Show error animation
        showLoginErrorAnimation();
    } finally {
        // Restore button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Generate unique session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Login success animation
function showLoginSuccessAnimation() {
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        loginCard.style.animation = 'bounce 0.6s ease-out';
        
        // Add success glow effect
        loginCard.style.boxShadow = `
            var(--glass-shadow-strong),
            0 0 0 1px rgba(255, 255, 255, 0.2),
            0 0 30px rgba(0, 200, 150, 0.4)
        `;
        
        setTimeout(() => {
            loginCard.style.animation = '';
            loginCard.style.boxShadow = '';
        }, 600);
    }
}

// Login error animation
function showLoginErrorAnimation() {
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        loginCard.style.animation = 'shake 0.5s ease-in-out';
        
        // Add error glow effect
        loginCard.style.boxShadow = `
            var(--glass-shadow-strong),
            0 0 0 1px rgba(255, 255, 255, 0.2),
            0 0 30px rgba(255, 118, 117, 0.4)
        `;
        
        setTimeout(() => {
            loginCard.style.animation = '';
            loginCard.style.boxShadow = '';
        }, 500);
    }
}

// User event tracking
function trackUserEvent(eventType, data) {
    const event = {
        type: eventType,
        data: data,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
    };
    
    // Store in localStorage for analytics
    const events = JSON.parse(localStorage.getItem('alimentor_events') || '[]');
    events.push(event);
    localStorage.setItem('alimentor_events', JSON.stringify(events.slice(-100))); // Keep last 100 events
}

function logout() {
    currentUser = null;
    localStorage.removeItem('alimentor_user');
    showNotification('Sesión cerrada correctamente', 'info');
    showLogin();
}

// ========================================
// USER CONFIGURATION - COMPLETE PROFILE MANAGEMENT
// ========================================

// Profile validation rules
const PROFILE_VALIDATION = {
    nombre: {
        minLength: 2,
        maxLength: 50,
        pattern: /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/,
        required: true
    },
    edad: {
        min: 1,
        max: 120,
        required: true
    },
    genero: {
        options: ['Masculino', 'Femenino', 'No especificado'],
        required: true
    },
    restricciones: {
        maxItems: 10,
        maxLength: 30
    },
    alergias: {
        maxItems: 15,
        maxLength: 30
    },
    enfermedades: {
        maxItems: 10,
        maxLength: 50
    }
};

// Enhanced user configuration with comprehensive validation
function showUserConfig() {
    const modal = document.getElementById('user-config-modal');
    if (modal) {
        modal.style.display = 'flex';
        loadUserConfigData();
        initializeProfileValidation();
        
        // Track profile view
        trackUserEvent('profile_config_view', {
            userId: currentUser.id_usuario,
            timestamp: new Date().toISOString()
        });
    }
}

function closeUserConfig() {
    const modal = document.getElementById('user-config-modal');
    if (modal) {
        // Check for unsaved changes
        if (hasUnsavedChanges()) {
            showUnsavedChangesDialog();
            return;
        }
        
        modal.style.display = 'none';
        clearFormValidation();
    }
}

function hasUnsavedChanges() {
    const form = document.getElementById('user-config-form');
    if (!form) return false;
    
    const formData = new FormData(form);
    const currentData = {
        nombre: formData.get('nombre'),
        edad: formData.get('edad'),
        genero: formData.get('genero'),
        restricciones: getChips('restrictions-container'),
        alergias: getChips('allergies-container'),
        enfermedades: getChips('diseases-container')
    };
    
    const originalData = {
        nombre: currentUser.nombre,
        edad: currentUser.edad,
        genero: currentUser.genero,
        restricciones: currentUser.restricciones || [],
        alergias: currentUser.alergias || [],
        enfermedades: currentUser.enfermedades || []
    };
    
    return JSON.stringify(currentData) !== JSON.stringify(originalData);
}

function showUnsavedChangesDialog() {
    const dialog = document.createElement('div');
    dialog.className = 'unsaved-changes-dialog';
    dialog.innerHTML = `
        <div class="dialog-content">
            <div class="dialog-header">
                <h3>⚠️ Cambios sin guardar</h3>
            </div>
            <div class="dialog-body">
                <p>Tienes cambios sin guardar. ¿Estás seguro de que quieres cerrar sin guardar?</p>
            </div>
            <div class="dialog-actions">
                <button class="btn btn-secondary" onclick="this.closest('.unsaved-changes-dialog').remove()">
                    Cancelar
                </button>
                <button class="btn btn-primary" onclick="closeUserConfigForce()">
                    Cerrar sin guardar
                </button>
            </div>
        </div>
    `;
    
    dialog.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(5px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
        animation: modalFadeIn 0.3s ease-out;
    `;
    
    document.body.appendChild(dialog);
}

function closeUserConfigForce() {
    const modal = document.getElementById('user-config-modal');
    const dialog = document.querySelector('.unsaved-changes-dialog');
    
    if (modal) modal.style.display = 'none';
    if (dialog) dialog.remove();
    
    clearFormValidation();
}

function loadUserConfigData() {
    if (!currentUser) return;
    
    // Load user data into form with validation
    const nameInput = document.getElementById('config-name');
    const ageInput = document.getElementById('config-age');
    const genderSelect = document.getElementById('config-gender');
    
    if (nameInput) nameInput.value = currentUser.nombre || '';
    if (ageInput) ageInput.value = currentUser.edad || '';
    if (genderSelect) genderSelect.value = currentUser.genero || 'No especificado';
    
    // Load restrictions, allergies, and diseases with enhanced display
    loadChips('restrictions-container', currentUser.restricciones || []);
    loadChips('allergies-container', currentUser.alergias || []);
    loadChips('diseases-container', currentUser.enfermedades || []);
    
    // Add profile completion indicator
    updateProfileCompletionIndicator();
}

function initializeProfileValidation() {
    const form = document.getElementById('user-config-form');
    if (!form) return;
    
    // Add real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
    
    // Add chip validation
    const chipContainers = ['restrictions-container', 'allergies-container', 'diseases-container'];
    chipContainers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            const input = container.querySelector('.chip-input');
            if (input) {
                input.addEventListener('input', validateChipInput);
            }
        }
    });
}

function validateField(event) {
    const field = event.target;
    const fieldName = field.name;
    const value = field.value.trim();
    
    let error = '';
    
    switch (fieldName) {
        case 'nombre':
            if (!value) {
                error = 'El nombre es requerido';
            } else if (value.length < PROFILE_VALIDATION.nombre.minLength) {
                error = `El nombre debe tener al menos ${PROFILE_VALIDATION.nombre.minLength} caracteres`;
            } else if (value.length > PROFILE_VALIDATION.nombre.maxLength) {
                error = `El nombre no puede exceder ${PROFILE_VALIDATION.nombre.maxLength} caracteres`;
            } else if (!PROFILE_VALIDATION.nombre.pattern.test(value)) {
                error = 'El nombre solo puede contener letras y espacios';
            }
            break;
            
        case 'edad':
            const age = parseInt(value);
            if (!value) {
                error = 'La edad es requerida';
            } else if (isNaN(age)) {
                error = 'La edad debe ser un número válido';
            } else if (age < PROFILE_VALIDATION.edad.min) {
                error = `La edad debe ser al menos ${PROFILE_VALIDATION.edad.min} años`;
            } else if (age > PROFILE_VALIDATION.edad.max) {
                error = `La edad no puede exceder ${PROFILE_VALIDATION.edad.max} años`;
            }
            break;
            
        case 'genero':
            if (!value || !PROFILE_VALIDATION.genero.options.includes(value)) {
                error = 'Selecciona un género válido';
            }
            break;
    }
    
    if (error) {
        showFieldError(field, error);
    } else {
        clearFieldError(event);
    }
    
    return !error;
}

function validateChipInput(event) {
    const input = event.target;
    const value = input.value.trim();
    const containerId = input.closest('.chips-container').id;
    const container = document.getElementById(containerId);
    
    // Check max items
    const currentChips = container.querySelectorAll('.chip');
    const maxItems = PROFILE_VALIDATION[containerId.replace('-container', '')].maxItems;
    
    if (currentChips.length >= maxItems) {
        input.placeholder = `Máximo ${maxItems} elementos`;
        input.disabled = true;
        setTimeout(() => {
            input.disabled = false;
            input.placeholder = `Agregar ${containerId.replace('-container', '').slice(0, -1)}...`;
        }, 2000);
        return;
    }
    
    // Check max length
    const maxLength = PROFILE_VALIDATION[containerId.replace('-container', '')].maxLength;
    if (value.length > maxLength) {
        input.value = value.substring(0, maxLength);
        showFieldError(input, `Máximo ${maxLength} caracteres`);
    }
}

function showFieldError(field, error) {
    clearFieldError({ target: field });
    
    field.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = error;
    errorDiv.style.cssText = `
        color: var(--coral-red);
        font-size: 0.8rem;
        margin-top: 0.25rem;
        animation: slideInUp 0.3s ease-out;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    `;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(event) {
    const field = event.target;
    field.classList.remove('error');
    
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function clearFormValidation() {
    document.querySelectorAll('.field-error').forEach(error => error.remove());
    document.querySelectorAll('.form-group input, .form-group select').forEach(field => {
        field.classList.remove('error');
    });
}

function updateProfileCompletionIndicator() {
    const completionData = calculateProfileCompletion();
    
    // Create or update completion indicator
    let indicator = document.getElementById('profile-completion');
    if (!indicator) {
        const modalHeader = document.querySelector('.modal-header');
        if (modalHeader) {
            indicator = document.createElement('div');
            indicator.id = 'profile-completion';
            indicator.className = 'profile-completion-indicator';
            modalHeader.appendChild(indicator);
        }
    }
    
    if (indicator) {
        indicator.innerHTML = `
            <div class="completion-bar">
                <div class="completion-fill" style="width: ${completionData.percentage}%"></div>
            </div>
            <span class="completion-text">Perfil ${completionData.percentage}% completo</span>
        `;
    }
}

function calculateProfileCompletion() {
    if (!currentUser) return { percentage: 0, missing: [] };
    
    const fields = [
        { key: 'nombre', weight: 20, value: currentUser.nombre },
        { key: 'edad', weight: 15, value: currentUser.edad },
        { key: 'genero', weight: 10, value: currentUser.genero },
        { key: 'restricciones', weight: 15, value: currentUser.restricciones?.length || 0 },
        { key: 'alergias', weight: 20, value: currentUser.alergias?.length || 0 },
        { key: 'enfermedades', weight: 20, value: currentUser.enfermedades?.length || 0 }
    ];
    
    let completed = 0;
    const missing = [];
    
    fields.forEach(field => {
        if (field.value && field.value !== 'No especificado') {
            completed += field.weight;
        } else {
            missing.push(field.key);
        }
    });
    
    return {
        percentage: Math.min(completed, 100),
        missing: missing
    };
}

async function handleUserConfigSave(event) {
    event.preventDefault();
    
    if (!currentUser) return;
    
    const formData = new FormData(event.target);
    
    const userData = {
        nombre: formData.get('nombre'),
        edad: parseInt(formData.get('edad')),
        genero: formData.get('genero'),
        restricciones: getChips('restrictions-container'),
        alergias: getChips('allergies-container'),
        enfermedades: getChips('diseases-container')
    };
    
    try {
        showNotification('Guardando cambios...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/usuarios/${currentUser.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        if (!response.ok) {
            throw new Error('Error al guardar cambios');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update current user data
            currentUser = { ...currentUser, ...userData };
            localStorage.setItem('alimentor_user', JSON.stringify(currentUser));
            
            // Show success animation
            showSuccessAnimation();
            showNotification('✅ Perfil actualizado correctamente', 'success');
            closeUserConfig();
            
            // Refresh user panel if visible
            if (currentView === 'user-panel') {
                loadUserPanelData();
            }
        } else {
            throw new Error(data.message || 'Error al guardar cambios');
        }
        
    } catch (error) {
        console.error('Save error:', error);
        showNotification('Error al guardar cambios: ' + error.message, 'error');
    }
}

// ========================================
// CHIP SYSTEM
// ========================================

function initializeChipInputs() {
    const chipContainers = ['restrictions-container', 'allergies-container', 'diseases-container'];
    
    chipContainers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            const input = container.querySelector('.chip-input');
            if (input) {
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        addChip(containerId, this.value.trim());
                        this.value = '';
                    }
                });
                
                input.addEventListener('blur', function() {
                    if (this.value.trim()) {
                        addChip(containerId, this.value.trim());
                        this.value = '';
                    }
                });
            }
        }
    });
}

function addChip(containerId, value) {
    if (!value) return;
    
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Check if chip already exists
    const existingChips = container.querySelectorAll('.chip');
    for (let chip of existingChips) {
        if (chip.textContent.trim() === value) {
            return;
        }
    }
    
    const chip = document.createElement('div');
    chip.className = 'chip';
    chip.innerHTML = `
        <span>${value}</span>
        <button class="chip-remove" onclick="removeChip(this)">×</button>
    `;
    
    const input = container.querySelector('.chip-input');
    container.insertBefore(chip, input);
}

function removeChip(button) {
    const chip = button.parentElement;
    chip.remove();
}

function loadChips(containerId, chips) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Clear existing chips
    const existingChips = container.querySelectorAll('.chip');
    existingChips.forEach(chip => chip.remove());
    
    // Add new chips
    chips.forEach(chip => {
        addChip(containerId, chip);
    });
}

function getChips(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    
    const chips = container.querySelectorAll('.chip');
    return Array.from(chips).map(chip => {
        return chip.querySelector('span').textContent.trim();
    });
}

// ========================================
// DASHBOARD DATA LOADING - COMPLETE ANALYTICS
// ========================================

// Dashboard analytics configuration
const DASHBOARD_CONFIG = {
    refreshInterval: 30000, // 30 seconds
    maxRetries: 3,
    cacheTimeout: 60000, // 1 minute
    animationDelay: 100 // ms between card animations
};

// Dashboard data cache
let dashboardCache = {
    data: null,
    timestamp: null,
    loading: false
};

// Enhanced dashboard data loading with caching and analytics
async function loadDashboardData() {
    if (!currentUser) return;
    
    // Check cache first
    if (dashboardCache.data && 
        dashboardCache.timestamp && 
        (Date.now() - dashboardCache.timestamp) < DASHBOARD_CONFIG.cacheTimeout) {
        renderDashboardData(dashboardCache.data);
        return;
    }
    
    if (dashboardCache.loading) return;
    dashboardCache.loading = true;
    
    try {
        showDashboardLoadingState();
        
        // Load all dashboard data in parallel
        const [
            recentDishes,
            recentFeedback,
            recentAIActions,
            metricsSummary,
            userStats,
            nutritionInsights,
            recommendations
        ] = await Promise.allSettled([
            loadRecentDishes(),
            loadRecentFeedback(),
            loadRecentAIActions(),
            loadMetricsSummary(),
            loadUserStats(),
            loadNutritionInsights(),
            loadPersonalizedRecommendations()
        ]);
        
        // Compile dashboard data
        const dashboardData = {
            recentDishes: recentDishes.status === 'fulfilled' ? recentDishes.value : null,
            recentFeedback: recentFeedback.status === 'fulfilled' ? recentFeedback.value : null,
            recentAIActions: recentAIActions.status === 'fulfilled' ? recentAIActions.value : null,
            metricsSummary: metricsSummary.status === 'fulfilled' ? metricsSummary.value : null,
            userStats: userStats.status === 'fulfilled' ? userStats.value : null,
            nutritionInsights: nutritionInsights.status === 'fulfilled' ? nutritionInsights.value : null,
            recommendations: recommendations.status === 'fulfilled' ? recommendations.value : null,
            lastUpdated: new Date().toISOString()
        };
        
        // Cache the data
        dashboardCache.data = dashboardData;
        dashboardCache.timestamp = Date.now();
        
        // Render with animations
        renderDashboardData(dashboardData);
        
        // Track dashboard view
        trackUserEvent('dashboard_view', {
            userId: currentUser.id_usuario,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error al cargar datos del dashboard', 'error');
    } finally {
        dashboardCache.loading = false;
        hideDashboardLoadingState();
    }
}

// Show loading state for dashboard
function showDashboardLoadingState() {
    const cards = document.querySelectorAll('.dashboard-card, .quick-action-card');
    cards.forEach(card => {
        card.style.opacity = '0.6';
        card.style.pointerEvents = 'none';
    });
    
    // Show loading overlay
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'dashboard-loading';
    loadingOverlay.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <p>Cargando datos...</p>
        </div>
    `;
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
    `;
    document.body.appendChild(loadingOverlay);
}

// Hide loading state
function hideDashboardLoadingState() {
    const loadingOverlay = document.getElementById('dashboard-loading');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
    
    const cards = document.querySelectorAll('.dashboard-card, .quick-action-card');
    cards.forEach(card => {
        card.style.opacity = '1';
        card.style.pointerEvents = 'auto';
    });
}

// Render dashboard data with animations
function renderDashboardData(data) {
    // Animate cards in sequence
    const cards = document.querySelectorAll('.dashboard-card, .quick-action-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.animation = `slideInUp 0.6s ease-out both`;
        }, index * DASHBOARD_CONFIG.animationDelay);
    });
    
    // Update each section
    if (data.recentDishes) updateRecentDishes(data.recentDishes);
    if (data.recentFeedback) updateRecentFeedback(data.recentFeedback);
    if (data.recentAIActions) updateRecentAIActions(data.recentAIActions);
    if (data.metricsSummary) updateMetricsSummary(data.metricsSummary);
    if (data.userStats) updateUserStats(data.userStats);
    if (data.nutritionInsights) updateNutritionInsights(data.nutritionInsights);
    if (data.recommendations) updateRecommendations(data.recommendations);
}

// Load user statistics
async function loadUserStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/usuarios/${currentUser.id_usuario}/stats`);
        if (!response.ok) {
            // Fallback to mock data
            return {
                totalDishesAnalyzed: 15,
                averageRating: 4.2,
                favoriteCategory: 'Ensaladas',
                healthScore: 85,
                weeklyProgress: {
                    monday: 80,
                    tuesday: 90,
                    wednesday: 75,
                    thursday: 95,
                    friday: 88,
                    saturday: 70,
                    sunday: 85
                }
            };
        }
        return await response.json();
    } catch (error) {
        console.error('Error loading user stats:', error);
        return null;
    }
}

// Load nutrition insights
async function loadNutritionInsights() {
    try {
        // Mock nutrition insights based on user data
        const insights = {
            dailyCalories: 1850,
            proteinIntake: 65,
            carbIntake: 45,
            fatIntake: 30,
            fiberIntake: 25,
            vitaminC: 120,
            iron: 18,
            calcium: 800,
            recommendations: [
                'Aumenta tu consumo de fibra con más vegetales',
                'Considera agregar más proteína magra',
                'Tu ingesta de vitamina C está excelente'
            ],
            warnings: [
                'Nivel de sodio ligeramente alto',
                'Consumo de agua por debajo de lo recomendado'
            ]
        };
        return insights;
    } catch (error) {
        console.error('Error loading nutrition insights:', error);
        return null;
    }
}

// Load personalized recommendations
async function loadPersonalizedRecommendations() {
    try {
        const recommendations = {
            dishes: [
                {
                    name: 'Ensalada de Quinoa',
                    reason: 'Perfecta para tu dieta sin gluten',
                    rating: 4.8,
                    calories: 320
                },
                {
                    name: 'Salmón a la Plancha',
                    reason: 'Alto en omega-3, ideal para tu salud cardiovascular',
                    rating: 4.6,
                    calories: 280
                }
            ],
            tips: [
                'Bebe al menos 8 vasos de agua al día',
                'Incluye 5 porciones de frutas y verduras',
                'Evita alimentos procesados con alto contenido de sodio'
            ],
            goals: [
                'Mantener un peso saludable',
                'Controlar la diabetes tipo 2',
                'Mejorar la salud cardiovascular'
            ]
        };
        return recommendations;
    } catch (error) {
        console.error('Error loading recommendations:', error);
        return null;
    }
}

// Update functions for dashboard sections
function updateRecentDishes(dishes) {
    const container = document.getElementById('recent-dishes');
    if (!container) return;
    
    if (dishes && dishes.length > 0) {
        container.innerHTML = dishes.map((plato, index) => `
            <div class="dish-item" style="animation-delay: ${index * 0.1}s">
                <div class="dish-icon">${getDishIcon(plato.nombre)}</div>
                <div class="dish-info">
                    <h4>${plato.nombre}</h4>
                    <p>${plato.categoria}</p>
                    <div class="dish-meta">
                        <span class="calories">${plato.calorias || 'N/A'} cal</span>
                        <span class="rating">${plato.rating || 'N/A'} ⭐</span>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-utensils"></i><p>No hay platos recientes</p></div>';
    }
}

function updateRecentFeedback(feedbacks) {
    const container = document.getElementById('recent-feedback');
    if (!container) return;
    
    if (feedbacks && feedbacks.length > 0) {
        container.innerHTML = feedbacks.map((feedback, index) => `
            <div class="feedback-item" style="animation-delay: ${index * 0.1}s">
                <div class="feedback-rating">
                    ${'★'.repeat(feedback.calificacion)}${'☆'.repeat(5 - feedback.calificacion)}
                </div>
                <div class="feedback-info">
                    <h4>${feedback.plato_nombre || 'Plato'}</h4>
                    <p>${feedback.comentario || 'Sin comentario'}</p>
                    <div class="feedback-meta">
                        <span class="date">${formatDate(feedback.fecha_creacion)}</span>
                        <span class="type">${feedback.tipo || 'General'}</span>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-comment"></i><p>No hay feedback reciente</p></div>';
    }
}

function updateRecentAIActions(actions) {
    const container = document.getElementById('recent-ai-actions');
    if (!container) return;
    
    if (actions && actions.length > 0) {
        container.innerHTML = actions.map((accion, index) => `
            <div class="ai-action-item" style="animation-delay: ${index * 0.1}s">
                <div class="action-type">${getActionTypeIcon(accion.tipo)}</div>
                <div class="action-info">
                    <h4>${accion.tipo}</h4>
                    <p>${accion.plato_nombre || 'Plato'}</p>
                    <div class="action-meta">
                        <span class="status ${accion.estado}">${accion.estado}</span>
                        <span class="date">${formatDate(accion.fecha_creacion)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-robot"></i><p>No hay acciones IA recientes</p></div>';
    }
}

function updateMetricsSummary(metrics) {
    const container = document.getElementById('metrics-summary');
    if (!container) return;
    
    if (metrics) {
        container.innerHTML = `
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-value">${metrics.total_platos || 0}</div>
                    <div class="metric-label">Platos</div>
                    <div class="metric-trend ${metrics.platos_trend > 0 ? 'up' : 'down'}">
                        <i class="fas fa-arrow-${metrics.platos_trend > 0 ? 'up' : 'down'}"></i>
                        ${Math.abs(metrics.platos_trend || 0)}%
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.total_feedbacks || 0}</div>
                    <div class="metric-label">Feedbacks</div>
                    <div class="metric-trend ${metrics.feedback_trend > 0 ? 'up' : 'down'}">
                        <i class="fas fa-arrow-${metrics.feedback_trend > 0 ? 'up' : 'down'}"></i>
                        ${Math.abs(metrics.feedback_trend || 0)}%
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-value">${metrics.promedio_calificacion || 0}</div>
                    <div class="metric-label">Calificación</div>
                    <div class="metric-trend ${metrics.rating_trend > 0 ? 'up' : 'down'}">
                        <i class="fas fa-arrow-${metrics.rating_trend > 0 ? 'up' : 'down'}"></i>
                        ${Math.abs(metrics.rating_trend || 0)}%
                    </div>
                </div>
            </div>
        `;
    } else {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-chart-pie"></i><p>No hay métricas disponibles</p></div>';
    }
}

function updateUserStats(stats) {
    // Create or update user stats section
    let statsContainer = document.getElementById('user-stats');
    if (!statsContainer) {
        // Create stats section if it doesn't exist
        const dashboardGrid = document.querySelector('.dashboard-grid');
        if (dashboardGrid) {
            const statsCard = document.createElement('div');
            statsCard.className = 'dashboard-card';
            statsCard.innerHTML = `
                <div class="card-header">
                    <h3><i class="fas fa-user-chart"></i> Mis Estadísticas</h3>
                </div>
                <div class="card-content" id="user-stats">
                    <div class="loading">Cargando estadísticas...</div>
                </div>
            `;
            dashboardGrid.appendChild(statsCard);
            statsContainer = document.getElementById('user-stats');
        }
    }
    
    if (statsContainer && stats) {
        statsContainer.innerHTML = `
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-icon">🍽️</div>
                    <div class="stat-value">${stats.totalDishesAnalyzed}</div>
                    <div class="stat-label">Platos Analizados</div>
                </div>
                <div class="stat-item">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-value">${stats.averageRating}</div>
                    <div class="stat-label">Calificación Promedio</div>
                </div>
                <div class="stat-item">
                    <div class="stat-icon">❤️</div>
                    <div class="stat-value">${stats.healthScore}%</div>
                    <div class="stat-label">Puntuación de Salud</div>
                </div>
                <div class="stat-item">
                    <div class="stat-icon">🏆</div>
                    <div class="stat-value">${stats.favoriteCategory}</div>
                    <div class="stat-label">Categoría Favorita</div>
                </div>
            </div>
            <div class="weekly-progress">
                <h4>Progreso Semanal</h4>
                <div class="progress-bars">
                    ${Object.entries(stats.weeklyProgress).map(([day, value]) => `
                        <div class="progress-item">
                            <span class="day">${day.charAt(0).toUpperCase() + day.slice(1)}</span>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${value}%"></div>
                            </div>
                            <span class="value">${value}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

function updateNutritionInsights(insights) {
    // Create or update nutrition insights section
    let insightsContainer = document.getElementById('nutrition-insights');
    if (!insightsContainer) {
        const dashboardGrid = document.querySelector('.dashboard-grid');
        if (dashboardGrid) {
            const insightsCard = document.createElement('div');
            insightsCard.className = 'dashboard-card';
            insightsCard.innerHTML = `
                <div class="card-header">
                    <h3><i class="fas fa-heartbeat"></i> Insights Nutricionales</h3>
                </div>
                <div class="card-content" id="nutrition-insights">
                    <div class="loading">Cargando insights...</div>
                </div>
            `;
            dashboardGrid.appendChild(insightsCard);
            insightsContainer = document.getElementById('nutrition-insights');
        }
    }
    
    if (insightsContainer && insights) {
        insightsContainer.innerHTML = `
            <div class="nutrition-overview">
                <div class="macro-nutrients">
                    <div class="macro-item">
                        <div class="macro-label">Calorías</div>
                        <div class="macro-value">${insights.dailyCalories}</div>
                        <div class="macro-bar">
                            <div class="macro-fill" style="width: ${(insights.dailyCalories / 2000) * 100}%"></div>
                        </div>
                    </div>
                    <div class="macro-item">
                        <div class="macro-label">Proteína</div>
                        <div class="macro-value">${insights.proteinIntake}g</div>
                        <div class="macro-bar">
                            <div class="macro-fill" style="width: ${(insights.proteinIntake / 100) * 100}%"></div>
                        </div>
                    </div>
                    <div class="macro-item">
                        <div class="macro-label">Carbohidratos</div>
                        <div class="macro-value">${insights.carbIntake}g</div>
                        <div class="macro-bar">
                            <div class="macro-fill" style="width: ${(insights.carbIntake / 100) * 100}%"></div>
                        </div>
                    </div>
                </div>
                <div class="recommendations">
                    <h4>Recomendaciones</h4>
                    <ul>
                        ${insights.recommendations.map(rec => `<li>✅ ${rec}</li>`).join('')}
                    </ul>
                </div>
                ${insights.warnings.length > 0 ? `
                    <div class="warnings">
                        <h4>Advertencias</h4>
                        <ul>
                            ${insights.warnings.map(warning => `<li>⚠️ ${warning}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }
}

function updateRecommendations(recommendations) {
    // Create or update recommendations section
    let recContainer = document.getElementById('recommendations');
    if (!recContainer) {
        const dashboardGrid = document.querySelector('.dashboard-grid');
        if (dashboardGrid) {
            const recCard = document.createElement('div');
            recCard.className = 'dashboard-card';
            recCard.innerHTML = `
                <div class="card-header">
                    <h3><i class="fas fa-lightbulb"></i> Recomendaciones Personalizadas</h3>
                </div>
                <div class="card-content" id="recommendations">
                    <div class="loading">Cargando recomendaciones...</div>
                </div>
            `;
            dashboardGrid.appendChild(recCard);
            recContainer = document.getElementById('recommendations');
        }
    }
    
    if (recContainer && recommendations) {
        recContainer.innerHTML = `
            <div class="recommendations-content">
                <div class="recommended-dishes">
                    <h4>Platos Recomendados</h4>
                    ${recommendations.dishes.map(dish => `
                        <div class="recommended-dish">
                            <div class="dish-info">
                                <h5>${dish.name}</h5>
                                <p>${dish.reason}</p>
                            </div>
                            <div class="dish-meta">
                                <span class="rating">${dish.rating} ⭐</span>
                                <span class="calories">${dish.calories} cal</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="tips-goals">
                    <div class="tips">
                        <h4>Consejos de Salud</h4>
                        <ul>
                            ${recommendations.tips.map(tip => `<li>💡 ${tip}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="goals">
                        <h4>Tus Objetivos</h4>
                        <ul>
                            ${recommendations.goals.map(goal => `<li>🎯 ${goal}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }
}

async function loadRecentDishes() {
    try {
        const response = await fetch(`${API_BASE_URL}/platos?limit=3`);
        const data = await response.json();
        
        if (data.platos && data.platos.length > 0) {
            return data.platos;
        }
        return [];
    } catch (error) {
        console.error('Error loading recent dishes:', error);
        return [];
    }
}

async function loadRecentFeedback() {
    try {
        const response = await fetch(`${API_BASE_URL}/feedback?limit=3`);
        const data = await response.json();
        
        const container = document.getElementById('recent-feedback');
        if (container) {
            if (data.feedbacks && data.feedbacks.length > 0) {
                container.innerHTML = data.feedbacks.map(feedback => `
                    <div class="feedback-item">
                        <div class="feedback-rating">
                            ${'★'.repeat(feedback.calificacion)}${'☆'.repeat(5 - feedback.calificacion)}
                        </div>
                        <div class="feedback-info">
                            <h4>${feedback.plato_nombre || 'Plato'}</h4>
                            <p>${feedback.comentario || 'Sin comentario'}</p>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p>No hay feedback reciente</p>';
            }
        }
    } catch (error) {
        console.error('Error loading recent feedback:', error);
    }
}

async function loadRecentAIActions() {
    try {
        const response = await fetch(`${API_BASE_URL}/acciones_ia?limit=3`);
        const data = await response.json();
        
        const container = document.getElementById('recent-ai-actions');
        if (container) {
            if (data.acciones && data.acciones.length > 0) {
                container.innerHTML = data.acciones.map(accion => `
                    <div class="ai-action-item">
                        <div class="action-type">${getActionTypeIcon(accion.tipo)}</div>
                        <div class="action-info">
                            <h4>${accion.tipo}</h4>
                            <p>${accion.plato_nombre || 'Plato'}</p>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p>No hay acciones IA recientes</p>';
            }
        }
    } catch (error) {
        console.error('Error loading recent AI actions:', error);
    }
}

async function loadMetricsSummary() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics`);
        const data = await response.json();
        
        const container = document.getElementById('metrics-summary');
        if (container) {
            if (data.metrics) {
                container.innerHTML = `
                    <div class="metrics-grid">
                        <div class="metric-item">
                            <div class="metric-value">${data.metrics.total_platos || 0}</div>
                            <div class="metric-label">Platos</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${data.metrics.total_feedbacks || 0}</div>
                            <div class="metric-label">Feedbacks</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">${data.metrics.promedio_calificacion || 0}</div>
                            <div class="metric-label">Calificación</div>
                        </div>
                    </div>
                `;
            } else {
                container.innerHTML = '<p>No hay métricas disponibles</p>';
            }
        }
    } catch (error) {
        console.error('Error loading metrics summary:', error);
    }
}

// ========================================
// USER PANEL DATA LOADING
// ========================================

async function loadUserPanelData() {
    if (!currentUser) return;
    
    try {
        // Load profile data
        loadProfileData();
        
        // Load feedback data
        await loadFeedbackTable();
        
        // Load AI actions data
        await loadAIActionsTable();
        
    } catch (error) {
        console.error('Error loading user panel data:', error);
    }
}

function loadProfileData() {
    if (!currentUser) return;
    
    // Update profile info
    document.getElementById('profile-name').textContent = currentUser.nombre || 'Usuario';
    document.getElementById('profile-age-gender').textContent = 
        `${currentUser.edad || 'N/A'} años • ${currentUser.genero || 'No especificado'}`;
    
    // Load chips
    loadChips('profile-restrictions', currentUser.restricciones || []);
    loadChips('profile-allergies', currentUser.alergias || []);
    loadChips('profile-diseases', currentUser.enfermedades || []);
}

async function loadFeedbackTable() {
    try {
        const response = await fetch(`${API_BASE_URL}/feedback`);
        const data = await response.json();
        
        const tbody = document.getElementById('feedback-table-body');
        if (tbody) {
            if (data.feedbacks && data.feedbacks.length > 0) {
                tbody.innerHTML = data.feedbacks.map(feedback => `
                    <tr>
                        <td>${feedback.plato_nombre || 'N/A'}</td>
                        <td>
                            <div class="rating-stars">
                                ${'★'.repeat(feedback.calificacion)}${'☆'.repeat(5 - feedback.calificacion)}
                            </div>
                        </td>
                        <td>${feedback.tipo || 'N/A'}</td>
                        <td>${feedback.comentario || 'Sin comentario'}</td>
                        <td>${formatDate(feedback.fecha_creacion)}</td>
                        <td>
                            <button class="btn btn-sm" onclick="viewDish(${feedback.plato_id})">
                                <i class="fas fa-eye"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="6">No hay feedback disponible</td></tr>';
            }
        }
    } catch (error) {
        console.error('Error loading feedback table:', error);
    }
}

async function loadAIActionsTable() {
    try {
        const response = await fetch(`${API_BASE_URL}/acciones_ia`);
        const data = await response.json();
        
        const tbody = document.getElementById('ai-actions-table-body');
        if (tbody) {
            if (data.acciones && data.acciones.length > 0) {
                tbody.innerHTML = data.acciones.map(accion => `
                    <tr>
                        <td>
                            <span class="action-type-badge">${getActionTypeIcon(accion.tipo)} ${accion.tipo}</span>
                        </td>
                        <td>${accion.plato_nombre || 'N/A'}</td>
                        <td>${accion.prompt || 'N/A'}</td>
                        <td>${accion.resultado || 'N/A'}</td>
                        <td>
                            <span class="status-badge ${accion.estado}">${accion.estado}</span>
                        </td>
                        <td>${formatDate(accion.fecha_creacion)}</td>
                    </tr>
                `).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="6">No hay acciones IA disponibles</td></tr>';
            }
        }
    } catch (error) {
        console.error('Error loading AI actions table:', error);
    }
}

// ========================================
// DISHES MANAGEMENT
// ========================================

async function loadDishes() {
    try {
        const response = await fetch(`${API_BASE_URL}/platos`);
        const data = await response.json();
        
        const container = document.getElementById('dishes-grid');
        if (container) {
            if (data.platos && data.platos.length > 0) {
                container.innerHTML = data.platos.map((plato, index) => `
                    <div class="dish-card" onclick="viewDish(${plato.id})" style="animation-delay: ${index * 0.1}s">
                        <div class="dish-header">
                            <div class="dish-icon">${getDishIcon(plato.nombre)}</div>
                            <div class="dish-info">
                                <h3>${plato.nombre}</h3>
                                <p>${plato.categoria}</p>
                            </div>
                        </div>
                        <div class="dish-details">
                            <p><strong>Ingredientes:</strong> ${plato.ingredientes || 'N/A'}</p>
                            <p><strong>Alérgenos:</strong> ${plato.alergenos || 'Ninguno'}</p>
                            <p><strong>Calorías:</strong> ${plato.calorias || 'N/A'}</p>
                        </div>
                        <button class="dish-feedback-btn" onclick="event.stopPropagation(); showFeedbackModal(${plato.id})">
                            <i class="fas fa-star"></i> Dar Feedback
                        </button>
                    </div>
                `).join('');
                
                // Add staggered animation to cards
                const cards = container.querySelectorAll('.dish-card');
                cards.forEach((card, index) => {
                    card.style.animation = `slideInUp 0.6s ease-out ${index * 0.1}s both`;
                });
            } else {
                container.innerHTML = '<div class="loading">No hay platos disponibles</div>';
            }
        }
    } catch (error) {
        console.error('Error loading dishes:', error);
    }
}

// ========================================
// TAB MANAGEMENT
// ========================================

function showTab(tabId) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    // Show selected tab content
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

// ========================================
// TABLE SEARCH
// ========================================

function initializeTableSearch() {
    const searchInputs = document.querySelectorAll('.data-table-search');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.data-table-container').querySelector('.data-table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

function updateUserInfo() {
    if (!currentUser) return;
    
    const userNameElements = document.querySelectorAll('#user-name, #dashboard-user-name');
    userNameElements.forEach(element => {
        element.textContent = currentUser.nombre || 'Usuario';
    });
}

function getDishIcon(dishName) {
    const name = dishName.toLowerCase();
    if (name.includes('ensalada') || name.includes('salad')) return '🥗';
    if (name.includes('pizza') || name.includes('pasta')) return '🍝';
    if (name.includes('carne') || name.includes('meat')) return '🥩';
    if (name.includes('pescado') || name.includes('fish')) return '🐟';
    if (name.includes('postre') || name.includes('dessert')) return '🍰';
    if (name.includes('sopa') || name.includes('soup')) return '🍲';
    if (name.includes('arroz') || name.includes('rice')) return '🍚';
    if (name.includes('pollo') || name.includes('chicken')) return '🍗';
    return '🍽️';
}

function getActionTypeIcon(type) {
    switch (type) {
        case 'analisis': return '🔍';
        case 'recomendacion': return '💡';
        case 'mejora': return '⚡';
        default: return '🤖';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
}

function viewDish(dishId) {
    showNotification(`Viendo plato ID: ${dishId}`, 'info');
    // TODO: Implement dish detail view
}

// ========================================
// NOTIFICATION SYSTEM
// ========================================

function showNotification(message, type = 'info') {
    const container = document.getElementById('notification-container');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icon = getNotificationIcon(type);
    
    notification.innerHTML = `
        <div class="notification-header">
            <div class="notification-title">
                <i class="fas fa-${icon}"></i>
                ${getNotificationTitle(type)}
            </div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
        <div class="notification-message">${message}</div>
    `;
    
    container.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function getNotificationTitle(type) {
    switch (type) {
        case 'success': return 'Éxito';
        case 'error': return 'Error';
        case 'warning': return 'Advertencia';
        default: return 'Información';
    }
}

// ========================================
// QUICK ACTIONS
// ========================================

function showMenuAnalysis() {
    showNotification('Función de análisis de menú en desarrollo', 'info');
}

function showMetrics() {
    showNotification('Función de métricas en desarrollo', 'info');
}

// ========================================
// GLOBAL FUNCTIONS (for HTML onclick)
// ========================================

window.showDashboard = showDashboard;
window.showUserPanel = showUserPanel;
window.showDishes = showDishes;
window.showUserConfig = showUserConfig;
window.closeUserConfig = closeUserConfig;
window.logout = logout;
window.showTab = showTab;
window.viewDish = viewDish;
window.showMenuAnalysis = showMenuAnalysis;
window.showMetrics = showMetrics;
window.removeChip = removeChip;
window.showFeedbackModal = showFeedbackModal;

// ========================================
// VISUAL FEEDBACK AND ANIMATIONS
// ========================================

function showSuccessAnimation() {
    // Create success animation element
    const successEl = document.createElement('div');
    successEl.className = 'success-animation';
    successEl.innerHTML = `
        <div class="success-check">
            <i class="fas fa-check"></i>
        </div>
        <div class="success-particles">
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
        </div>
    `;
    
    // Add styles
    successEl.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 3000;
        pointer-events: none;
    `;
    
    document.body.appendChild(successEl);
    
    // Remove after animation
    setTimeout(() => {
        successEl.remove();
    }, 2000);
}

function showFeedbackModal(dishId) {
    showNotification(`Modal de feedback para plato ID: ${dishId} - En desarrollo`, 'info');
    // TODO: Implement feedback modal
}

// ========================================
// ENHANCED ANIMATIONS
// ========================================

function addStaggeredAnimation(container, selector, animation = 'slideInUp') {
    const elements = container.querySelectorAll(selector);
    elements.forEach((element, index) => {
        element.style.animation = `${animation} 0.6s ease-out ${index * 0.1}s both`;
    });
}

function addHoverEffects() {
    // Add hover effects to all interactive elements
    const interactiveElements = document.querySelectorAll('.btn, .card, .dish-card, .quick-action-card');
    
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        element.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Initialize enhanced animations when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    addHoverEffects();
});

// ========================================
// SIMULATION SYSTEM - COMPLETE FLOW
// ========================================

// Simulation configuration
const SIMULATION_CONFIG = {
    enabled: true,
    demoUser: {
        username: 'Demo',
        password: '12345',
        id: 3
    },
    steps: [
        { id: 'login', name: 'Inicio de Sesión', duration: 2000 },
        { id: 'dashboard', name: 'Dashboard Principal', duration: 3000 },
        { id: 'profile', name: 'Perfil de Usuario', duration: 2500 },
        { id: 'feedback', name: 'Sistema de Feedback', duration: 2000 },
        { id: 'metrics', name: 'Métricas y Analytics', duration: 2000 },
        { id: 'completion', name: 'Simulación Completada', duration: 1500 }
    ]
};

// Simulation state
let simulationState = {
    currentStep: 0,
    isRunning: false,
    startTime: null
};

// Initialize simulation system
function initializeSimulation() {
    // Add simulation controls to login page
    addSimulationControls();
    
    // Add demo credentials hint
    addDemoCredentialsHint();
    
    // Initialize simulation event listeners
    setupSimulationEventListeners();
}

// Add simulation controls
function addSimulationControls() {
    const loginCard = document.querySelector('.login-card');
    if (loginCard) {
        const simulationControls = document.createElement('div');
        simulationControls.className = 'simulation-controls';
        simulationControls.innerHTML = `
            <div class="simulation-header">
                <h4>🎭 Modo Demostración</h4>
                <p>Prueba el flujo completo con datos simulados</p>
            </div>
            <div class="demo-credentials">
                <div class="credential-item">
                    <span class="label">Usuario:</span>
                    <span class="value">Demo</span>
                </div>
                <div class="credential-item">
                    <span class="label">Contraseña:</span>
                    <span class="value">12345</span>
                </div>
            </div>
            <button class="btn btn-simulation" onclick="startCompleteSimulation()">
                <i class="fas fa-play"></i> Iniciar Simulación Completa
            </button>
        `;
        loginCard.appendChild(simulationControls);
    }
}

// Add demo credentials hint
function addDemoCredentialsHint() {
    const loginForm = document.querySelector('#login-form');
    if (loginForm) {
        const hint = document.createElement('div');
        hint.className = 'demo-hint';
        hint.innerHTML = `
            <div class="hint-content">
                <i class="fas fa-info-circle"></i>
                <span>Para la demostración, usa: <strong>Demo</strong> / <strong>12345</strong></span>
            </div>
        `;
        loginForm.appendChild(hint);
    }
}

// Setup simulation event listeners
function setupSimulationEventListeners() {
    // Auto-fill demo credentials when typing
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    if (usernameInput && passwordInput) {
        usernameInput.addEventListener('input', function() {
            if (this.value.toLowerCase() === 'demo') {
                passwordInput.value = '12345';
                showNotification('🔑 Credenciales de demostración cargadas', 'info');
            }
        });
    }
}

// Start complete simulation flow
async function startCompleteSimulation() {
    if (simulationState.isRunning) return;
    
    simulationState.isRunning = true;
    simulationState.startTime = Date.now();
    simulationState.currentStep = 0;
    
    showNotification('🎭 Iniciando simulación completa...', 'info');
    
    try {
        // Step 1: Login
        await executeSimulationStep('login');
        
        // Step 2: Dashboard
        await executeSimulationStep('dashboard');
        
        // Step 3: Profile
        await executeSimulationStep('profile');
        
        // Step 4: Feedback
        await executeSimulationStep('feedback');
        
        // Step 5: Metrics
        await executeSimulationStep('metrics');
        
        // Step 6: Completion
        await executeSimulationStep('completion');
        
    } catch (error) {
        console.error('Simulation error:', error);
        showNotification('❌ Error en la simulación', 'error');
    } finally {
        simulationState.isRunning = false;
    }
}

// Execute individual simulation step
async function executeSimulationStep(stepId) {
    const step = SIMULATION_CONFIG.steps.find(s => s.id === stepId);
    if (!step) return;
    
    simulationState.currentStep++;
    
    // Show step progress
    showSimulationProgress(step);
    
    switch (stepId) {
        case 'login':
            await simulateLogin();
            break;
        case 'dashboard':
            await simulateDashboard();
            break;
        case 'profile':
            await simulateProfile();
            break;
        case 'feedback':
            await simulateFeedback();
            break;
        case 'metrics':
            await simulateMetrics();
            break;
        case 'completion':
            await simulateCompletion();
            break;
    }
    
    // Wait for step duration
    await new Promise(resolve => setTimeout(resolve, step.duration));
}

// Show simulation progress
function showSimulationProgress(step) {
    const progress = (simulationState.currentStep / SIMULATION_CONFIG.steps.length) * 100;
    
    showNotification(`🎭 Paso ${simulationState.currentStep}/${SIMULATION_CONFIG.steps.length}: ${step.name}`, 'info');
    
    // Update progress bar if exists
    let progressBar = document.getElementById('simulation-progress');
    if (!progressBar) {
        progressBar = document.createElement('div');
        progressBar.id = 'simulation-progress';
        progressBar.className = 'simulation-progress-bar';
        document.body.appendChild(progressBar);
    }
    
    progressBar.innerHTML = `
        <div class="progress-content">
            <div class="progress-info">
                <span class="step-name">${step.name}</span>
                <span class="step-progress">${simulationState.currentStep}/${SIMULATION_CONFIG.steps.length}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress}%"></div>
            </div>
        </div>
    `;
}

// Simulate login process
async function simulateLogin() {
    // Auto-fill credentials
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    if (usernameInput && passwordInput) {
        // Animate typing
        await typeText(usernameInput, SIMULATION_CONFIG.demoUser.username);
        await new Promise(resolve => setTimeout(resolve, 500));
        await typeText(passwordInput, SIMULATION_CONFIG.demoUser.password);
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Submit form
        const form = document.getElementById('login-form');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
}

// Simulate dashboard interaction
async function simulateDashboard() {
    // Wait for dashboard to load
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simulate clicking on dish cards
    const dishCards = document.querySelectorAll('.dish-card');
    if (dishCards.length > 0) {
        const randomCard = dishCards[Math.floor(Math.random() * dishCards.length)];
        randomCard.style.animation = 'pulse 0.5s ease-in-out';
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    // Simulate quick actions
    const quickActions = document.querySelectorAll('.quick-action-card');
    quickActions.forEach((action, index) => {
        setTimeout(() => {
            action.style.animation = 'bounce 0.6s ease-out';
        }, index * 200);
    });
}

// Simulate profile interaction
async function simulateProfile() {
    // Open profile modal
    const profileBtn = document.querySelector('[onclick="showUserConfig()"]');
    if (profileBtn) {
        profileBtn.click();
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simulate profile viewing
        const modal = document.getElementById('user-config-modal');
        if (modal) {
            modal.style.animation = 'modalSlideUp 0.5s ease-out';
        }
        
        // Simulate closing modal
        await new Promise(resolve => setTimeout(resolve, 1500));
        const closeBtn = modal.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.click();
        }
    }
}

// Simulate feedback interaction
async function simulateFeedback() {
    // Find feedback button and simulate click
    const feedbackBtn = document.querySelector('.dish-feedback-btn');
    if (feedbackBtn) {
        feedbackBtn.click();
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simulate feedback form interaction
        const feedbackModal = document.querySelector('.feedback-modal');
        if (feedbackModal) {
            // Simulate rating selection
            const stars = feedbackModal.querySelectorAll('.star');
            if (stars.length > 0) {
                stars[3].click(); // Select 4 stars
                await new Promise(resolve => setTimeout(resolve, 500));
            }
            
            // Simulate comment
            const commentInput = feedbackModal.querySelector('textarea');
            if (commentInput) {
                await typeText(commentInput, 'Muy sabroso, pero contiene lactosa');
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
            // Close modal
            const closeBtn = feedbackModal.querySelector('.close-btn');
            if (closeBtn) {
                closeBtn.click();
            }
        }
    }
}

// Simulate metrics interaction
async function simulateMetrics() {
    // Open metrics view
    const metricsBtn = document.querySelector('[onclick*="metrics"]');
    if (metricsBtn) {
        metricsBtn.click();
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Simulate metrics viewing
        const metricsCards = document.querySelectorAll('.metric-item');
        metricsCards.forEach((card, index) => {
            setTimeout(() => {
                card.style.animation = 'slideInUp 0.6s ease-out';
            }, index * 200);
        });
    }
}

// Simulate completion
async function simulateCompletion() {
    // Show completion animation
    showSimulationCompletion();
    
    // Remove progress bar
    const progressBar = document.getElementById('simulation-progress');
    if (progressBar) {
        setTimeout(() => {
            progressBar.remove();
        }, 2000);
    }
}

// Show simulation completion
function showSimulationCompletion() {
    const completionTime = Date.now() - simulationState.startTime;
    const duration = Math.round(completionTime / 1000);
    
    const completionModal = document.createElement('div');
    completionModal.className = 'simulation-completion-modal';
    completionModal.innerHTML = `
        <div class="completion-content">
            <div class="completion-animation">
                <div class="success-check">✅</div>
                <div class="completion-particles">
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                    <div class="particle"></div>
                </div>
            </div>
            <h2>🎉 ¡Simulación Completada!</h2>
            <p>✅ Usuario <strong>Demo</strong> ha navegado por todo el sistema</p>
            <div class="completion-stats">
                <div class="stat">
                    <span class="stat-value">${duration}s</span>
                    <span class="stat-label">Duración</span>
                </div>
                <div class="stat">
                    <span class="stat-value">${SIMULATION_CONFIG.steps.length}</span>
                    <span class="stat-label">Pasos</span>
                </div>
                <div class="stat">
                    <span class="stat-value">100%</span>
                    <span class="stat-label">Completado</span>
                </div>
            </div>
            <div class="completion-features">
                <h3>Funcionalidades Probadas:</h3>
                <ul>
                    <li>✅ Sistema de Login con validación</li>
                    <li>✅ Dashboard con analytics completos</li>
                    <li>✅ Gestión de perfil de usuario</li>
                    <li>✅ Sistema de feedback interactivo</li>
                    <li>✅ Métricas y visualizaciones</li>
                    <li>✅ Animaciones y transiciones</li>
                </ul>
            </div>
            <button class="btn btn-primary" onclick="this.closest('.simulation-completion-modal').remove()">
                <i class="fas fa-check"></i> Continuar
            </button>
        </div>
    `;
    
    document.body.appendChild(completionModal);
    
    // Animate completion
    setTimeout(() => {
        completionModal.style.opacity = '1';
        completionModal.style.transform = 'scale(1)';
    }, 100);
}

// Type text animation
async function typeText(element, text) {
    element.value = '';
    for (let i = 0; i < text.length; i++) {
        element.value += text[i];
        await new Promise(resolve => setTimeout(resolve, 50));
    }
}
