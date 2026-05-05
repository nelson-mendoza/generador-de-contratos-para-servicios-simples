/* 
 * ContratoUniversal - Lógica JavaScript
 * Maneja interacciones del formulario y validaciones frontend
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== ELEMENTOS DEL DOM =====
    const contractForm = document.getElementById('contractForm');
    const generateBtn = document.getElementById('generateBtn');
    const formErrors = document.getElementById('form-errors');
    
    // Elementos condicionales
    const hasMaterialsCheckbox = document.getElementById('has_materials');
    const materialsContainer = document.getElementById('materials-container');
    
    const paymentStructureSelect = document.getElementById('payment_structure');
    const advanceFields = document.getElementById('advance-fields');
    
    const paymentMethodSelect = document.getElementById('payment_method');
    const bankFields = document.getElementById('bank-fields');
    
    const paymentTimingSelect = document.getElementById('payment_timing');
    const penaltyCheckbox = document.getElementById('apply_penalty');
    const penaltyFields = document.getElementById('penalty-fields');
    const penaltyHint = document.getElementById('penalty-hint');
    
    const advancedToggle = document.getElementById('advanced-toggle');
    const advancedOptions = document.getElementById('advanced-options');
    
    const includeSignaturesCheckbox = document.getElementById('include_signatures');
    const signatureNames = document.getElementById('signature-names');
    
    const logoInput = document.getElementById('logo');
    const filePreview = document.getElementById('file-preview');
    
    // ===== INICIALIZACIÓN =====
    initEventListeners();
    setMinDate();
    
    // ===== EVENT LISTENERS =====
    function initEventListeners() {
        // Toggle materiales
        hasMaterialsCheckbox.addEventListener('change', toggleMaterials);
        
        // Toggle campos de anticipo
        paymentStructureSelect.addEventListener('change', toggleAdvanceFields);
        
        // Toggle campos bancarios
        paymentMethodSelect.addEventListener('change', toggleBankFields);
        
        // Toggle penalizaciones según timing
        paymentTimingSelect.addEventListener('change', togglePenaltyAvailability);
        penaltyCheckbox.addEventListener('change', togglePenaltyFields);
        
        // Toggle opciones avanzadas
        advancedToggle.addEventListener('click', toggleAdvancedOptions);
        
        // Toggle nombres de firmas
        includeSignaturesCheckbox.addEventListener('change', toggleSignatureNames);
        
        // Preview de logo
        logoInput.addEventListener('change', handleLogoPreview);
        
        // Submit del formulario
        contractForm.addEventListener('submit', handleSubmit);
        
        // Validación en tiempo real
        setupRealTimeValidation();
    }
    
    // ===== FUNCIONES DE TOGGLE =====
    
    // Mostrar/ocultar campo de materiales
    function toggleMaterials() {
        if (hasMaterialsCheckbox.checked) {
            materialsContainer.classList.remove('hidden');
        } else {
            materialsContainer.classList.add('hidden');
        }
    }
    
    // Mostrar/ocultar campos de anticipo
    function toggleAdvanceFields() {
        if (paymentStructureSelect.value === 'advance') {
            advanceFields.classList.remove('hidden');
            // Calcular automáticamente si el total cambia
            calculateRemaining();
        } else {
            advanceFields.classList.add('hidden');
        }
    }
    
    // Calcular resto automáticamente
    function calculateRemaining() {
        const total = parseFloat(document.getElementById('total_amount').value) || 0;
        const advance = parseFloat(document.getElementById('advance_amount').value) || 0;
        const remainingField = document.getElementById('remaining_amount');
        
        if (paymentStructureSelect.value === 'advance' && total > 0) {
            remainingField.value = (total - advance).toFixed(2);
        }
    }
    
    // Agregar listener al total para recalcular
    document.getElementById('total_amount').addEventListener('input', calculateRemaining);
    document.getElementById('advance_amount').addEventListener('input', calculateRemaining);
    
    // Mostrar/ocultar campos bancarios
    function toggleBankFields() {
        if (paymentMethodSelect.value === 'transfer') {
            bankFields.classList.remove('hidden');
        } else {
            bankFields.classList.add('hidden');
        }
    }
    
    // Habilitar/deshabilitar penalizaciones según timing
    function togglePenaltyAvailability() {
        const isAfter = paymentTimingSelect.value === 'after';
        
        if (!isAfter) {
            // Deshabilitar visualmente
            penaltyCheckbox.checked = false;
            penaltyCheckbox.disabled = true;
            penaltyFields.classList.add('hidden');
            penaltyHint.style.color = '#ff9800';
            penaltyHint.textContent = '⚠️ Las penalizaciones solo aplican cuando el pago es DESPUÉS del servicio';
        } else {
            penaltyCheckbox.disabled = false;
            penaltyHint.style.color = 'var(--text-secondary)';
            penaltyHint.textContent = 'Las penalizaciones solo aplican para pagos posteriores al servicio';
        }
    }
    
    // Mostrar/ocultar campos de penalización
    function togglePenaltyFields() {
        if (penaltyCheckbox.checked) {
            penaltyFields.classList.remove('hidden');
        } else {
            penaltyFields.classList.add('hidden');
        }
    }
    
    // Toggle opciones avanzadas (acordeón)
    function toggleAdvancedOptions() {
        const isHidden = advancedOptions.classList.contains('hidden');
        
        if (isHidden) {
            advancedOptions.classList.remove('hidden');
            advancedToggle.querySelector('span').textContent = '[-] Opciones Avanzadas';
        } else {
            advancedOptions.classList.add('hidden');
            advancedToggle.querySelector('span').textContent = '[+] Opciones Avanzadas';
        }
    }
    
    // Toggle nombres de firmas
    function toggleSignatureNames() {
        if (includeSignaturesCheckbox.checked) {
            signatureNames.classList.remove('hidden');
        } else {
            signatureNames.classList.add('hidden');
        }
    }
    
    // ===== MANEJO DE ARCHIVOS =====
    
    // Preview del logo
    function handleLogoPreview() {
        const file = logoInput.files[0];
        filePreview.innerHTML = '';
        
        if (file) {
            // Validar tipo
            const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
            if (!validTypes.includes(file.type)) {
                showError('El archivo debe ser PNG o JPG');
                logoInput.value = '';
                return;
            }
            
            // Validar tamaño (2MB)
            if (file.size > 2 * 1024 * 1024) {
                showError('El archivo no debe superar 2MB');
                logoInput.value = '';
                return;
            }
            
            // Crear preview
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.alt = 'Vista previa del logo';
                filePreview.appendChild(img);
            };
            reader.readAsDataURL(file);
        }
    }
    
    // ===== VALIDACIONES =====
    
    // Configurar validación en tiempo real
    function setupRealTimeValidation() {
        const requiredFields = [
            'provider_name',
            'client_name',
            'client_phone',
            'service_description',
            'total_amount',
            'payment_deadline'
        ];
        
        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', () => validateField(field));
                field.addEventListener('input', () => clearError(field));
            }
        });
    }
    
    // Validar campo individual
    function validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        
        // Validaciones específicas por campo
        switch(field.id) {
            case 'provider_name':
            case 'client_name':
                isValid = value.length >= 3;
                break;
            case 'client_phone':
                const phoneDigits = value.replace(/\D/g, '');
                isValid = phoneDigits.length >= 10;
                break;
            case 'service_description':
                isValid = value.length >= 10;
                break;
            case 'total_amount':
                isValid = parseFloat(value) > 0;
                break;
            case 'payment_deadline':
                const selectedDate = new Date(value);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                isValid = selectedDate > today;
                break;
            default:
                isValid = value.length > 0;
        }
        
        if (!isValid) {
            showFieldError(field, getErrorMessage(field.id));
        } else {
            clearError(field);
        }
        
        return isValid;
    }
    
    // Obtener mensaje de error específico
    function getErrorMessage(fieldId) {
        const messages = {
            'provider_name': 'Nombre muy corto (mínimo 3 caracteres)',
            'client_name': 'Nombre muy corto (mínimo 3 caracteres)',
            'client_phone': 'Teléfono inválido (mínimo 10 dígitos)',
            'service_description': 'Descripción muy corta (mínimo 10 caracteres)',
            'total_amount': 'Monto debe ser mayor a 0',
            'payment_deadline': 'Fecha debe ser futura'
        };
        return messages[fieldId] || 'Campo inválido';
    }
    
    // Mostrar error en campo
    function showFieldError(field, message) {
        field.classList.add('error');
        const errorSpan = field.parentElement.querySelector('.error-msg');
        if (errorSpan) {
            errorSpan.textContent = message;
            errorSpan.classList.add('visible');
        }
    }
    
    // Limpiar error de campo
    function clearError(field) {
        field.classList.remove('error');
        const errorSpan = field.parentElement.querySelector('.error-msg');
        if (errorSpan) {
            errorSpan.classList.remove('visible');
        }
    }
    
    // Mostrar error general
    function showError(message) {
        formErrors.innerHTML = `<ul><li>${message}</li></ul>`;
        formErrors.classList.remove('hidden');
        setTimeout(() => {
            formErrors.classList.add('hidden');
        }, 5000);
    }
    
    // ===== CONFIGURACIÓN INICIAL =====
    
    // Establecer fecha mínima como hoy
    function setMinDate() {
        const deadlineInput = document.getElementById('payment_deadline');
        const today = new Date().toISOString().split('T')[0];
        deadlineInput.setAttribute('min', today);
    }
    
    // ===== SUBMIT DEL FORMULARIO =====
    
    async function handleSubmit(e) {
        e.preventDefault();
        
        // Limpiar errores previos
        formErrors.innerHTML = '';
        formErrors.classList.add('hidden');
        
        // Validar todos los campos requeridos
        const requiredFields = [
            'provider_name',
            'client_name',
            'client_phone',
            'service_description',
            'total_amount',
            'payment_deadline'
        ];
        
        let isValid = true;
        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (!validateField(field)) {
                isValid = false;
            }
        });
        
        // Validaciones condicionales
        if (hasMaterialsCheckbox.checked && !document.getElementById('materials_details').value.trim()) {
            showError('Debe especificar los materiales incluidos');
            isValid = false;
        }
        
        if (paymentMethodSelect.value === 'transfer' && !document.getElementById('bank_clabe').value.trim()) {
            showError('Debe proporcionar CLABE para transferencia');
            isValid = false;
        }
        
        if (paymentStructureSelect.value === 'advance') {
            const total = parseFloat(document.getElementById('total_amount').value) || 0;
            const advance = parseFloat(document.getElementById('advance_amount').value) || 0;
            const remaining = parseFloat(document.getElementById('remaining_amount').value) || 0;
            
            if (Math.abs((advance + remaining) - total) > 0.01) {
                showError('Anticipo + Resto debe ser igual al total');
                isValid = false;
            }
        }
        
        if (includeSignaturesCheckbox.checked) {
            if (!document.getElementById('provider_signature').value.trim()) {
                showError('Nombre requerido para firma del prestador');
                isValid = false;
            }
            if (!document.getElementById('client_signature').value.trim()) {
                showError('Nombre requerido para firma del cliente');
                isValid = false;
            }
        }
        
        if (!isValid) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            return;
        }
        
        // Enviar formulario
        try {
            // Mostrar estado de carga
            generateBtn.classList.add('loading');
            generateBtn.disabled = true;
            
            const formData = new FormData(contractForm);
            
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Redirigir a vista del contrato para imprimir
                window.location.href = `/view/${result.contract_id}`;
            } else {
                // Mostrar errores del backend
                const errorsList = result.errors.map(err => `<li>${err}</li>`).join('');
                formErrors.innerHTML = `<ul>${errorsList}</ul>`;
                formErrors.classList.remove('hidden');
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        } catch (error) {
            showError('Error de conexión. Intente nuevamente.');
        } finally {
            generateBtn.classList.remove('loading');
            generateBtn.disabled = false;
        }
    }
});
