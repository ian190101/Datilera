// app/interfaces/web/static/js/inscripciones.js

import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';

let currentStep = 1;
let formData = {};
let codigoGenerado = '';
let telefonoTutor = '';
let nombreTutor = '';
let nombreNino = '';

/* ============================================================
   NAVEGACIÓN ENTRE PASOS
   ============================================================ */
window.nextStep = async function(step) {
    if (!await validateStep(step)) {
        return;
    }
    
    saveStepData(step);
    currentStep = step + 1;
    showStep(currentStep);
    
    if (currentStep === 3) {
        generateResumen();
    }
}

window.prevStep = function(step) {
    currentStep = step - 1;
    showStep(currentStep);
}

function showStep(step) {
    document.querySelectorAll('.step').forEach(el => {
        el.classList.remove('active');
        el.classList.add('inactive');
    });
    
    document.getElementById(`step-${step}`).classList.remove('inactive');
    document.getElementById(`step-${step}`).classList.add('active');
    
    updateStepIndicators(step);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateStepIndicators(currentStepNum) {
    for (let i = 1; i <= 3; i++) {
        const indicator = document.getElementById(`step-indicator-${i}`);
        
        if (i < currentStepNum) {
            indicator.classList.remove('active', 'pending');
            indicator.classList.add('completed');
            indicator.innerHTML = '<i class="fas fa-check"></i>';
        } else if (i === currentStepNum) {
            indicator.classList.remove('completed', 'pending');
            indicator.classList.add('active');
            indicator.textContent = i;
        } else {
            indicator.classList.remove('completed', 'active');
            indicator.classList.add('pending');
            indicator.textContent = i;
        }
    }
}

/* ============================================================
   VALIDACIÓN POR PASO
   ============================================================ */
async function validateStep(step) {
    clearErrors();
    switch (step) {
        case 1: return validateStep1();
        case 2: return validateStep2();
        default: return true;
    }
}

function validateStep1() {
    let isValid = true;
    
    const nombres = document.getElementById('nombres').value.trim();
    if (!nombres || nombres.length < 2) {
        showError('nombres', 'Los nombres son obligatorios (mínimo 2 caracteres)');
        isValid = false;
    }
    
    const apellidos = document.getElementById('apellidos').value.trim();
    if (!apellidos || apellidos.length < 2) {
        showError('apellidos', 'Los apellidos son obligatorios');
        isValid = false;
    }
    
    const fechaNacimiento = document.getElementById('fecha_nacimiento').value;
    if (!fechaNacimiento) {
        showError('fecha_nacimiento', 'La fecha de nacimiento es obligatoria');
        isValid = false;
    }
    
    const genero = document.getElementById('genero').value;
    if (!genero) {
        showError('genero', 'Selecciona el género');
        isValid = false;
    }
    
    const grupo = document.getElementById('grupo').value;
    if (!grupo) {
        showError('grupo', 'Selecciona el grupo');
        isValid = false;
    }
    
    return isValid;
}

function validateStep2() {
    let isValid = true;
    const tutorNombre = document.getElementById('tutor_nombre').value.trim();
    if (!tutorNombre || tutorNombre.length < 5) {
        showError('tutor_nombre', 'El nombre completo es obligatorio');
        isValid = false;
    }
    
    const tutorTelefono = document.getElementById('tutor_telefono').value.trim();
    if (!tutorTelefono || !/^\d{7,8}$/.test(tutorTelefono)) {
        showError('tutor_telefono', 'El teléfono debe tener 7 u 8 dígitos');
        isValid = false;
    }
    
    return isValid;
}

function showError(fieldId, message) {
    const errorElement = document.getElementById(`${fieldId}-error`);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
    }
    const inputElement = document.getElementById(fieldId);
    if (inputElement) {
        inputElement.classList.add('border-red-500', 'focus:ring-red-500');
    }
}

function clearErrors() {
    document.querySelectorAll('[id$="-error"]').forEach(el => {
        el.classList.add('hidden');
        el.textContent = '';
    });
    document.querySelectorAll('input, select, textarea').forEach(el => {
        el.classList.remove('border-red-500', 'focus:ring-red-500');
    });
}

/* ============================================================
   GUARDAR DATOS DEL PASO
   ============================================================ */
function saveStepData(step) {
    const stepElement = document.getElementById(`step-${step}`);
    const inputs = stepElement.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        formData[input.name] = input.value;
    });
}

/* ============================================================
   GENERAR RESUMEN
   ============================================================ */
