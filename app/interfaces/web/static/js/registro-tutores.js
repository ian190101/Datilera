// app/interfaces/web/static/js/registro-tutores.js

const API_BASE = '/api/v1';
let currentStep = 1;
const totalSteps = 10;

// --- FUNCIÓN DE INICIO PRINCIPAL ---
function initApp() {
    console.log("🚀 JS de Registro Tutores INICIADO");

    // 1. Verificar si viene código en URL
    const urlParams = new URLSearchParams(window.location.search);
    const codigoURL = urlParams.get('codigo');
    
    const codigoInput = document.getElementById('codigo-registro');
    if (codigoURL && codigoInput) {
        codigoInput.value = codigoURL.toUpperCase();
        console.log("Código cargado desde URL:", codigoURL);
    }

    // 2. Inicializar Listeners
    initListeners();
    
    // 3. Mostrar paso 1
    showStep(1);
}

// --- EJECUCIÓN INMEDIATA (Para type="module") ---
if (document.readyState === 'loading') {
    // Por si acaso se carga tradicionalmente
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    // Si es módulo o ya cargó, ejecutar directo
    initApp();
}

function initListeners() {
    console.log("👂 Inicializando Listeners...");

    // Botón Siguiente (btn-siguiente)
    const btnSiguiente = document.getElementById('btn-siguiente');
    if (btnSiguiente) {
        btnSiguiente.addEventListener('click', async () => {
            console.log("🖱️ Click en Siguiente");
            
            if (currentStep === 1) {
                // Validación especial para el paso 1 (Código)
                const isValid = await validarCodigoBackend();
                if (!isValid) return;
            } else {
                // Validación genérica de campos 'required'
                if (!validateStepFields(currentStep)) return;
            }
            
            if (currentStep < totalSteps) {
                currentStep++;
                showStep(currentStep);
            }
        });
    } else {
        console.warn("⚠️ No se encontró el botón 'btn-siguiente'");
    }

    // Botón Anterior (btn-anterior)
    const btnAnterior = document.getElementById('btn-anterior');
    if (btnAnterior) {
        btnAnterior.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                showStep(currentStep);
            }
        });
    }

    // Botón Finalizar (btn-finalizar) - Submit del form
    const formRegistro = document.getElementById('form-registro');
    if (formRegistro) {
        formRegistro.addEventListener('submit', handleFinalSubmit);
    }

    // Botón Validar código dedicado (btn-validar-codigo)
    const btnValidar = document.getElementById('btn-validar-codigo');
    if (btnValidar) {
        btnValidar.addEventListener('click', async () => {
            console.log("🖱️ Click en Validar Código");
            const isValid = await validarCodigoBackend();
            if (isValid) {
                currentStep++;
                showStep(currentStep);
            }
        });
    }
}

function showStep(step) {
    // Ocultar todos
    document.querySelectorAll('.step-container').forEach(el => el.classList.remove('active'));
    
    // Mostrar actual
    const currentStepEl = document.getElementById(`step-${step}`);
    if (currentStepEl) currentStepEl.classList.add('active');
    
    // Actualizar barra e indicadores
    const stepIndicator = document.getElementById('step-indicator');
    if (stepIndicator) stepIndicator.textContent = `Paso ${step} de ${totalSteps}`;
    
    // Barra de progreso
    const progressBar = document.getElementById('progress-bar');
    if (progressBar) progressBar.style.width = `${(step/totalSteps)*100}%`;

    // --- MANEJO DE VISIBILIDAD DE BOTONES ---
    const btnAnterior = document.getElementById('btn-anterior');
    const btnSiguiente = document.getElementById('btn-siguiente');
    const btnFinalizar = document.getElementById('btn-finalizar');

    if (btnAnterior) btnAnterior.classList.toggle('hidden', step === 1);
    
    if (step === totalSteps) {
        if (btnSiguiente) btnSiguiente.classList.add('hidden');
        if (btnFinalizar) btnFinalizar.classList.remove('hidden');
    } else {
        if (btnSiguiente) btnSiguiente.classList.remove('hidden');
        if (btnFinalizar) btnFinalizar.classList.add('hidden');
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function validateStepFields(step) {
    const container = document.getElementById(`step-${step}`);
    if (!container) return true;

    const requiredInputs = container.querySelectorAll('[required]');
    let valid = true;

    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('border-red-500', 'ring-1', 'ring-red-500');
            valid = false;
        } else {
            input.classList.remove('border-red-500', 'ring-1', 'ring-red-500');
        }
    });

    if (!valid) {
        Swal.fire({
            icon: 'warning',
            title: 'Campos Incompletos',
            text: 'Por favor complete los campos obligatorios marcados con *',
            confirmButtonColor: '#DD8E0A'
        });
    }
    return valid;
}

