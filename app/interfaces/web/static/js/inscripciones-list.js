import { fetchAPI, showToast, showConfirm } from './main.js';

const API_BASE = '/api/v1';
let currentPage = 1;
let currentPerPage = 10;

document.addEventListener('DOMContentLoaded', () => {
    loadGrupos();
    loadInscripciones();
    initListeners();
    initModalForms();
});

// --- LISTENERS (CORREGIDOS PARA EVITAR ERROR 422) ---
function initListeners() {
    // Buscador: Usamos () => para evitar pasar el evento 'e' como página
    document.getElementById('search-input')?.addEventListener('input', debounce(() => loadInscripciones(1), 500));

    document.getElementById('form-asignacion')?.addEventListener('submit', guardarAsignacion);
    
    // Filtros
    document.getElementById('filter-estado')?.addEventListener('change', () => loadInscripciones(1));
    document.getElementById('filter-grupo')?.addEventListener('change', () => loadInscripciones(1));
    
    // Paginación por página
    document.getElementById('per-page')?.addEventListener('change', (e) => {
        currentPerPage = parseInt(e.target.value);
        loadInscripciones(1);
    });

    document.getElementById('assign-grupo')?.addEventListener('change', async (e) => {
        const grupoId = e.target.value;
        await cargarParalelosModal(grupoId);
    });

    document.getElementById('form-foto')?.addEventListener('submit', handleUploadFoto);
}

// --- CARGA DE DATOS ---
async function loadInscripciones(page = 1) {
    currentPage = page;
    const tbody = document.getElementById('inscripciones-tbody');
    tbody.innerHTML = '<tr><td colspan="10" class="text-center py-8 text-gray-500 dark:text-gray-400"><i class="fas fa-spinner fa-spin text-2xl"></i><p class="mt-2">Cargando...</p></td></tr>';

    try {
        const params = new URLSearchParams({
            page: page, // Aseguramos que sea número
            per_page: currentPerPage,
            search: document.getElementById('search-input').value,
            estado: document.getElementById('filter-estado').value,
            grupo: document.getElementById('filter-grupo').value
        });
        
        const res = await fetchAPI(`${API_BASE}/inscripciones?${params}`);
        if(!res.ok) throw new Error("Error API");
        const data = await res.json();
        
        renderTable(data.items);
        updateStats(data.stats);
        
        // Renderizar botones de paginación
        renderPagination(data.total, currentPage, currentPerPage);
        
    } catch (error) {
        console.error(error);
        tbody.innerHTML = '<tr><td colspan="10" class="text-center text-red-500 py-8">Error al cargar datos. Intente nuevamente.</td></tr>';
    }
}

// --- PAGINACIÓN (TU CÓDIGO ADAPTADO) ---
function renderPagination(total, page, perPageValue) {
    const totalPages = Math.ceil(total / perPageValue);
    const paginationDiv = document.getElementById('pagination');
    
    if (!paginationDiv) return; // Si no existe el div en el HTML, salir

    let html = '';
    
    // Botón Anterior
    html += `
        <button onclick="changePage(${page - 1})" 
                ${page === 1 ? 'disabled' : ''}
                class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-sm ${page === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100 dark:hover:bg-gray-700'} text-gray-700 dark:text-gray-300 transition-colors">
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    
    const maxVisible = 5;
    let startPage = Math.max(1, page - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <button onclick="changePage(${i})" 
                    class="px-3 py-1 border ${i === page ? 'bg-primary-600 border-primary-600 text-white' : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'} rounded-md text-sm transition-colors">
                ${i}
            </button>
        `;
    }
    
    // Botón Siguiente
    html += `
        <button onclick="changePage(${page + 1})" 
                ${page === totalPages || totalPages === 0 ? 'disabled' : ''}
                class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-sm ${page === totalPages || totalPages === 0 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100 dark:hover:bg-gray-700'} text-gray-700 dark:text-gray-300 transition-colors">
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    paginationDiv.innerHTML = html;
}

// Función global para que el HTML la pueda llamar
window.changePage = function(page) {
    if (page < 1) return;
    loadInscripciones(page);
}

// --- RESTO DE FUNCIONES (RenderTable, Stats, Modales...) ---

function renderTable(items) {
    const tbody = document.getElementById('inscripciones-tbody');
    tbody.innerHTML = '';
    
    if (!items || items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="10" class="text-center py-12 text-gray-500 dark:text-gray-400">No se encontraron registros</td></tr>';
        return;
    }

    items.forEach(item => {
        let badgeClass = 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
        if (item.estado === 'ACTIVO') badgeClass = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
        else if (item.estado === 'PENDIENTE') badgeClass = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
        else if (item.estado === 'INACTIVO') badgeClass = 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';

        const tr = document.createElement('tr');
        tr.className = "hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors border-b border-gray-100 dark:border-gray-700";

        // FOTO Y NOMBRE - Avatar consistente y alineado perfectamente
let avatarHTML = `
    <div class="flex items-center">
        <div class="flex-shrink-0 w-10 h-10 rounded-full overflow-hidden shadow-sm">
            ${item.foto_url 
                ? `<img src="${item.foto_url}?t=${Date.now()}" 
                        alt="${item.nombre_alumno}"
                        class="w-full h-full object-cover">`
                : `<div class="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                    <span class="text-primary-600 dark:text-primary-400 font-semibold text-lg">
                        ${item.nombre_alumno.charAt(0).toUpperCase()}
                    </span>
                </div>`
            }
        </div>
        <div class="ml-3">
            <div class="font-medium text-gray-900 dark:text-white">${item.nombre_alumno}</div>
        </div>
    </div>