function generateResumen() {
    const resumenContent = document.getElementById('resumen-content');
    const grupoSelect = document.getElementById('grupo');
    const grupoTexto = grupoSelect.options[grupoSelect.selectedIndex]?.text || 'No seleccionado';

    const html = `
        <div class="p-6 bg-gray-50 dark:bg-gray-900 rounded-lg">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <i class="fas fa-child text-primary-500 mr-2"></i>
                Datos del Niño/a
            </h4>
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="text-gray-600 dark:text-gray-400">Nombre:</span>
                    <p class="font-medium text-gray-900 dark:text-white">${formData.nombres} ${formData.apellidos}</p>
                </div>
                <div>
                    <span class="text-gray-600 dark:text-gray-400">Grupo:</span>
                    <p class="font-medium text-gray-900 dark:text-white">${grupoTexto}</p>
                </div>
            </div>
        </div>
        <div class="p-6 bg-gray-50 dark:bg-gray-900 rounded-lg mt-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <i class="fas fa-user text-primary-500 mr-2"></i>
                Tutor Principal
            </h4>
            <div class="grid grid-cols-2 gap-4 text-sm">
                <div>
                    <span class="text-gray-600 dark:text-gray-400">Nombre:</span>
                    <p class="font-medium text-gray-900 dark:text-white">${formData.tutor_nombre}</p>
                </div>
                <div>
                    <span class="text-gray-600 dark:text-gray-400">Teléfono:</span>
                    <p class="font-medium text-gray-900 dark:text-white">+591 ${formData.tutor_telefono}</p>
                </div>
            </div>
        </div>
    `;
    resumenContent.innerHTML = html;
}

/* ============================================================
   ENVIAR FORMULARIO (POST REAL)
   ============================================================ */
document.getElementById('inscripcion-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const btnFinalizar = document.getElementById('btn-finalizar');
    const originalText = btnFinalizar.innerHTML;
    btnFinalizar.disabled = true;
    btnFinalizar.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Generando código...';
    
    try {
        // CORRECCIÓN: Usar el código que viene del backend, NO generarlo aquí.
        // CORRECCIÓN: Los apellidos ya se envían como string en "apellidos", 
        // el backend se encarga de separarlos en paterno/materno si es necesario.
        
        const response = await fetchAPI(`${API_BASE}/inscripciones/preinscripcion`, {
            method: 'POST',
            body: JSON.stringify(formData),
        });
        
        const data = await response.json();
        
        if (response.ok) {

            console.log("Respuesta del servidor:", data); 
            console.log("Código en data.codigo_tutor:", data.codigo_tutor);

            // USAR EL CÓDIGO REAL DEL BACKEND
            codigoGenerado = data.codigo_tutor;
            
            telefonoTutor = formData.tutor_telefono;
            nombreTutor = formData.tutor_nombre;
            nombreNino = `${formData.nombres} ${formData.apellidos}`;
            
            // Mostrar pantalla de éxito con el código CORRECTO
            document.getElementById('resumen-inscripcion').classList.add('hidden');
            document.getElementById('success-message').classList.remove('hidden');
            document.getElementById('codigo-tutor-display').textContent = codigoGenerado; // <--- AQUÍ SE MUESTRA EL CÓDIGO REAL
            
            document.getElementById('btn-enviar-whatsapp').onclick = enviarCodigoPorWhatsApp;
            showToast('¡Pre-inscripción creada exitosamente!', 'success');
        } else {
            throw new Error(data.detail || 'Error al crear pre-inscripción');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message, 'error');
        btnFinalizar.disabled = false;
        btnFinalizar.innerHTML = originalText;
    }
});

/* ============================================================
   ENVIAR WHATSAPP
   ============================================================ */
function enviarCodigoPorWhatsApp() {
    const appUrl = window.location.origin;
    const mensaje = encodeURIComponent(
        `🌴 *¡Bienvenido a Datilera!*\n\n` +
        `Hola ${nombreTutor}, hemos pre-inscrito a *${nombreNino}*.\n\n` +
        `Tu código de acceso es:\n` +
        `🔑 *${codigoGenerado}*\n\n` +
        `Ingresa a: ${appUrl}/registro-tutor\n`
    );
    window.open(`https://wa.me/591${telefonoTutor}?text=${mensaje}`, '_blank');
}

window.copiarCodigo = function() {
    navigator.clipboard.writeText(codigoGenerado);
    showToast('Código copiado', 'success');
}

/* ============================================================
   CARGAR GRUPOS DESDE BD
   ============================================================ */
async function loadGrupos() {
    try {
        const response = await fetchAPI(`${API_BASE}/grupos`);
        const data = await response.json();
        
        const select = document.getElementById('grupo');
        // Limpiar opciones previas manteniendo el placeholder
        while (select.options.length > 1) {
            select.remove(1);
        }
        
        if (data.items) {
            data.items.forEach(g => {
                const option = document.createElement('option');
                option.value = g.id;
                option.textContent = g.nombre;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error("Error cargando grupos:", error);
    }
}

/* ============================================================
   HELPERS
   ============================================================ */
function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    return age;
}

document.getElementById('fecha_nacimiento')?.addEventListener('change', (e) => {
    const edad = calculateAge(e.target.value);
    document.getElementById('edad-display').textContent = `${edad} años`;
});

function formatDate(dateString) {
    if (!dateString) return '';
    const [y, m, d] = dateString.split('-');
    return `${d}/${m}/${y}`;
}

document.addEventListener('DOMContentLoaded', () => {
    showStep(1);
    loadGrupos(); // Cargar lista real
});