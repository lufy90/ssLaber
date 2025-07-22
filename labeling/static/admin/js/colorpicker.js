/**
 * Color Picker Enhancement for Django Admin
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize color pickers
    initializeColorPickers();
});

function initializeColorPickers() {
    const colorInputs = document.querySelectorAll('input[name*="color"]');
    
    colorInputs.forEach(function(input) {
        if (input.type === 'text' || input.type === 'color') {
            enhanceColorInput(input);
        }
    });
}

function enhanceColorInput(input) {
    // Skip if already enhanced
    if (input.classList.contains('color-enhanced')) {
        return;
    }
    
    input.classList.add('color-enhanced');
    
    // Create container
    const container = document.createElement('div');
    container.className = 'color-picker-container';
    
    // Create color input (HTML5 color picker)
    const colorPicker = document.createElement('input');
    colorPicker.type = 'color';
    colorPicker.className = 'color-picker';
    colorPicker.value = normalizeColorValue(input.value) || '#FF0000';
    
    // Create text input for hex value
    const textInput = document.createElement('input');
    textInput.type = 'text';
    textInput.className = 'color-text-input';
    textInput.value = normalizeColorValue(input.value) || '#FF0000';
    textInput.placeholder = '#RRGGBB';
    textInput.maxLength = 7;
    
    // Create color preset palette
    const presetContainer = createColorPresetPalette();
    
    // Hide original input
    input.style.display = 'none';
    
    // Insert enhanced picker after original input
    input.parentNode.insertBefore(container, input.nextSibling);
    container.appendChild(colorPicker);
    container.appendChild(textInput);
    container.appendChild(presetContainer);
    
    // Event listeners
    colorPicker.addEventListener('change', function() {
        const color = this.value.toUpperCase();
        textInput.value = color;
        input.value = color;
        updatePresetSelection(presetContainer, color);
    });
    
    textInput.addEventListener('input', function() {
        let color = this.value;
        if (isValidHexColor(color)) {
            colorPicker.value = color;
            input.value = color;
            updatePresetSelection(presetContainer, color);
        }
    });
    
    textInput.addEventListener('blur', function() {
        const color = normalizeColorValue(this.value);
        if (color) {
            this.value = color;
            colorPicker.value = color;
            input.value = color;
        }
    });
    
    // Initialize preset selection
    updatePresetSelection(presetContainer, colorPicker.value);
}

function createColorPresetPalette() {
    const presetColors = [
        '#FF0000', '#FF8800', '#FFFF00', '#88FF00', '#00FF00', '#00FF88',
        '#00FFFF', '#0088FF', '#0000FF', '#8800FF', '#FF00FF', '#FF0088',
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD',
        '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA',
        '#000000', '#404040', '#808080', '#C0C0C0', '#FFFFFF', '#8B4513'
    ];
    
    const container = document.createElement('div');
    container.className = 'color-preset-palette';
    
    presetColors.forEach(function(color) {
        const preset = document.createElement('div');
        preset.className = 'color-preset';
        preset.style.backgroundColor = color;
        preset.title = color;
        preset.dataset.color = color;
        
        preset.addEventListener('click', function() {
            const selectedColor = this.dataset.color;
            const parentContainer = this.closest('.color-picker-container');
            const colorPicker = parentContainer.querySelector('.color-picker');
            const textInput = parentContainer.querySelector('.color-text-input');
            const originalInput = parentContainer.parentNode.querySelector('input[name*="color"]:not(.color-enhanced)');
            
            colorPicker.value = selectedColor;
            textInput.value = selectedColor;
            originalInput.value = selectedColor;
            updatePresetSelection(container, selectedColor);
        });
        
        container.appendChild(preset);
    });
    
    return container;
}

function updatePresetSelection(presetContainer, selectedColor) {
    const presets = presetContainer.querySelectorAll('.color-preset');
    presets.forEach(function(preset) {
        preset.classList.remove('selected');
        if (preset.dataset.color.toUpperCase() === selectedColor.toUpperCase()) {
            preset.classList.add('selected');
        }
    });
}

function normalizeColorValue(value) {
    if (!value) return '#FF0000';
    
    // Remove any whitespace
    value = value.trim().toUpperCase();
    
    // Add # if missing
    if (!value.startsWith('#')) {
        value = '#' + value;
    }
    
    // Validate hex color
    if (isValidHexColor(value)) {
        return value;
    }
    
    return '#FF0000';
}

function isValidHexColor(color) {
    const hexColorRegex = /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/;
    return hexColorRegex.test(color);
}

// Handle dynamic forms (like inline formsets)
document.addEventListener('DOMNodeInserted', function(e) {
    if (e.target.nodeType === 1) {
        const colorInputs = e.target.querySelectorAll('input[name*="color"]');
        colorInputs.forEach(function(input) {
            if (!input.classList.contains('color-enhanced')) {
                enhanceColorInput(input);
            }
        });
    }
});

// For newer browsers, use MutationObserver
if (window.MutationObserver) {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    const colorInputs = node.querySelectorAll ? node.querySelectorAll('input[name*="color"]') : [];
                    colorInputs.forEach(function(input) {
                        if (!input.classList.contains('color-enhanced')) {
                            enhanceColorInput(input);
                        }
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}