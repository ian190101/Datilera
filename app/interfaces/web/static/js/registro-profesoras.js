// app/interfaces/web/static/js/registro-profesoras.js

const API_BASE = '/api/v1';
let currentStep = 1;
const totalSteps = 2;

function initApp() {
    console.log("🚀 JS Registro Profesoras INICIADO");
    initListeners();
    showStep(1);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

function initListeners() {
    // Botón Validar Código (Paso 1)
    const btnValidar = document.getElementById('btn-validar-codigo');
    if (btnValidar) {
        btnValidar.addEventListener('click', async () => {
            const isValid = await validarCodigoBackend();
            if (isValid) {
                currentStep++;
                showStep(currentStep);
            }
        });
    }

    // Botón Anterior
    const btnAnterior = document.getElementById('btn-anterior');
    if (btnAnterior) {
        btnAnterior.addEventListener('click', () => {
            if (currentStep > 1) {
                currentStep--;
                showStep(currentStep);
            }
        });
    }

    // Submit del Formulario (Finalizar)
    const formRegistro = document.getElementById('form-registro-profes');
    if (formRegistro) {
        formRegistro.addEventListener('submit', handleFinalSubmit);
    }
}

function showStep(step) {
    document.querySelectorAll('.step-container').forEach(el => el.classList.remove('active'));
    document.getElementById(`step-${step}`).classList.add('active');
    
    // Indicadores
    document.getElementById('step-indicator').textContent = `Paso ${step} de ${totalSteps}`;
    document.getElementById('step-title').textContent = step === 1 ? "Validación" : "Datos Personales";
    document.getElementById('progress-bar').style.width = `${(step/totalSteps)*100}%`;

    // Botones
    const btnAnterior = document.getElementById('btn-anterior');
    const btnFinalizar = document.getElementById('btn-finalizar');

    if (btnAnterior) btnAnterior.classList.toggle('hidden', step === 1);
    
    // El botón finalizar solo aparece en el último paso
    if (step === totalSteps) {
        btnFinalizar.classList.remove('hidden');
    } else {
        btnFinalizar.classList.add('hidden');
    }
}

async function validarCodigoBackend() {
    const codigoInput = document.getElementById('codigo-registro');
    const codigo = codigoInput.value.trim().toUpperCase();

    if (codigo.length !== 6) {
        Swal.fire({ icon: 'error', title: 'Error', text: 'El código debe tener 6 caracteres', confirmButtonColor: '#DD8E0A' });
        return false;
    }

    try {
        Swal.showLoading();
        const res = await fetch(`${API_BASE}/profesoras/validar-codigo`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ codigo })
        });
        const data = await res.json();
        Swal.close();

        if (data.valido) return true;
        
        Swal.fire({ icon: 'error', title: 'Código Inválido', text: data.mensaje, confirmButtonColor: '#DD8E0A' });
        return false;
    } catch (error) {
        console.error(error);
        Swal.fire({ icon: 'error', title: 'Error de Red', text: 'No se pudo conectar con el servidor', confirmButtonColor: '#DD8E0A' });
        return false;
    }
}

async function handleFinalSubmit(e) {
    e.preventDefault();
    
    // Validar campos vacíos
    const inputs = document.getElementById('step-2').querySelectorAll('input[required]');
    let empty = false;
    inputs.forEach(inp => {
        if(!inp.value.trim()) { inp.classList.add('border-red-500'); empty = true; }
        else { inp.classList.remove('border-red-500'); }
    });
    if(empty) return Swal.fire({ icon: 'warning', text: 'Complete los campos obligatorios', confirmButtonColor: '#DD8E0A' });

    // Validar Contraseñas
    const pass = document.getElementById('password').value;
    const confirm = document.getElementById('password_confirm').value;
    if(pass !== confirm) {
        return Swal.fire({ icon: 'error', title: 'Error', text: 'Las contraseñas no coinciden', confirmButtonColor: '#DD8E0A' });
    }
    if(pass.length < 6) {
        return Swal.fire({ icon: 'warning', title: 'Seguridad', text: 'La contraseña debe tener al menos 6 caracteres', confirmButtonColor: '#DD8E0A' });
    }

    // Enviar
    const btn = document.getElementById('btn-finalizar');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registrando...';

    const formData = new FormData(e.target);
    // Asegurar código
    formData.append('codigo_validado', document.getElementById('codigo-registro').value.trim().toUpperCase());

    try {
        const res = await fetch(`${API_BASE}/profesoras/completar-registro`, {
            method: 'POST',
            body: formData
        });
        const data = await res.json();

        if (res.ok && data.success) {
            await Swal.fire({
                icon: 'success',
                title: '¡Bienvenida!',
                text: 'Cuenta creada correctamente. Redirigiendo...',
                confirmButtonColor: '#10b981',
                timer: 2000
            });
            window.location.href = '/login';
        } else {
            throw new Error(data.detail || data.mensaje || 'Error desconocido');
        }
    } catch (error) {
        Swal.fire({ icon: 'error', title: 'Error', text: error.message, confirmButtonColor: '#DD8E0A' });
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-check-circle mr-2"></i> Finalizar Registro';
    }
}