window.toggleField = function(id, show) {
    const el = document.getElementById(id);
    if (show) el.classList.remove('hidden'); else el.classList.add('hidden');
}

async function validarCodigoBackend() {
    const codigoInput = document.getElementById('codigo-registro');
    if (!codigoInput) return false;
    
    const codigo = codigoInput.value.trim().toUpperCase();

    if (codigo.length !== 6) {
        Swal.fire('Error', 'El código debe tener 6 caracteres', 'error');
        return false;
    }

    try {
        Swal.fire({
            title: 'Verificando...',
            text: 'Buscando código en el servidor...',
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading()
        });

        console.log(`📡 Enviando validación para código: ${codigo}`);
        
        const res = await fetch(`${API_BASE}/tutores/validar-codigo`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ codigo })
        });
        
        const data = await res.json();
        console.log("Respuesta servidor:", data);
        
        Swal.close();

        if (data.valido) {
            const nombreEl = document.getElementById('preview-nombre-completo'); 
            if (nombreEl) {
                nombreEl.textContent = `${data.preinscripcion.nombres} ${data.preinscripcion.apellidos}`;
            }
            return true;
        } else {
            Swal.fire('Error', data.mensaje || 'Código no válido', 'error');
            return false;
        }
    } catch (error) {
        console.error("Error en fetch:", error);
        Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
        return false;
    }
}

async function handleFinalSubmit(e) {
    e.preventDefault();
    
    if (!validateStepFields(10)) return;

    const confirm = await Swal.fire({
        title: '¿Finalizar Inscripción?',
        text: "Verifique que todos los datos sean correctos.",
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sí, Registrar',
        cancelButtonText: 'Revisar',
        confirmButtonColor: '#10b981'
    });

    if (!confirm.isConfirmed) return;

    const btnSubmit = document.getElementById('btn-finalizar');
    if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    }

    const formData = new FormData(document.getElementById('form-registro'));
    const codigoInput = document.getElementById('codigo-registro');
    if (codigoInput) {
        formData.append('codigo_validado', codigoInput.value.trim().toUpperCase());
    }

    try {
        const res = await fetch(`${API_BASE}/tutores/completar-registro`, {
            method: 'POST',
            body: formData 
        });
        
        const data = await res.json();

        if (res.ok && data.success) {
            await Swal.fire({
                icon: 'success',
                title: '¡Registro Exitoso!',
                text: 'La cuenta ha sido creada. Redirigiendo...',
                confirmButtonColor: '#10b981',
                timer: 3000
            });
            window.location.href = '/login';
        } else {
            throw new Error(data.detail || data.mensaje || 'Error desconocido');
        }

    } catch (error) {
        console.error(error);
        Swal.fire({
            icon: 'error',
            title: 'Error al Guardar',
            text: error.message,
            confirmButtonColor: '#DD8E0A'
        });
        if (btnSubmit) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = '<i class="fas fa-save mr-2"></i> Finalizar Inscripción';
        }
    }
}