`;
        
        // Botón de Asignación (Solo si es ACTIVO)
        let btnAsignar = '';
        if (item.estado === 'ACTIVO') {
            btnAsignar = `
                <button onclick="abrirAsignacion(${item.id}, '${item.nombre_alumno}')" 
                        class="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300" 
                        title="Asignar Grupo/Turno">
                    <i class="fas fa-clipboard-list"></i>
                </button>
            `;
        }
        tr.innerHTML = `
            <td class="px-6 py-4">
                <div class="flex items-center">
                    ${avatarHTML}
                <div>
                
            </td>
            <td class="px-6 py-4 text-xs font-mono text-gray-500 dark:text-gray-400">${item.codigo_inscripcion}</td>
            <td class="px-6 py-4 text-sm font-medium text-blue-600 dark:text-blue-400 whitespace-nowrap">${item.edad_detalle}</td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">${item.grupo}</td>
            <td class="px-6 py-4 text-sm font-bold text-primary-600 dark:text-primary-400">${item.paralelo || '-'}</td>
            <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">${item.turno}</td>
            <td class="px-6 py-4 text-sm">
                <div class="font-medium text-gray-900 dark:text-gray-200">${item.nombre_tutor_1}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">${item.telefono_tutor_1}</div>
            </td>
            <td class="px-6 py-4"><span class="px-2 py-1 rounded-full text-xs font-semibold ${badgeClass}">${item.estado}</span></td>
            <td class="px-6 py-4 text-right space-x-3">
                ${btnAsignar} 
                
                ${item.estado !== 'INACTIVO' ? `<button onclick="desactivarAlumno(${item.id}, '${item.nombre_alumno}')" class="text-red-600 hover:text-red-800 dark:text-red-400" title="Dar de Baja"><i class="fas fa-user-times"></i></button>` : ''}
                <button onclick="abrirSubirFoto(${item.id})" class="p-1 text-purple-600 hover:bg-purple-50 rounded" title="Subir Foto">
                    <i class="fas fa-camera"></i>
                </button>
                <button onclick="verFichaCompleta(${item.id})" class="p-1 text-blue-600 hover:bg-blue-50 rounded" title="Ver File Personal">
                    <i class="fas fa-id-card"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// --- FUNCIONES DE FOTO ---
window.abrirSubirFoto = (id) => {
    document.getElementById('form-foto').reset();
    document.getElementById('foto-alumno-id').value = id;
    document.getElementById('preview-container').classList.remove('hidden');
    document.getElementById('img-preview').classList.add('hidden');
    openModal('modal-foto');
}

