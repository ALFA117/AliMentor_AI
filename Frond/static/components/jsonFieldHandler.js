/**
 * JSON Field Handler Component
 * Maneja la visualización y edición de campos JSON como chips/pills
 */

class JsonFieldHandler {
    constructor() {
        this.init();
    }

    init() {
        // Configurar event listeners globales
        this.setupGlobalEventListeners();
    }

    setupGlobalEventListeners() {
        // Event listener para agregar chips
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-chip-btn')) {
                this.addChip(e.target);
            }
            if (e.target.classList.contains('remove-chip')) {
                this.removeChip(e.target);
            }
        });

        // Event listener para input de chips
        document.addEventListener('keypress', (e) => {
            if (e.target.classList.contains('chip-input') && e.key === 'Enter') {
                e.preventDefault();
                this.addChipFromInput(e.target);
            }
        });
    }

    /**
     * Renderizar array JSON como chips
     */
    renderAsChips(data, containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const {
            editable = false,
            maxItems = 10,
            placeholder = 'Agregar elemento',
            color = 'primary',
            size = 'medium'
        } = options;

        if (!Array.isArray(data)) {
            data = [];
        }

        container.innerHTML = '';

        // Mostrar chips existentes
        data.forEach((item, index) => {
            const chip = this.createChip(item, index, editable, color, size);
            container.appendChild(chip);
        });

        // Agregar input para nuevos elementos si es editable
        if (editable && data.length < maxItems) {
            const inputContainer = this.createChipInput(placeholder, color, size);
            container.appendChild(inputContainer);
        }

        // Mostrar contador si hay muchos elementos
        if (data.length > maxItems) {
            const counter = document.createElement('div');
            counter.className = 'chip-counter';
            counter.textContent = `+${data.length - maxItems} más`;
            container.appendChild(counter);
        }
    }

    /**
     * Crear un chip individual
     */
    createChip(text, index, editable = false, color = 'primary', size = 'medium') {
        const chip = document.createElement('div');
        chip.className = `chip chip-${color} chip-${size}`;
        chip.dataset.index = index;

        chip.innerHTML = `
            <span class="chip-text">${text}</span>
            ${editable ? '<button class="remove-chip" type="button"><i class="fas fa-times"></i></button>' : ''}
        `;

        return chip;
    }

    /**
     * Crear input para agregar chips
     */
    createChipInput(placeholder, color, size) {
        const container = document.createElement('div');
        container.className = 'chip-input-container';

        container.innerHTML = `
            <input type="text" class="chip-input" placeholder="${placeholder}" maxlength="50">
            <button class="add-chip-btn" type="button">
                <i class="fas fa-plus"></i>
            </button>
        `;

        return container;
    }

    /**
     * Agregar chip desde botón
     */
    addChip(button) {
        const container = button.closest('.chip-input-container');
        const input = container.querySelector('.chip-input');
        const value = input.value.trim();

        if (value) {
            this.addChipFromInput(input);
        }
    }

    /**
     * Agregar chip desde input
     */
    addChipFromInput(input) {
        const value = input.value.trim();
        if (!value) return;

        const container = input.closest('.chips-container');
        const chipsContainer = container.querySelector('.chips-list') || container;
        
        // Crear nuevo chip
        const newChip = this.createChip(value, Date.now(), true, 'primary', 'medium');
        
        // Insertar antes del input
        const inputContainer = input.closest('.chip-input-container');
        chipsContainer.insertBefore(newChip, inputContainer);
        
        // Limpiar input
        input.value = '';
        
        // Actualizar datos
        this.updateChipsData(container);
    }

    /**
     * Remover chip
     */
    removeChip(button) {
        const chip = button.closest('.chip');
        const container = chip.closest('.chips-container');
        
        chip.remove();
        this.updateChipsData(container);
    }

    /**
     * Actualizar datos de chips
     */
    updateChipsData(container) {
        const chips = container.querySelectorAll('.chip:not(.chip-input-container)');
        const data = Array.from(chips).map(chip => 
            chip.querySelector('.chip-text').textContent
        );

        // Disparar evento personalizado
        const event = new CustomEvent('chipsUpdated', {
            detail: { data, container }
        });
        container.dispatchEvent(event);
    }

    /**
     * Obtener datos de chips
     */
    getChipsData(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return [];

        const chips = container.querySelectorAll('.chip:not(.chip-input-container)');
        return Array.from(chips).map(chip => 
            chip.querySelector('.chip-text').textContent
        );
    }

    /**
     * Renderizar campo JSON específico para ingredientes
     */
    renderIngredients(ingredients, containerId, editable = false) {
        this.renderAsChips(ingredients, containerId, {
            editable,
            placeholder: 'Agregar ingrediente',
            color: 'success',
            size: 'small'
        });
    }

    /**
     * Renderizar campo JSON específico para alérgenos
     */
    renderAllergens(allergens, containerId, editable = false) {
        this.renderAsChips(allergens, containerId, {
            editable,
            placeholder: 'Agregar alérgeno',
            color: 'warning',
            size: 'small'
        });
    }

    /**
     * Renderizar campo JSON específico para restricciones
     */
    renderRestrictions(restrictions, containerId, editable = false) {
        this.renderAsChips(restrictions, containerId, {
            editable,
            placeholder: 'Agregar restricción',
            color: 'info',
            size: 'small'
        });
    }

    /**
     * Renderizar campo JSON específico para enfermedades
     */
    renderDiseases(diseases, containerId, editable = false) {
        this.renderAsChips(diseases, containerId, {
            editable,
            placeholder: 'Agregar enfermedad',
            color: 'danger',
            size: 'small'
        });
    }

    /**
     * Validar datos de chips
     */
    validateChipsData(data, options = {}) {
        const {
            minItems = 0,
            maxItems = 50,
            maxLength = 100,
            required = false
        } = options;

        if (required && (!data || data.length === 0)) {
            return { valid: false, message: 'Este campo es requerido' };
        }

        if (data && data.length < minItems) {
            return { valid: false, message: `Mínimo ${minItems} elementos requeridos` };
        }

        if (data && data.length > maxItems) {
            return { valid: false, message: `Máximo ${maxItems} elementos permitidos` };
        }

        if (data) {
            for (const item of data) {
                if (item.length > maxLength) {
                    return { valid: false, message: `Elemento demasiado largo (máx. ${maxLength} caracteres)` };
                }
                if (item.trim().length === 0) {
                    return { valid: false, message: 'Elementos vacíos no permitidos' };
                }
            }
        }

        return { valid: true };
    }
}

// Exportar para uso global
window.JsonFieldHandler = JsonFieldHandler;
