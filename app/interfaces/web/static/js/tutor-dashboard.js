// app/interfaces/web/static/js/registro-tutores.js

const API_BASE = '/api/v1';

let currentStep = 1;
const totalSteps = 7;
let codigoValido = false;
let datosPreinscripcion = null;

// Canvas para firmas
let canvasTutor1, ctxTutor1, isDrawingTutor1 = false;
let canvasTutor2, ctxTutor2, isDrawingTutor2 = false;

/* ============================================================
   INICIALIZACIÓN
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
    // Verificar si viene código en URL
    const urlParams = new URLSearchParams(window.location.search);
    const codigoURL = urlParams.get('codigo');
    
    if (codigoURL) {
        document.getElementById('codigo-registro').value = codigoURL.toUpperCase();
    }
    
    // Inicializar canvas de firmas
    initCanvasFirmas();
    
    // Event listeners
    initEventListeners();
    
    // Mostrar primer paso
    showStep(1);
});

/* ============================================================
   EVENT LISTENERS
   ============================================================ */
function initEventListeners() {
    // Auto-formatear código a mayúsculas
    document.getElementById('codigo-registro')?.addEventListener('input', (e) => {
        e.target.value = e.target.value.toUpperCase();
    });
    
    // Validación en tiempo real de contraseña
    document.getElementById('password')?.addEventListener('input', validatePassword);
    document.getElementById('password-confirm')?.addEventListener('input', validatePasswordConfirm);
    
    // Validación de nombre de usuario
    document.getElementById('nombre-usuario')?.addEventListener('blur', checkUsernameAvailable);
    
    // Validación de email
    document.getElementById('email-cuenta')?.addEventListener('blur', checkEmailAvailable);
    
    // Submit del formulario
    document.getElementById('form-registro')?.addEventListener('submit', handleSubmit);
}

/* ============================================================
   NAVEGACIÓN ENTRE PASOS
   ============================================================ */
function showStep(step) {
    // Ocultar todos los pasos
    document.querySelectorAll('.step-container').forEach(container => {
        container.classList.remove('active');
    });
    
    // Mostrar paso actual
    document.getElementById(`step-${step}`).classList.add('active');
    
    // Actualizar indicadores
    updateStepIndicators(step);
    
    // Actualizar barra de progreso
    const progress = (step / totalSteps) * 100;
    document.getElementById('progress-bar').style.width = `${progress}%`;
    
    // Mostrar/ocultar botones
    const btnAnterior = document.getElementById('btn-anterior');
    const btnSiguiente = document.getElementById('btn-siguiente');
    const btnFinalizar = document.getElementById('btn-finalizar');
    
    if (step === 1) {
        btnAnterior.classList.add('hidden');
    } else {
        btnAnterior.classList.remove('hidden');
    }
    
    if (step === totalSteps) {
        btnSiguiente.classList.add('hidden');
        btnFinalizar.classList.remove('hidden');
    } else {
        btnSiguiente.classList.remove('hidden');
        btnFinalizar.classList.add('hidden');
    }
    
    // Scroll al inicio
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    currentStep = step;
}

function updateStepIndicators(step) {
    document.querySelectorAll('.step-indicator').forEach((indicator, index) => {
        const stepNum = index + 1;
        const circle = indicator.querySelector('.step-circle');
        const text = indicator.querySelector('span');
        
        if (stepNum < step) {
            // Paso completado - SIEMPRE NARANJA #DD8E0A
            circle.style.background = '#10B981'; // Verde para completado
            circle.classList.remove('bg-gray-300', 'text-gray-600');
            circle.classList.add('text-white');
            circle.innerHTML = '<i class="fas fa-check"></i>';
            text.style.color = '#10B981';
        } else if (stepNum === step) {
            // Paso actual - NARANJA #DD8E0A
            circle.style.background = '#DD8E0A';
            circle.classList.remove('bg-gray-300', 'text-gray-600');
            circle.classList.add('text-white');
            circle.textContent = stepNum;
            text.style.color = '#DD8E0A';
        } else {
            // Paso pendiente - GRIS
            circle.style.background = '#D1D5DB';
            circle.classList.remove('text-white');
            circle.classList.add('bg-gray-300', 'text-gray-600');
            circle.textContent = stepNum;
            text.style.color = '#9CA3AF';
        }
    });
}

window.siguientePaso = async function() {
    // Validar paso actual antes de avanzar
    if (!await validateCurrentStep()) {
        return;
    }
    
    if (currentStep < totalSteps) {
        showStep(currentStep + 1);
    }
}