window.previewImage = (input) => {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('preview-container').classList.add('hidden');
            const img = document.getElementById('img-preview');
            img.src = e.target.result;
            img.classList.remove('hidden');
        }
        reader.readAsDataURL(input.files[0]);
    }
}

async function handleUploadFoto(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerText = "Subiendo...";
    
    const id = document.getElementById('foto-alumno-id').value;
    const formData = new FormData(e.target);
    
    try {
        const res = await fetchAPI(`${API_BASE}/inscripciones/${id}/foto`, {
            method: 'POST',
            body: formData // No stringify para archivos
        });
        if(res.ok) {
            showToast('Foto actualizada', 'success');
            closeModal('modal-foto');
            loadInscripciones(currentPage);
        } else {
            showToast('Error al subir imagen', 'error');
        }
    } catch(err) { showToast('Error de conexión', 'error'); }
    finally { btn.disabled = false; btn.innerText = "Subir"; }
}

// --- FUNCIÓN FICHA COMPLETA (FILE PERSONAL) ---
window.verFichaCompleta = async (id) => {
    try {
        const res = await fetchAPI(`${API_BASE}/inscripciones/${id}/ficha`);
        if(!res.ok) throw new Error("No se pudo cargar la ficha");
        
        const data = await res.json();
        
        // 1. Datos Alumno
        setText('ficha-nombre', data.alumno.nombre_completo);
        setText('ficha-nacimiento', data.alumno.fecha_nacimiento);
        setText('ficha-edad', data.alumno.edad_texto);
        setText('ficha-meses', data.alumno.edad_meses);
        
        const img = document.getElementById('ficha-foto');
        img.src = data.alumno.foto_url || '/static/img/default-avatar.png'; // Asegúrate de tener un default
        
        // 2. Mamá
        setText('ficha-mama-nombre', data.mama.nombre || '---');
        setText('ficha-mama-ci', data.mama.ci || '---');
        setText('ficha-mama-email', data.mama.email || '---');
        setText('ficha-mama-cel', data.mama.celular || '---');
        setText('ficha-mama-prof', data.mama.profesion || '---');
        setText('ficha-mama-lugar', data.mama.lugar_trabajo || '---');
        setText('ficha-mama-dir', data.mama.direccion_trabajo || '---');

        // 3. Papá
        setText('ficha-papa-nombre', data.papa.nombre || '---');
        setText('ficha-papa-ci', data.papa.ci || '---');
        setText('ficha-papa-email', data.papa.email || '---');
        setText('ficha-papa-cel', data.papa.celular || '---');
        setText('ficha-papa-prof', data.papa.profesion || '---');
        setText('ficha-papa-lugar', data.papa.lugar_trabajo || '---');
        setText('ficha-papa-dir', data.papa.direccion_trabajo || '---');

        // 4. Contactos
        setText('ficha-direccion', data.alumno.direccion || '---');
        setText('ficha-celulares', data.alumno.celulares || '---');
        
        // 5. Emergencia
        setText('ficha-emerg-nombre', data.emergencia.nombre || '---');
        setText('ficha-emerg-paren', data.emergencia.parentesco || '---');
        setText('ficha-emerg-tel', data.emergencia.telefono || '---');

        // 6. Recojo
        setText('ficha-recojo-nombre', data.recojo.nombre || '---');
        setText('ficha-recojo-paren', data.recojo.parentesco || '---');
        setText('ficha-recojo-tel', data.recojo.telefono || '---');

        openModal('modal-ficha');

    } catch(e) {
        showToast('Error cargando ficha técnica', 'error');
        console.error(e);
    }
}

function setText(id, text) {
    const el = document.getElementById(id);
    if(el) el.textContent = text;
}

// --- LÓGICA DE ASIGNACIÓN ---

