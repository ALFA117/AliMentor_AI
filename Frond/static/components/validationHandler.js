/**
 * Validation Handler Component
 * Maneja validaciones y manejo de errores en toda la aplicación
 */

class ValidationHandler {
    constructor() {
        this.rules = {};
        this.errors = {};
        this.init();
    }

    init() {
        this.setupDefaultRules();
        this.setupGlobalEventListeners();
    }

    setupDefaultRules() {
        this.rules = {
            required: (value) => {
                if (value === null || value === undefined || value === '') {
                    return 'Este campo es requerido';
                }
                return null;
            },
            
            email: (value) => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (value && !emailRegex.test(value)) {
                    return 'Ingresa un email válido';
                }
                return null;
            },
            
            minLength: (value, min) => {
                if (value && value.length < min) {
                    return `Mínimo ${min} caracteres requeridos`;
                }
                return null;
            },
            
            maxLength: (value, max) => {
                if (value && value.length > max) {
                    return `Máximo ${max} caracteres permitidos`;
                }
                return null;
            },
            
            min: (value, min) => {
                const num = parseFloat(value);
                if (!isNaN(num) && num < min) {
                    return `El valor mínimo es ${min}`;
                }
                return null;
            },
            
            max: (value, max) => {
                const num = parseFloat(value);
                if (!isNaN(num) && num > max) {
                    return `El valor máximo es ${max}`;
                }
                return null;
            },
            
            numeric: (value) => {
                if (value && isNaN(parseFloat(value))) {
                    return 'Solo se permiten números';
                }
                return null;
            },
            
            integer: (value) => {
                if (value && !Number.isInteger(parseFloat(value))) {
                    return 'Solo se permiten números enteros';
                }
                return null;
            },
            
            positive: (value) => {
                const num = parseFloat(value);
                if (!isNaN(num) && num <= 0) {
                    return 'El valor debe ser positivo';
                }
                return null;
            },
            
            range: (value, min, max) => {
                const num = parseFloat(value);
                if (!isNaN(num) && (num < min || num > max)) {
                    return `El valor debe estar entre ${min} y ${max}`;
                }
                return null;
            },
            
            pattern: (value, regex) => {
                if (value && !regex.test(value)) {
                    return 'El formato no es válido';
                }
                return null;
            },
            
            custom: (value, validator) => {
                if (typeof validator === 'function') {
                    return validator(value);
                }
                return null;
            }
        };
    }

    setupGlobalEventListeners() {
        // Event listener para validación en tiempo real
        document.addEventListener('blur', (e) => {
            if (e.target.hasAttribute('data-validate')) {
                this.validateField(e.target);
            }
        });

        // Event listener para limpiar errores al escribir
        document.addEventListener('input', (e) => {
            if (e.target.hasAttribute('data-validate')) {
                this.clearFieldError(e.target);
            }
        });
    }

    validateField(field) {
        const rules = this.getFieldRules(field);
        const value = this.getFieldValue(field);
        
        for (const rule of rules) {
            const error = this.applyRule(rule, value);
            if (error) {
                this.showFieldError(field, error);
                return false;
            }
        }
        
        this.clearFieldError(field);
        return true;
    }

    validateForm(form) {
        const fields = form.querySelectorAll('[data-validate]');
        let isValid = true;
        
        for (const field of fields) {
            if (!this.validateField(field)) {
                isValid = false;
            }
        }
        
        return isValid;
    }

    getFieldRules(field) {
        const rulesStr = field.getAttribute('data-validate');
        if (!rulesStr) return [];
        
        const rules = [];
        const ruleParts = rulesStr.split('|');
        
        for (const part of ruleParts) {
            const [ruleName, ...params] = part.split(':');
            rules.push({ name: ruleName, params });
        }
        
        return rules;
    }

    getFieldValue(field) {
        if (field.type === 'checkbox') {
            return field.checked;
        } else if (field.type === 'radio') {
            const checked = form.querySelector(`input[name="${field.name}"]:checked`);
            return checked ? checked.value : null;
        } else if (field.tagName === 'SELECT') {
            return field.value;
        } else {
            return field.value;
        }
    }

    applyRule(rule, value) {
        const validator = this.rules[rule.name];
        if (!validator) {
            console.warn(`Regla de validación no encontrada: ${rule.name}`);
            return null;
        }
        
        return validator(value, ...rule.params);
    }

    showFieldError(field, message) {
        this.clearFieldError(field);
        
        // Agregar clase de error
        field.classList.add('error');
        
        // Crear elemento de error
        const errorElement = document.createElement('div');
        errorElement.className = 'field-error';
        errorElement.textContent = message;
        
        // Insertar después del campo
        field.parentNode.insertBefore(errorElement, field.nextSibling);
        
        // Agregar a la lista de errores
        this.errors[field.name || field.id] = message;
    }

    clearFieldError(field) {
        field.classList.remove('error');
        
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
        
        delete this.errors[field.name || field.id];
    }

    clearAllErrors() {
        const errorFields = document.querySelectorAll('.error');
        errorFields.forEach(field => {
            field.classList.remove('error');
        });
        
        const errorElements = document.querySelectorAll('.field-error');
        errorElements.forEach(element => {
            element.remove();
        });
        
        this.errors = {};
    }

    showNotification(message, type = 'error', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `
            <div class="notification-content">
                <i class="${icon}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Agregar al DOM
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => {
            notification.classList.add('notification-show');
        }, 100);
        
        // Auto-remover
        setTimeout(() => {
            this.removeNotification(notification);
        }, duration);
        
        // Event listener para cerrar
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.removeNotification(notification);
        });
    }

    removeNotification(notification) {
        notification.classList.remove('notification-show');
        notification.classList.add('notification-hide');
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons['info'];
    }

    // Métodos de validación específicos
    validateEmail(email) {
        return this.rules.email(email);
    }

    validatePassword(password) {
        const errors = [];
        
        if (!password) {
            errors.push('La contraseña es requerida');
        } else {
            if (password.length < 8) {
                errors.push('Mínimo 8 caracteres');
            }
            if (!/[A-Z]/.test(password)) {
                errors.push('Al menos una mayúscula');
            }
            if (!/[a-z]/.test(password)) {
                errors.push('Al menos una minúscula');
            }
            if (!/\d/.test(password)) {
                errors.push('Al menos un número');
            }
        }
        
        return errors.length > 0 ? errors.join(', ') : null;
    }

    validatePhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (phone && !phoneRegex.test(phone.replace(/\s/g, ''))) {
            return 'Formato de teléfono inválido';
        }
        return null;
    }

    validateURL(url) {
        try {
            new URL(url);
            return null;
        } catch {
            return 'URL inválida';
        }
    }

    validateDate(date) {
        const dateObj = new Date(date);
        if (isNaN(dateObj.getTime())) {
            return 'Fecha inválida';
        }
        return null;
    }

    validateAge(age) {
        const num = parseInt(age);
        if (isNaN(num) || num < 1 || num > 120) {
            return 'La edad debe estar entre 1 y 120 años';
        }
        return null;
    }

    validateRating(rating) {
        const num = parseInt(rating);
        if (isNaN(num) || num < 1 || num > 5) {
            return 'La calificación debe estar entre 1 y 5';
        }
        return null;
    }

    validateConfidence(confidence) {
        const num = parseFloat(confidence);
        if (isNaN(num) || num < 0 || num > 1) {
            return 'La confianza debe estar entre 0 y 1';
        }
        return null;
    }

    // Método para validar campos JSON
    validateJsonArray(value, options = {}) {
        const {
            minItems = 0,
            maxItems = 100,
            maxLength = 100,
            required = false
        } = options;

        if (required && (!value || value.length === 0)) {
            return 'Este campo es requerido';
        }

        if (value && value.length < minItems) {
            return `Mínimo ${minItems} elementos requeridos`;
        }

        if (value && value.length > maxItems) {
            return `Máximo ${maxItems} elementos permitidos`;
        }

        if (value) {
            for (const item of value) {
                if (item.length > maxLength) {
                    return `Elemento demasiado largo (máx. ${maxLength} caracteres)`;
                }
                if (item.trim().length === 0) {
                    return 'Elementos vacíos no permitidos';
                }
            }
        }

        return null;
    }

    // Método para manejar errores de API
    handleApiError(error, context = '') {
        console.error(`Error en ${context}:`, error);
        
        let message = 'Ha ocurrido un error inesperado';
        
        if (error.response) {
            // Error de respuesta HTTP
            const status = error.response.status;
            const data = error.response.data;
            
            switch (status) {
                case 400:
                    message = data.error || 'Datos inválidos';
                    break;
                case 401:
                    message = 'No autorizado. Inicia sesión nuevamente';
                    break;
                case 403:
                    message = 'No tienes permisos para esta acción';
                    break;
                case 404:
                    message = 'Recurso no encontrado';
                    break;
                case 422:
                    message = data.error || 'Datos de validación inválidos';
                    break;
                case 500:
                    message = 'Error interno del servidor';
                    break;
                default:
                    message = data.error || `Error ${status}`;
            }
        } else if (error.request) {
            // Error de red
            message = 'Error de conexión. Verifica tu internet';
        } else {
            // Otros errores
            message = error.message || message;
        }
        
        this.showNotification(message, 'error');
        return message;
    }

    // Método para mostrar mensaje de éxito
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    // Método para mostrar mensaje de advertencia
    showWarning(message) {
        this.showNotification(message, 'warning');
    }

    // Método para mostrar mensaje informativo
    showInfo(message) {
        this.showNotification(message, 'info');
    }

    // Método para obtener todos los errores
    getErrors() {
        return this.errors;
    }

    // Método para verificar si hay errores
    hasErrors() {
        return Object.keys(this.errors).length > 0;
    }
}

// Crear instancia global
window.ValidationHandler = ValidationHandler;
window.Utils = {
    showNotification: (message, type) => {
        if (window.validationHandler) {
            window.validationHandler.showNotification(message, type);
        } else {
            alert(message);
        }
    }
};
