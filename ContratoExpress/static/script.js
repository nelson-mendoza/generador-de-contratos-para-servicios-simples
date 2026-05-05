// Lógica del formulario dinámico

function toggleOtherService() {
    const type = document.getElementById('serviceType').value;
    const input = document.getElementById('customServiceInput');
    if (type === 'Otros') {
        input.classList.remove('hidden');
        input.setAttribute('required', 'true');
        input.name = "service_title"; 
    } else {
        input.classList.add('hidden');
        input.removeAttribute('required');
        input.name = ""; 
    }
}

function toggleMaterials() {
    const checkbox = document.getElementById('hasMaterials');
    const options = document.getElementById('materialsOptions');
    if (checkbox.checked) {
        options.classList.remove('hidden');
        options.querySelector('textarea').setAttribute('required', 'true');
    } else {
        options.classList.add('hidden');
        options.querySelector('textarea').removeAttribute('required');
    }
}

function calcRemaining() {
    const structure = document.getElementById('payStructure').value;
    const total = parseFloat(document.getElementById('totalAmount').value) || 0;
    const advanceInput = document.getElementById('advanceAmount');
    const remainingInput = document.getElementById('remainingAmount');
    
    const advanceDiv = document.getElementById('advanceDiv');
    const remainingDiv = document.getElementById('remainingDiv');

    if (structure === 'advance' || structure === 'partial') {
        advanceDiv.classList.remove('hidden');
        remainingDiv.classList.remove('hidden');
        const advance = parseFloat(advanceInput.value) || 0;
        remainingInput.value = (total - advance).toFixed(2);
    } else {
        advanceDiv.classList.add('hidden');
        remainingDiv.classList.add('hidden');
        advanceInput.value = '';
        remainingInput.value = total.toFixed(2);
    }
}

function togglePaymentDetails() {
    const method = document.getElementById('payMethod').value;
    document.getElementById('bankDetails').classList.add('hidden');
    document.getElementById('cryptoDetails').classList.add('hidden');
    document.getElementById('otherDetails').classList.add('hidden');
    
    document.querySelectorAll('#bankDetails input, #cryptoDetails input, #otherDetails input').forEach(i => i.removeAttribute('required'));

    if (method === 'transfer') {
        document.getElementById('bankDetails').classList.remove('hidden');
        document.getElementById('bankDetails').querySelector('input').setAttribute('required', 'true');
    } else if (method === 'crypto') {
        document.getElementById('cryptoDetails').classList.remove('hidden');
        document.getElementById('cryptoDetails').querySelector('input').setAttribute('required', 'true');
    } else if (method === 'other') {
        document.getElementById('otherDetails').classList.remove('hidden');
        document.getElementById('otherDetails').querySelector('input').setAttribute('required', 'true');
    }
}

function togglePenalties() {
    const timing = document.getElementById('payTiming').value;
    const section = document.getElementById('penaltySection');
    if (timing === 'before') {
        section.classList.add('hidden');
    } else {
        section.classList.remove('hidden');
    }
}

function toggleAdvanced() {
    const panel = document.getElementById('advancedOptions');
    panel.classList.toggle('hidden');
}

function toggleSignatureNames() {
    const checkbox = document.getElementById('includeSignatures');
    const namesDiv = document.getElementById('signatureNames');
    const inputs = namesDiv.querySelectorAll('input');
    
    if (checkbox.checked) {
        namesDiv.classList.remove('hidden');
        inputs[0].setAttribute('required', 'true');
        inputs[1].setAttribute('required', 'true');
    } else {
        namesDiv.classList.add('hidden');
        inputs[0].removeAttribute('required');
        inputs[1].removeAttribute('required');
    }
}

function previewLogo(input) {
    const preview = document.getElementById('logoPreview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.classList.remove('hidden');
        }
        reader.readAsDataURL(input.files[0]);
    } else {
        preview.classList.add('hidden');
    }
}

document.getElementById('contractForm').addEventListener('submit', function(e) {
    const total = parseFloat(document.getElementById('totalAmount').value);
    if (total <= 0) {
        e.preventDefault();
        alert("El monto total debe ser mayor a 0.");
        return false;
    }
    
    const customInput = document.getElementById('customServiceInput');
    if (!customInput.classList.contains('hidden')) {
        if(!customInput.value) {
            e.preventDefault();
            alert("Especifica el tipo de servicio personalizado.");
            return false;
        }
    }
});