window.abrirAsignacion = async (id, nombre) => {
    // 1. Resetear Modal
    document.getElementById('form-asignacion').reset();
    document.getElementById('assign-alumno-id').value = id;
    document.getElementById('assign-alumno-nombre').textContent = `Asignando a: ${nombre}`;
    
    // 2. Cargar Selects Maestros (Grupos y Turnos)
    await Promise.all([cargarGruposModal(), cargarTurnosModal()]);
    
    // 3. Cargar Datos Actuales del Alumno
    try {
        const res = await fetchAPI(`${API_BASE}/inscripciones/${id}/asignacion`);
        if (res.ok) {
            const data = await res.json();
            
            // Pre-seleccionar
            if (data.grupo_id) {
                document.getElementById('assign-grupo').value = data.grupo_id;
                // Cargar paralelos del grupo seleccionado
                await cargarParalelosModal(data.grupo_id);
                // Seleccionar paralelo si existe
                if (data.paralelo_id) {
                    document.getElementById('assign-paralelo').value = data.paralelo_id;
                }
            }
            if (data.turno_id) {
                document.getElementById('assign-turno').value = data.turno_id;
            }
        }
    } catch (e) { console.error("Error cargando asignacion actual", e); }

    // 4. Mostrar
    openModal('modal-asignacion');
};

async function cargarGruposModal() {
    const select = document.getElementById('assign-grupo');
    if (!select.options.length || select.options.length <= 1) { // Evitar recargar si ya tiene datos
        try {
            const res = await fetchAPI(`${API_BASE}/grupos`);
            const data = await res.json();
            select.innerHTML = '<option value="">Seleccione grupo...</option>' + 
                data.items.map(g => `<option value="${g.id}">${g.nombre}</option>`).join('');
        } catch(e) {}
    }
}

async function cargarTurnosModal() {
    const select = document.getElementById('assign-turno');
    if (!select.options.length || select.options.length <= 1) {
        try {
            const res = await fetchAPI(`${API_BASE}/turnos`);
            const data = await res.json();
            select.innerHTML = '<option value="">Seleccione turno...</option>' + 
                data.items.map(t => `<option value="${t.id}">${t.nombre} (${t.hora_inicio}-${t.hora_fin})</option>`).join('');
        } catch(e) {}
    }
}

async function cargarParalelosModal(grupoId) {
    const select = document.getElementById('assign-paralelo');
    
    // Estado de carga visual
    select.innerHTML = '<option value="">Cargando aulas...</option>';
    select.disabled = true;
    select.classList.add('cursor-not-allowed', 'opacity-60');

    if (!grupoId) {
        select.innerHTML = '<option value="">Primero seleccione un grupo</option>';
        return;
    }

    try {
        // SOLUCIÓN EFICIENTE: Pedimos al backend solo los paralelos de ESTE grupo
        const res = await fetchAPI(`${API_BASE}/paralelos?grupo_id=${grupoId}&per_page=100`); 
        const data = await res.json();
        
        if (data.items && data.items.length > 0) {
            // Renderizado directo (ya vienen filtrados desde la BD)
            select.innerHTML = '<option value="">Seleccione paralelo...</option>' + 
                data.items.map(p => `<option value="${p.id}">${p.letra} (Cupos: ${p.capacidad})</option>`).join('');
            
            // Habilitar select
            select.disabled = false;
            select.classList.remove('cursor-not-allowed', 'opacity-60');
        } else {
            select.innerHTML = '<option value="">Este grupo no tiene paralelos creados</option>';
        }

    } catch(e) {
        console.error(e);
        select.innerHTML = '<option value="">Error al cargar datos</option>';
    }
}

async function guardarAsignacion(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';

    const alumnoId = document.getElementById('assign-alumno-id').value;
    const formData = new FormData(e.target);
    
    try {
        const res = await fetchAPI(`${API_BASE}/inscripciones/${alumnoId}/asignacion`, {
            method: 'POST',
            body: JSON.stringify(Object.fromEntries(formData))
        });
        
        if (res.ok) {
            showToast('Asignación guardada correctamente', 'success');
            closeModal('modal-asignacion');
            loadInscripciones(currentPage); // Recargar tabla
        } else {
            showToast('Error al guardar asignación', 'error');
        }
    } catch(err) { showToast('Error de conexión', 'error'); } 
    finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
    }
}

function updateStats(stats) {
    if(stats) {
        document.getElementById('total-count').textContent = stats.total;
        document.getElementById('activos-count').textContent = stats.activos;
        document.getElementById('pendientes-count').textContent = stats.pendientes;
    }
}