window.anteriorPaso = function() {
    if (currentStep > 1) {
        showStep(currentStep - 1);
    }
}

/* ============================================================
   VALIDACIÓN DEL CÓDIGO (PASO 1)
   ============================================================ */
async function validateCurrentStep() {
    switch (currentStep) {
        case 1:
            return await validarCodigo();
        case 2:
            return validatePaso2();
        case 3:
            return validatePaso3();
        case 4:
            return validatePaso4();
        case 5:
            return validatePaso5();
        case 6:
            return validatePaso6();
        case 7:
            return validatePaso7();
        default:
            return true;
    }
}

async function validarCodigo() {
    const codigo = document.getElementById('codigo-registro').value.trim();
    
    if (codigo.length !== 6) {
        Swal.fire({
            icon: 'error',
            title: 'Código inválido',
            text: 'El código debe tener exactamente 6 caracteres',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    // Mostrar loading
    Swal.fire({
        title: 'Validando código...',
        html: 'Por favor espera',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    try {
        const response = await fetch(`${API_BASE}/tutores/validar-codigo`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ codigo })
        });
        
        const data = await response.json();
        
        if (response.ok && data.valido) {
            Swal.close();
            
            // Guardar datos de preinscripción
            datosPreinscripcion = data.preinscripcion;
            codigoValido = true;
            
            // Pre-cargar datos del niño
            document.getElementById('preview-nombres').textContent = data.preinscripcion.nombres;
            document.getElementById('preview-apellidos').textContent = data.preinscripcion.apellidos;
            
            Swal.fire({
                icon: 'success',
                title: '¡Código válido!',
                text: `Bienvenido. Vas a completar la inscripción de ${data.preinscripcion.nombres}`,
                confirmButtonColor: '#DD8E0A',
                timer: 2000
            });
            
            return true;
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Código inválido',
                text: data.mensaje || 'El código no existe o ya fue utilizado',
                confirmButtonColor: '#DD8E0A'
            });
            return false;
        }
        
    } catch (error) {
        console.error('Error validando código:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Hubo un problema al validar el código. Intenta nuevamente.',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
}

/* ============================================================
   VALIDACIONES POR PASO
   ============================================================ */
function validatePaso2() {
    const required = ['genero', 'lugar_nacimiento'];
    
    for (const field of required) {
        const input = document.querySelector(`[name="${field}"]`);
        if (!input || !input.value.trim()) {
            Swal.fire({
                icon: 'warning',
                title: 'Campos incompletos',
                text: 'Por favor completa todos los campos obligatorios',
                confirmButtonColor: '#DD8E0A'
            });
            input?.focus();
            return false;
        }
    }
    
    return true;
}

function validatePaso3() {
    const required = [
        'tutor1_relacion',
        'tutor1_nombres',
        'tutor1_ci',
        'tutor1_expedido',
        'tutor1_celular',
        'tutor1_email',
        'tutor1_direccion'
    ];
    
    for (const field of required) {
        const input = document.querySelector(`[name="${field}"]`);
        if (!input || !input.value.trim()) {
            Swal.fire({
                icon: 'warning',
                title: 'Campos incompletos',
                text: 'Por favor completa todos los campos obligatorios del tutor principal',
                confirmButtonColor: '#DD8E0A'
            });
            input?.focus();
            return false;
        }
    }
    
    // Validar formato de celular (8 dígitos)
    const celular = document.querySelector('[name="tutor1_celular"]').value;
    if (!/^\d{8}$/.test(celular)) {
        Swal.fire({
            icon: 'warning',
            title: 'Celular inválido',
            text: 'El celular debe tener 8 dígitos',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    // Validar email
    const email = document.querySelector('[name="tutor1_email"]').value;
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        Swal.fire({
            icon: 'warning',
            title: 'Email inválido',
            text: 'Ingresa un correo electrónico válido',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    return true;
}

function validatePaso4() {
    // Si tiene tutor 2, validar sus campos
    const tieneTutor2 = document.getElementById('tiene-tutor2').checked;
    
    if (tieneTutor2) {
        const required = ['tutor2_nombres', 'tutor2_ci'];
        
        for (const field of required) {
            const input = document.querySelector(`[name="${field}"]`);
            if (!input || !input.value.trim()) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Campos incompletos',
                    text: 'Por favor completa los datos básicos del segundo tutor',
                    confirmButtonColor: '#DD8E0A'
                });
                input?.focus();
                return false;
            }
        }
    }
    
    return true;
}

function validatePaso5() {
    const requiredDocs = [
        'doc_certificado_nacimiento',
        'doc_ci_tutor1',
        'doc_carnet_vacunas'
    ];
    
    for (const doc of requiredDocs) {
        const input = document.querySelector(`[name="${doc}"]`);
        if (!input || !input.files || input.files.length === 0) {
            Swal.fire({
                icon: 'warning',
                title: 'Documentos incompletos',
                text: 'Por favor sube todos los documentos obligatorios',
                confirmButtonColor: '#DD8E0A'
            });
            return false;
        }
        
        // Validar tamaño (10MB)
        const file = input.files[0];
        if (file.size > 10 * 1024 * 1024) {
            Swal.fire({
                icon: 'warning',
                title: 'Archivo muy grande',
                text: `El archivo ${file.name} supera los 10MB`,
                confirmButtonColor: '#DD8E0A'
            });
            return false;
        }
    }
    
    return true;
}

function validatePaso6() {
    // Validar firma tutor 1
    const firmaTutor1 = document.getElementById('firma-tutor1-data').value;
    if (!firmaTutor1) {
        Swal.fire({
            icon: 'warning',
            title: 'Firma requerida',
            text: 'Por favor firma en el recuadro del tutor principal',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    // Validar firma tutor 2 si existe
    const tieneTutor2 = document.getElementById('tiene-tutor2')?.checked;
    if (tieneTutor2) {
        const firmaTutor2 = document.getElementById('firma-tutor2-data').value;
        if (!firmaTutor2) {
            Swal.fire({
                icon: 'warning',
                title: 'Firma requerida',
                text: 'Por favor firma en el recuadro del segundo tutor',
                confirmButtonColor: '#DD8E0A'
            });
            return false;
        }
    }
    
    // Validar consentimiento
    if (!document.getElementById('consentimiento').checked) {
        Swal.fire({
            icon: 'warning',
            title: 'Consentimiento requerido',
            text: 'Debes aceptar el consentimiento de imágenes',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    return true;
}

async function validatePaso7() {
    const usuario = document.getElementById('nombre-usuario').value.trim();
    const email = document.getElementById('email-cuenta').value.trim();
    const password = document.getElementById('password').value;
    const passwordConfirm = document.getElementById('password-confirm').value;
    
    if (!usuario || usuario.length < 4) {
        Swal.fire({
            icon: 'warning',
            title: 'Nombre de usuario inválido',
            text: 'Debe tener al menos 4 caracteres',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        Swal.fire({
            icon: 'warning',
            title: 'Email inválido',
            text: 'Ingresa un correo electrónico válido',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    if (password.length < 8) {
        Swal.fire({
            icon: 'warning',
            title: 'Contraseña muy corta',
            text: 'Debe tener al menos 8 caracteres',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    if (password !== passwordConfirm) {
        Swal.fire({
            icon: 'warning',
            title: 'Contraseñas no coinciden',
            text: 'Las contraseñas deben ser iguales',
            confirmButtonColor: '#DD8E0A'
        });
        return false;
    }
    
    return true;
}

/* ============================================================
   CANVAS DE FIRMAS
   ============================================================ */
function initCanvasFirmas() {
    // Canvas Tutor 1
    canvasTutor1 = document.getElementById('canvas-firma-tutor1');
    if (canvasTutor1) {
        ctxTutor1 = canvasTutor1.getContext('2d');
        ctxTutor1.strokeStyle = '#000';
        ctxTutor1.lineWidth = 2;
        
        // Mouse events
        canvasTutor1.addEventListener('mousedown', startDrawingTutor1);
        canvasTutor1.addEventListener('mousemove', drawTutor1);
        canvasTutor1.addEventListener('mouseup', stopDrawingTutor1);
        canvasTutor1.addEventListener('mouseleave', stopDrawingTutor1);
        
        // Touch events
        canvasTutor1.addEventListener('touchstart', handleTouchStart1);
        canvasTutor1.addEventListener('touchmove', handleTouchMove1);
        canvasTutor1.addEventListener('touchend', stopDrawingTutor1);
    }
    
    // Canvas Tutor 2
    canvasTutor2 = document.getElementById('canvas-firma-tutor2');
    if (canvasTutor2) {
        ctxTutor2 = canvasTutor2.getContext('2d');
        ctxTutor2.strokeStyle = '#000';
        ctxTutor2.lineWidth = 2;
        
        canvasTutor2.addEventListener('mousedown', startDrawingTutor2);
        canvasTutor2.addEventListener('mousemove', drawTutor2);
        canvasTutor2.addEventListener('mouseup', stopDrawingTutor2);
        canvasTutor2.addEventListener('mouseleave', stopDrawingTutor2);
        
        canvasTutor2.addEventListener('touchstart', handleTouchStart2);
        canvasTutor2.addEventListener('touchmove', handleTouchMove2);
        canvasTutor2.addEventListener('touchend', stopDrawingTutor2);
    }
}

// Tutor 1 Drawing
function startDrawingTutor1(e) {
    isDrawingTutor1 = true;
    const rect = canvasTutor1.getBoundingClientRect();
    ctxTutor1.beginPath();
    ctxTutor1.moveTo(e.clientX - rect.left, e.clientY - rect.top);
}

function drawTutor1(e) {
    if (!isDrawingTutor1) return;
    const rect = canvasTutor1.getBoundingClientRect();
    ctxTutor1.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctxTutor1.stroke();
}

function stopDrawingTutor1() {
    if (isDrawingTutor1) {
        isDrawingTutor1 = false;
        document.getElementById('firma-tutor1-data').value = canvasTutor1.toDataURL();
    }
}

function handleTouchStart1(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousedown', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvasTutor1.dispatchEvent(mouseEvent);
}

function handleTouchMove1(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvasTutor1.dispatchEvent(mouseEvent);
}

// Tutor 2 Drawing
function startDrawingTutor2(e) {
    isDrawingTutor2 = true;
    const rect = canvasTutor2.getBoundingClientRect();
    ctxTutor2.beginPath();
    ctxTutor2.moveTo(e.clientX - rect.left, e.clientY - rect.top);
}

function drawTutor2(e) {
    if (!isDrawingTutor2) return;
    const rect = canvasTutor2.getBoundingClientRect();
    ctxTutor2.lineTo(e.clientX - rect.left, e.clientY - rect.top);
    ctxTutor2.stroke();
}

function stopDrawingTutor2() {
    if (isDrawingTutor2) {
        isDrawingTutor2 = false;
        document.getElementById('firma-tutor2-data').value = canvasTutor2.toDataURL();
    }
}

function handleTouchStart2(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousedown', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvasTutor2.dispatchEvent(mouseEvent);
}

function handleTouchMove2(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent('mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvasTutor2.dispatchEvent(mouseEvent);
}

window.limpiarFirma = function(tutor) {
    if (tutor === 'tutor1') {
        ctxTutor1.clearRect(0, 0, canvasTutor1.width, canvasTutor1.height);
        document.getElementById('firma-tutor1-data').value = '';
    } else {
        ctxTutor2.clearRect(0, 0, canvasTutor2.width, canvasTutor2.height);
        document.getElementById('firma-tutor2-data').value = '';
    }
}

/* ============================================================
   TOGGLE DE CAMPOS CONDICIONALES
   ============================================================ */
window.toggleAlergias = function() {
    const tiene = document.querySelector('[name="tiene_alergias"]:checked').value;
    const textarea = document.getElementById('textarea-alergias');
    
    if (tiene === 'SI') {
        textarea.classList.remove('hidden');
        textarea.required = true;
    } else {
        textarea.classList.add('hidden');
        textarea.required = false;
        textarea.value = '';
    }
}

window.toggleMedicacion = function() {
    const tiene = document.querySelector('[name="tiene_medicacion"]:checked').value;
    const textarea = document.getElementById('textarea-medicacion');
    
    if (tiene === 'SI') {
        textarea.classList.remove('hidden');
        textarea.required = true;
    } else {
        textarea.classList.add('hidden');
        textarea.required = false;
        textarea.value = '';
    }
}

window.toggleTutor2 = function() {
    const checked = document.getElementById('tiene-tutor2').checked;
    const campos = document.getElementById('campos-tutor2');
    const firmaContainer = document.getElementById('firma-tutor2-container');
    const docContainer = document.getElementById('doc-ci-tutor2-container');
    
    if (checked) {
        campos.classList.remove('hidden');
        firmaContainer?.classList.remove('hidden');
        docContainer?.classList.remove('hidden');
    } else {
        campos.classList.add('hidden');
        firmaContainer?.classList.add('hidden');
        docContainer?.classList.add('hidden');
    }
}

/* ============================================================
   VALIDACIONES EN TIEMPO REAL
   ============================================================ */
function validatePassword() {
    const password = document.getElementById('password').value;
    const feedback = document.getElementById('password-feedback');
    
    const hasLength = password.length >= 8;
    const hasLetter = /[a-zA-Z]/.test(password);
    const hasNumber = /\d/.test(password);
    
    // Actualizar indicadores visuales - USAR COLOR #DD8E0A
    updateRequirement('req-length', hasLength);
    updateRequirement('req-letter', hasLetter);
    updateRequirement('req-number', hasNumber);
    
    if (hasLength && hasLetter && hasNumber) {
        feedback.textContent = '✓ Contraseña segura';
        feedback.style.color = '#10B981'; // Verde para éxito
    } else {
        feedback.textContent = '';
    }
}

function updateRequirement(id, met) {
    const el = document.getElementById(id);
    const icon = el.querySelector('i');
    
    if (met) {
        icon.className = 'fas fa-check-circle mr-2 text-xs';
        icon.style.color = '#10B981'; // Verde
        el.style.color = '#10B981';
    } else {
        icon.className = 'fas fa-circle mr-2 text-xs';
        icon.style.color = '#9CA3AF'; // Gris
        el.style.color = '#6B7280';
    }
}

function validatePasswordConfirm() {
    const password = document.getElementById('password').value;
    const confirm = document.getElementById('password-confirm').value;
    const feedback = document.getElementById('password-confirm-feedback');
    
    if (confirm === '') {
        feedback.textContent = '';
        return;
    }
    
    if (password === confirm) {
        feedback.textContent = '✓ Las contraseñas coinciden';
        feedback.style.color = '#10B981'; // Verde
    } else {
        feedback.textContent = '✗ Las contraseñas no coinciden';
        feedback.style.color = '#EF4444'; // Rojo
    }
}

async function checkUsernameAvailable() {
    const username = document.getElementById('nombre-usuario').value.trim();
    const feedback = document.getElementById('usuario-feedback');
    
    if (username.length < 4) {
        feedback.textContent = '';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tutores/check-username?username=${username}`);
        const data = await response.json();
        
        if (data.disponible) {
            feedback.textContent = '✓ Nombre de usuario disponible';
            feedback.style.color = '#10B981'; // Verde
        } else {
            feedback.textContent = '✗ Este nombre de usuario ya está en uso';
            feedback.style.color = '#EF4444'; // Rojo
        }
    } catch (error) {
        console.error('Error checking username:', error);
    }
}

async function checkEmailAvailable() {
    const email = document.getElementById('email-cuenta').value.trim();
    const feedback = document.getElementById('email-feedback');
    
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        feedback.textContent = '';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/tutores/check-email?email=${email}`);
        const data = await response.json();
        
        if (data.disponible) {
            feedback.textContent = '✓ Email disponible';
            feedback.style.color = '#10B981'; // Verde
        } else {
            feedback.textContent = '✗ Este email ya está registrado';
            feedback.style.color = '#EF4444'; // Rojo
        }
    } catch (error) {
        console.error('Error checking email:', error);
    }
}

window.togglePassword = function(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

/* ============================================================
   ENVÍO DEL FORMULARIO
   ============================================================ */
async function handleSubmit(e) {
    e.preventDefault();
    
    // Validación final
    if (!await validatePaso7()) {
        return;
    }
    
    // Mostrar loading
    Swal.fire({
        title: 'Procesando registro...',
        html: 'Por favor espera mientras guardamos tu información',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
    
    try {
        // Construir FormData con todos los datos
        const formData = new FormData(document.getElementById('form-registro'));
        
        // Agregar código validado
        formData.append('codigo_validado', document.getElementById('codigo-registro').value);
        
        // Enviar al backend
        const response = await fetch(`${API_BASE}/tutores/completar-registro`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Éxito
            Swal.fire({
                icon: 'success',
                title: '¡Registro completado!',
                html: `
                    <p class="mb-4">Tu cuenta ha sido creada exitosamente.</p>
                    <p class="text-sm text-gray-600">Usuario: <strong>${data.usuario}</strong></p>
                    <p class="text-sm text-gray-600 mt-2">Serás redirigido al inicio de sesión...</p>
                `,
                confirmButtonColor: '#DD8E0A',
                timer: 3000,
                showConfirmButton: false
            }).then(() => {
                // Redirigir a login
                window.location.href = '/login';
            });
        } else {
            throw new Error(data.mensaje || 'Error al completar el registro');
        }
        
    } catch (error) {
        console.error('Error en registro:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error al registrar',
            text: error.message || 'Hubo un problema al completar tu registro. Por favor intenta nuevamente.',
            confirmButtonColor: '#DD8E0A'
        });
    }
}
