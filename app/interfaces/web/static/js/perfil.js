import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    // Listener para subir foto automáticamente al seleccionar archivo
    const inputFoto = document.getElementById('input-foto');
    if (inputFoto) {
        inputFoto.addEventListener('change', handleFotoUpload);
    }

    // Listener para formulario de contraseña
    const formPass = document.getElementById('form-password');
    if (formPass) {
        formPass.addEventListener('submit', handlePasswordUpdate);
    }
});

/* ============================
   CAMBIO DE FOTO
   ============================ */
async function handleFotoUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    // Validar tipo
    if (!file.type.startsWith('image/')) {
        showToast('Por favor selecciona un archivo de imagen', 'warning');
        return;
    }

    // Previsualización inmediata (Optimista)
    const reader = new FileReader();
    reader.onload = (event) => {
        const img = document.getElementById('img-perfil-preview');
        const avatarDiv = document.getElementById('avatar-iniciales');
        
        if (img) {
            img.src = event.target.result;
            img.classList.remove('hidden');
        }
        if (avatarDiv) {
            avatarDiv.classList.add('hidden'); // Ocultar iniciales
        }
    };
    reader.readAsDataURL(file);

    // Subir al servidor
    const formData = new FormData();
    formData.append('file', file);

    try {
        showToast('Subiendo foto...', 'info');
        const res = await fetchAPI(`${API_BASE}/perfil/foto`, {
            method: 'POST',
            body: formData // fetchAPI maneja el Content-Type para FormData
        });

        const data = await res.json();

        /* ... dentro de handleFotoUpload ... */

        if (res.ok) {
            showToast('Foto de perfil actualizada', 'success');
            
            // --- ACTUALIZACIÓN EN TIEMPO REAL DEL HEADER ---
            const headerImg = document.getElementById('header-avatar-img');
            const headerInitials = document.getElementById('header-avatar-initials');

            if (headerImg) {
                // Actualizar fuente y mostrar imagen
                // Agregamos timestamp para evitar caché del navegador
                headerImg.src = `${data.foto_url}?t=${new Date().getTime()}`;
                headerImg.classList.remove('hidden');
            }
            
            if (headerInitials) {
                // Ocultar las iniciales
                headerInitials.classList.add('hidden');
            }
            // -----------------------------------------------
            
        } else {
            throw new Error(data.detail || 'Error al subir imagen');
        }

/* ... resto del código ... */
    } catch (error) {
        console.error(error);
        showToast(error.message, 'error');
        // Revertir previsualización si falla (opcional)
        setTimeout(() => location.reload(), 2000);
    }
}

/* ============================
   CAMBIO DE CONTRASEÑA
   ============================ */
async function handlePasswordUpdate(e) {
    e.preventDefault();
    
    const actual = document.getElementById('pass-actual').value;
    const nueva = document.getElementById('pass-nueva').value;
    const confirm = document.getElementById('pass-confirm').value;

    if (nueva !== confirm) {
        showToast('Las contraseñas nuevas no coinciden', 'error');
        return;
    }

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';

    try {
        const res = await fetchAPI(`${API_BASE}/perfil/password`, {
            method: 'POST',
            body: JSON.stringify({
                password_actual: actual,
                password_nueva: nueva
            })
        });

        const data = await res.json();

        if (res.ok) {
            showToast('Contraseña actualizada exitosamente', 'success');
            e.target.reset();
        } else {
            throw new Error(data.detail || 'Error al actualizar contraseña');
        }
    } catch (error) {
        console.error(error);
        showToast(error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
}