// Cargar select de Grupos
async function loadGrupos() {
    try {
        const res = await fetchAPI(`${API_BASE}/grupos`);
        const data = await res.json();
        const filterSelect = document.getElementById('filter-grupo');
        const modalSelect = document.getElementById('select-grupo-modal');
        
        if (data.items) {
            if (filterSelect) filterSelect.innerHTML = '<option value="">Todos</option>';
            if (modalSelect) modalSelect.innerHTML = '<option value="">Seleccione...</option>';

            data.items.forEach(g => {
                const opt = `<option value="${g.id}">${g.nombre}</option>`;
                if (filterSelect) filterSelect.insertAdjacentHTML('beforeend', opt);
                if (modalSelect) modalSelect.insertAdjacentHTML('beforeend', opt);
            });
        }
    } catch(e) { console.error(e); }
}

// MODALES Y FORMS
window.openModal = (id) => document.getElementById(id).classList.remove('hidden');
window.closeModal = (id) => document.getElementById(id).classList.add('hidden');

function initModalForms() {
    const setupForm = (id, endpoint, modal, msg) => {
        document.getElementById(id)?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleFormSubmit(e.target, endpoint, modal, msg);
            if (id === 'form-grupo') loadGrupos();
        });
    };
    setupForm('form-grupo', '/grupos', 'modal-grupo', 'Grupo creado exitosamente');
    setupForm('form-paralelo', '/paralelos', 'modal-paralelo', 'Paralelo creado exitosamente');
    setupForm('form-turno', '/turnos', 'modal-turno', 'Turno creado exitosamente');
    setupForm('form-horario', '/horarios', 'modal-horario', 'Horario creado exitosamente');
}

async function handleFormSubmit(form, endpoint, modalId, successMsg) {
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const res = await fetchAPI(`${API_BASE}${endpoint}`, {
            method: 'POST', body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Error al guardar');
        showToast(successMsg, 'success');
        closeModal(modalId);
        form.reset();
        // Recargar datos si estamos en la vista de inscripciones podría ser opcional
        // pero idealmente refrescas la vista actual
    } catch (error) { showToast(error.message, 'error'); } 
    finally { btn.disabled = false; btn.innerHTML = originalText; }
}

// Helpers globales
window.desactivarAlumno = async (id, nombre) => {
    const confirm = await showConfirm('¿Baja?', `Desactivar a ${nombre}`, 'Sí');
    if (confirm.isConfirmed) {
        await fetchAPI(`${API_BASE}/inscripciones/${id}/desactivar`, { method: 'PATCH' });
        loadInscripciones(currentPage);
    }
};
window.exportarExcel = () => window.location.href = `${API_BASE}/exportaciones/inscripciones/excel`;
window.exportarPDF = () => window.open(`${API_BASE}/exportaciones/inscripciones/pdf`, '_blank');
window.resetFilters = () => {
    document.getElementById('search-input').value = '';
    document.getElementById('filter-estado').value = '';
    document.getElementById('filter-grupo').value = '';
    loadInscripciones(1);
};
window.verDetalle = (id) => showToast('Detalle próximamente', 'info');

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}


window.imprimirFichaDetalle = function() {
    // Helper seguro: si el ID no existe, devuelve vacío en lugar de error
    const getTextSafe = (id) => {
        const el = document.getElementById(id);
        return el ? el.innerText : '';
    };

    // 1. Obtener datos (Usando los IDs reales de tu HTML)
    const nombre = getTextSafe('ficha-nombre');
    // const codigo = getTextSafe('ficha-codigo'); // ELIMINADO: No existe en el HTML
    const edad = getTextSafe('ficha-edad');
    const meses = getTextSafe('ficha-meses'); 
    const nac = getTextSafe('ficha-nacimiento'); // CORREGIDO: coincide con tu HTML
    
    // Foto
    const imgEl = document.getElementById('ficha-foto');
    const foto = imgEl ? imgEl.src : '/static/img/default-avatar.png';
    
    // Datos de contacto
    const mamaNombre = getTextSafe('ficha-mama-nombre');
    const mamaCel = getTextSafe('ficha-mama-cel');
    const papaNombre = getTextSafe('ficha-papa-nombre');
    const papaCel = getTextSafe('ficha-papa-cel');
    
    // Emergencia y Recojo
    const emergNombre = getTextSafe('ficha-emerg-nombre');
    const emergTel = getTextSafe('ficha-emerg-tel');
    const recojoNombre = getTextSafe('ficha-recojo-nombre');
    const recojoTel = getTextSafe('ficha-recojo-tel');

    // 2. Crear ventana nueva
    const printWindow = window.open('', '', 'height=800,width=900');
    
    // 3. Escribir documento
    printWindow.document.write(`
        <html>
        <head>
            <title>Ficha - ${nombre}</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; padding: 40px; color: #333; max-width: 800px; margin: 0 auto; }
                .header { display: flex; align-items: center; border-bottom: 2px solid #DD8E0A; padding-bottom: 20px; margin-bottom: 30px; }
                .foto { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 4px solid #f3f4f6; margin-right: 25px; }
                .titulo h1 { margin: 0; font-size: 24px; color: #111827; text-transform: uppercase; }
                .titulo p { margin: 5px 0 0; color: #6b7280; font-size: 14px; }
                
                .section { margin-bottom: 30px; break-inside: avoid; }
                .section-title { 
                    font-size: 14px; font-weight: bold; text-transform: uppercase; 
                    letter-spacing: 1px; color: #DD8E0A; border-bottom: 1px solid #e5e7eb; 
                    padding-bottom: 5px; margin-bottom: 15px; 
                }
                
                .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
                .field { margin-bottom: 5px; }
                .label { font-weight: 700; font-size: 11px; color: #6b7280; display: block; text-transform: uppercase; margin-bottom: 2px; }
                .value { font-size: 14px; color: #1f2937; font-weight: 500; }
                
                .contacts-table { width: 100%; border-collapse: collapse; font-size: 13px; }
                .contacts-table th { text-align: left; background: #f9fafb; padding: 8px; border-bottom: 2px solid #e5e7eb; color: #374151; font-size: 11px; text-transform: uppercase; }
                .contacts-table td { padding: 8px; border-bottom: 1px solid #e5e7eb; }
                
                .footer { margin-top: 50px; text-align: center; font-size: 11px; color: #9ca3af; border-top: 1px solid #e5e7eb; padding-top: 20px; }
                
                @media print {
                    body { -webkit-print-color-adjust: exact; padding: 20px; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <img src="${foto}" class="foto" onerror="this.style.display='none'">
                <div class="titulo">
                    <h1>${nombre}</h1>
                    <p>Edad: ${edad} (${meses} meses)</p>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Información Personal</div>
                <div class="grid">
                    <div class="field">
                        <span class="label">Fecha de Nacimiento</span>
                        <span class="value">${nac}</span>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Padres / Tutores</div>
                <div class="grid">
                    <div class="field">
                        <span class="label">Madre / Tutor 1</span>
                        <span class="value">${mamaNombre || '-'} <br> ${mamaCel ? '📞 ' + mamaCel : ''}</span>
                    </div>
                    <div class="field">
                        <span class="label">Padre / Tutor 2</span>
                        <span class="value">${papaNombre || '-'} <br> ${papaCel ? '📞 ' + papaCel : ''}</span>
                    </div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Contactos de Emergencia & Recojo</div>
                <table class="contacts-table">
                    <thead>
                        <tr>
                            <th>Tipo</th>
                            <th>Nombre</th>
                            <th>Teléfono</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Emergencia</strong></td>
                            <td>${emergNombre}</td>
                            <td>${emergTel}</td>
                        </tr>
                        <tr>
                            <td><strong>Autorizado Recojo</strong></td>
                            <td>${recojoNombre}</td>
                            <td>${recojoTel}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="footer">
                Documento generado el ${new Date().toLocaleDateString()} a las ${new Date().toLocaleTimeString()}
            </div>
        </body>
        </html>
    `);
    
    printWindow.document.close();
    
    printWindow.onload = function() {
        printWindow.focus();
        // Pequeño delay para asegurar que la imagen (si hay) cargue
        setTimeout(() => {
            printWindow.print();
            printWindow.close();
        }, 500);
    };
};