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
    document.getElementById('form-preinscribir-hermano')?.addEventListener('submit', guardarPreinscripcionHermano);
    
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
                ${item.estado !== 'INACTIVO' && item.tiene_tutor_con_cuenta ? `<button onclick="abrirPreinscribirHermano(${item.id}, '${encodeURIComponent(item.nombre_alumno)}', '${encodeURIComponent(item.nombre_tutor_1)}')" class="p-1 text-primary-600 hover:bg-primary-50 rounded dark:text-primary-400 dark:hover:bg-primary-900/20" title="Preinscribir hermano" aria-label="Preinscribir hermano"><i class="fas fa-children"></i></button>` : ''}
                
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

// --- FICHA PERSONAL MULTIPÁGINA ---
// El modal y la impresión comparten este único árbol DOM. No se interpolan
// valores sin escapar y las URL solo admiten HTTP(S) o rutas locales absolutas.
function escapeFichaHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

function safeFichaUrl(value, fallback = '') {
    const raw = String(value ?? '').trim();
    if (!raw) return fallback;
    if (raw.startsWith('/') && !raw.startsWith('//')) return raw;
    try {
        const url = new URL(raw);
        return (url.protocol === 'http:' || url.protocol === 'https:') ? url.href : fallback;
    } catch (_) {
        return fallback;
    }
}

function fichaValue(data, ...paths) {
    for (const path of paths) {
        const value = path.split('.').reduce((current, key) => current?.[key], data);
        if (value !== undefined && value !== null && value !== '') return value;
    }
    return null;
}

function fichaDisplay(value, suffix = '') {
    if (value === undefined || value === null || value === '') return 'No registrado';
    if (typeof value === 'boolean') return value ? 'Sí' : 'No';
    if (Array.isArray(value)) {
        const items = value.filter(item => item !== undefined && item !== null && item !== '');
        return items.length ? items.join(', ') : 'No registrado';
    }
    return `${value}${suffix}`;
}

function fichaField(label, value, options = {}) {
    const className = options.wide ? 'ficha-field ficha-field-wide' : 'ficha-field';
    return `<div class="${className}">
        <div class="ficha-field-label">${escapeFichaHtml(label)}</div>
        <div class="ficha-field-value">${escapeFichaHtml(fichaDisplay(value, options.suffix || ''))}</div>
    </div>`;
}

function fichaSection(title, content, extraClass = '') {
    return `<section class="ficha-section ${escapeFichaHtml(extraClass)}">
        <h2 class="ficha-section-title">${escapeFichaHtml(title)}</h2>
        <div class="ficha-grid">${content}</div>
    </section>`;
}

function fichaHeader(data, pageNumber, totalPages) {
    const alumno = data.alumno || {};
    const photo = safeFichaUrl(
        fichaValue(data, 'alumno.foto_url', 'foto_url'),
        '/static/img/logo.png'
    );
    const name = fichaValue(data, 'alumno.nombre_completo', 'alumno.nombres_completos', 'nombre_completo') || 'Estudiante';

    const code = fichaValue(data, 'alumno.codigo_unico', 'alumno.codigo') || '';
    return `<header class="ficha-page-header">
        <div class="ficha-page-logo">
            <img src="/static/img/logo.png" alt="Logo Datilera">
        </div>
        <div class="ficha-page-heading">
            <h1 class="ficha-page-title">File personal</h1>
            <p class="ficha-page-subtitle">Centro Infantil de Desarrollo Integral</p>
            <strong class="ficha-student-name">${escapeFichaHtml(name)}</strong>
        </div>
        <div class="ficha-page-meta">
            <img class="ficha-student-photo" src="${escapeFichaHtml(photo)}" alt="Foto del estudiante">
            <span class="ficha-page-number">Página ${pageNumber} de ${totalPages}</span>
            <span>${escapeFichaHtml(code)}</span>
        </div>
    </header>`;
}

function fichaPage(data, pageNumber, totalPages, body) {
    return `<article class="ficha-page" data-page="${pageNumber}">
        ${fichaHeader(data, pageNumber, totalPages)}
        <div class="ficha-page-body">${body}</div>
        <footer class="ficha-page-footer"><span>Datilera · File personal del alumno</span><span>Página ${pageNumber} de ${totalPages}</span></footer>
    </article>`;
}

function normalizeFichaTutores(data) {
    let tutores = Array.isArray(data.tutores) ? data.tutores : [];
    if (!tutores.length) tutores = [data.mama, data.papa].filter(Boolean);
    return tutores;
}

function renderFichaTutor(tutor, index) {
    const ci = tutor.ci || [tutor.ci_numero, tutor.ci_complemento, tutor.ci_expedido].filter(Boolean).join(' ');
    const title = tutor.tipo_relacion || tutor.relacion || (index === 0 ? 'Tutor principal' : `Tutor ${index + 1}`);
    const fields = [
            fichaField('Nombre completo', tutor.nombre || tutor.nombre_completo || [tutor.nombres, tutor.apellidos].filter(Boolean).join(' '), { wide: true }),
            fichaField('Relación', title),
            fichaField('C.I.', ci),
            fichaField('Celular', tutor.celular),
            fichaField('Celular alternativo', tutor.celular_alternativo),
            fichaField('Correo electrónico', tutor.email),
            fichaField('Dirección', tutor.direccion),
            fichaField('Profesión', tutor.profesion),
            fichaField('Lugar de trabajo', tutor.lugar_trabajo),
            fichaField('Dirección de trabajo', tutor.direccion_trabajo),
            fichaField('Teléfono de trabajo', tutor.telefono_trabajo),
            fichaField('Tutor principal', tutor.es_principal),
            fichaField('Tiene custodia', tutor.tiene_custodia),
            fichaField('Recibe notificaciones', tutor.recibe_notificaciones),
            fichaField('Autorizado para retirar', tutor.autorizado_retirar)
    ].join('');
    return `<div class="ficha-subsection ficha-field-wide"><h3>${escapeFichaHtml(title)}</h3><div class="ficha-grid">${fields}</div></div>`;
}

function renderFichaTutores(data) {
    const tutores = normalizeFichaTutores(data);
    if (!tutores.length) return '<p class="ficha-empty">No se registraron padres o tutores.</p>';
    return tutores.map(renderFichaTutor).join('');
}

function renderFichaDocument(data) {
    const target = document.getElementById('ficha-document');
    if (!target) throw new Error('No existe el contenedor #ficha-document');

    const a = data.alumno || {};
    const nacimiento = data.nacimiento || {};
    const salud = data.salud || {};
    const sueno = data.sueno || data['sueño'] || {};
    const alimentacion = data.alimentacion || {};
    const desarrollo = data.desarrollo || {};
    const social = data.social_familiar || data.social || {};
    const emergencia = data.emergencia || {};
    const recojo = data.recojo || {};
    const documentos = data.documentos || {};

    const page1 = [
        fichaSection('Datos del estudiante', [
            fichaField('Nombre completo', fichaValue(data, 'alumno.nombre_completo', 'alumno.nombres_completos'), { wide: true }),
            fichaField('Código', fichaValue(data, 'alumno.codigo_unico', 'alumno.codigo')),
            fichaField('C.I.', fichaValue(data, 'alumno.ci', 'alumno.ci_numero')),
            fichaField('Fecha de nacimiento', a.fecha_nacimiento),
            fichaField('Edad', a.edad_texto),
            fichaField('Edad en meses', a.edad_meses),
            fichaField('Lugar de nacimiento', a.lugar_nacimiento),
            fichaField('Género', a.genero),
            fichaField('Dirección domiciliaria', a.direccion || a.direccion_domicilio, { wide: true }),
            fichaField('Seguro médico / aseguradora', fichaValue(data, 'alumno.aseguradora', 'salud.aseguradora')),
            fichaField('Carnet de asegurado', fichaValue(data, 'alumno.carnet_asegurado', 'salud.carnet_asegurado')),
            fichaField('Estado de inscripción', a.estado),
            fichaField('Fecha de inscripción', a.fecha_inscripcion)
        ].join(''))
    ].join('');

    const tutorPages = normalizeFichaTutores(data).map((tutor, index) =>
        fichaSection(`Padre, madre o tutor ${index + 1}`, renderFichaTutor(tutor, index))
    );
    if (!tutorPages.length) tutorPages.push(fichaSection('Padres y tutores', renderFichaTutores(data)));

    const page2 = [
        fichaSection('Contactos y autorizaciones', [
            fichaField('Contacto de emergencia', emergencia.nombre || a.contacto_emergencia_nombre, { wide: true }),
            fichaField('Parentesco', emergencia.parentesco),
            fichaField('Teléfono de emergencia', emergencia.telefono || a.contacto_emergencia_telefono),
            fichaField('Familiares autorizados a recoger', recojo.nombre || recojo.detalle || a.familiares_autorizados_recogo, { wide: true }),
            fichaField('Parentesco / detalle de recojo', recojo.parentesco, { wide: true }),
            fichaField('Teléfono de recojo', recojo.telefono)
        ].join(''))
    ].join('');

    const page3 = [
        fichaSection('Historia de nacimiento', [
            fichaField('Embarazo normal', fichaValue(data, 'nacimiento.embarazo_normal', 'alumno.embarazo_normal')),
            fichaField('Complicaciones del embarazo', fichaValue(data, 'nacimiento.embarazo_complicaciones', 'alumno.embarazo_complicaciones'), { wide: true }),
            fichaField('Parto normal', fichaValue(data, 'nacimiento.parto_normal', 'alumno.parto_normal')),
            fichaField('Complicaciones del parto', fichaValue(data, 'nacimiento.parto_complicaciones', 'alumno.parto_complicaciones'), { wide: true }),
            fichaField('Peso al nacer', fichaValue(data, 'nacimiento.peso_nacer', 'alumno.peso_nacer'), { suffix: ' kg' }),
            fichaField('Talla al nacer', fichaValue(data, 'nacimiento.talla_nacer', 'alumno.talla_nacer'), { suffix: ' cm' })
        ].join('')),
        fichaSection('Salud y antecedentes', [
            fichaField('Enfermedades previas', fichaValue(data, 'salud.enfermedades_previas', 'alumno.enfermedades_previas'), { wide: true }),
            fichaField('Problemas de salud', fichaValue(data, 'salud.problemas_salud', 'alumno.problemas_salud'), { wide: true }),
            fichaField('Tiene alergias', fichaValue(data, 'salud.tiene_alergias', 'alumno.tiene_alergias')),
            fichaField('Detalle de alergias', fichaValue(data, 'salud.alergias_detalle', 'alumno.alergias_detalle'), { wide: true }),
            fichaField('Medicación actual', fichaValue(data, 'salud.medicacion_actual', 'alumno.medicacion_actual'), { wide: true }),
            fichaField('Tratamiento actual', fichaValue(data, 'salud.tratamiento_actual', 'alumno.tratamiento_actual'), { wide: true }),
            fichaField('Traumatismos o caídas', fichaValue(data, 'salud.traumatismos_caidas', 'alumno.traumatismos_caidas'), { wide: true })
        ].join(''))
    ].join('');

    const page4 = [
        fichaSection('Sueño y descanso', [
            fichaField('Horario nocturno', fichaValue(data, 'sueno.horario_nocturno', 'sueno.horario_sueno_nocturno', 'alumno.horario_sueno_nocturno')),
            fichaField('Horario diurno', fichaValue(data, 'sueno.horario_diurno', 'sueno.horario_sueno_diurno', 'alumno.horario_sueno_diurno')),
            fichaField('Lugar donde duerme', fichaValue(data, 'sueno.lugar_sueno', 'alumno.lugar_sueno')),
            fichaField('Duerme con', fichaValue(data, 'sueno.duerme_con', 'alumno.duerme_con')),
            fichaField('De bebé dormía con / hasta qué edad', fichaValue(data, 'sueno.co_sleeping_bebe_edad', 'alumno.co_sleeping_bebe_edad'), { wide: true }),
            fichaField('Usa chupete', fichaValue(data, 'sueno.usa_chupete', 'alumno.usa_chupete')),
            fichaField('Postura al dormir', fichaValue(data, 'sueno.postura_sueno', 'alumno.postura_sueno')),
            fichaField('Cómo se duerme', fichaValue(data, 'sueno.se_duerme_como', 'alumno.se_duerme_como')),
            fichaField('Pesadillas / frecuencia', fichaValue(data, 'sueno.pesadillas_frecuencia', 'alumno.pesadillas_frecuencia')),
            fichaField('Problemas de sueño', fichaValue(data, 'sueno.problemas_sueno', 'alumno.problemas_sueno'), { wide: true }),
            fichaField('Momento de los problemas de sueño', fichaValue(data, 'sueno.momento_problemas_sueno', 'alumno.momento_problemas_sueno')),
            fichaField('Respuesta familiar ante problemas', fichaValue(data, 'sueno.respuesta_problemas_sueno', 'alumno.respuesta_problemas_sueno'), { wide: true }),
            fichaField('Otros hábitos de sueño', fichaValue(data, 'sueno.otros_habitos_sueno', 'alumno.otros_habitos_sueno'), { wide: true })
        ].join(''))
    ].join('');

    const page5 = [
        fichaSection('Alimentación', [
            fichaField('Lactancia materna', fichaValue(data, 'alimentacion.lactancia_materna_meses', 'alumno.lactancia_materna_meses'), { suffix: ' meses' }),
            fichaField('Uso de biberón desde', fichaValue(data, 'alimentacion.uso_biberon_desde_meses', 'alumno.uso_biberon_desde_meses'), { suffix: ' meses' }),
            fichaField('Dieta actual', fichaValue(data, 'alimentacion.dieta_actual', 'alumno.dieta_actual'), { wide: true }),
            fichaField('Alimentos en puré', fichaValue(data, 'alimentacion.alimentos_en_pure', 'alumno.alimentos_en_pure')),
            fichaField('Problemas de succión o masticación', fichaValue(data, 'alimentacion.problemas_succion_masticacion', 'alumno.problemas_succion_masticacion'), { wide: true }),
            fichaField('Transición a alimentos sólidos', fichaValue(data, 'alimentacion.transicion_alimentacion_solida', 'alumno.transicion_alimentacion_solida'), { wide: true }),
            fichaField('Intolerancias alimenticias', fichaValue(data, 'alimentacion.intolerancias_alimenticias', 'alumno.intolerancias_alimenticias')),
            fichaField('Alimentos que rechaza', fichaValue(data, 'alimentacion.alimentos_rechaza', 'alumno.alimentos_rechaza')),
            fichaField('Alimentos que prefiere', fichaValue(data, 'alimentacion.alimentos_prefiere', 'alumno.alimentos_prefiere')),
            fichaField('Problemas de alimentación', fichaValue(data, 'alimentacion.problemas_alimentacion', 'alumno.problemas_alimentacion'), { wide: true }),
            fichaField('Respuesta familiar ante problemas', fichaValue(data, 'alimentacion.respuesta_problemas_comer', 'alumno.respuesta_problemas_comer'), { wide: true })
        ].join(''))
    ].join('');

    const page6 = [
        fichaSection('Desarrollo evolutivo', [
            fichaField('Controló la cabeza', fichaValue(data, 'desarrollo.edad_control_cabeza_meses', 'alumno.edad_control_cabeza_meses'), { suffix: ' meses' }),
            fichaField('Se sentó sin ayuda', fichaValue(data, 'desarrollo.edad_sentarse_meses', 'alumno.edad_sentarse_meses'), { suffix: ' meses' }),
            fichaField('Gateó', fichaValue(data, 'desarrollo.edad_gatear_meses', 'alumno.edad_gatear_meses'), { suffix: ' meses' }),
            fichaField('Se levantó / sostuvo', fichaValue(data, 'desarrollo.edad_levantarse_meses', 'alumno.edad_levantarse_meses'), { suffix: ' meses' }),
            fichaField('Caminó', fichaValue(data, 'desarrollo.edad_caminar_meses', 'alumno.edad_caminar_meses'), { suffix: ' meses' }),
            fichaField('Balbuceó', fichaValue(data, 'desarrollo.edad_balbuceo_meses', 'alumno.edad_balbuceo_meses'), { suffix: ' meses' }),
            fichaField('Primeras palabras', fichaValue(data, 'desarrollo.edad_primeras_palabras_meses', 'alumno.edad_primeras_palabras_meses'), { suffix: ' meses' }),
            fichaField('Primeros dientes', fichaValue(data, 'desarrollo.edad_primeros_dientes_meses', 'alumno.edad_primeros_dientes_meses'), { suffix: ' meses' }),
            fichaField('Problemas de marcha', fichaValue(data, 'desarrollo.problemas_marcha', 'alumno.problemas_marcha'), { wide: true }),
            fichaField('Síntomas de dentición', fichaValue(data, 'desarrollo.sintomas_denticion', 'alumno.sintomas_denticion'), { wide: true })
        ].join(''))
    ].join('');

    const page7 = [
        fichaSection('Área social y familiar', [
            fichaField('Quién le atiende habitualmente', fichaValue(data, 'social_familiar.quien_atiende', 'social.quien_atiende', 'alumno.quien_atiende')),
            fichaField('Personas que viven en casa', fichaValue(data, 'social_familiar.familiares_en_casa', 'social.familiares_en_casa', 'alumno.familiares_en_casa'), { wide: true }),
            fichaField('Familiar con mayor apego', fichaValue(data, 'social_familiar.familiar_mas_apego', 'social.familiar_mas_apego', 'alumno.familiar_mas_apego')),
            fichaField('Objeto afectivo', fichaValue(data, 'social_familiar.objeto_afectivo', 'social.objeto_afectivo', 'alumno.objeto_afectivo')),
            fichaField('Actividades con los padres', fichaValue(data, 'social_familiar.actividades_con_padres', 'social.actividades_con_padres', 'alumno.actividades_con_padres'), { wide: true }),
            fichaField('Sentimientos más expresados', fichaValue(data, 'social_familiar.sentimientos_mas_expresados', 'social.sentimientos_mas_expresados', 'alumno.sentimientos_mas_expresados'), { wide: true }),
            fichaField('Llora habitualmente', fichaValue(data, 'social_familiar.llora_habitualmente', 'social.llora_habitualmente', 'alumno.llora_habitualmente')),
            fichaField('Circunstancias del llanto', fichaValue(data, 'social_familiar.circunstancias_llanto', 'social.circunstancias_llanto', 'alumno.circunstancias_llanto'), { wide: true }),
            fichaField('Con quién juega', fichaValue(data, 'social_familiar.con_quien_juega', 'social.con_quien_juega', 'alumno.con_quien_juega')),
            fichaField('Juguetes preferidos', fichaValue(data, 'social_familiar.juguetes_preferidos', 'social.juguetes_preferidos', 'alumno.juguetes_preferidos')),
            fichaField('Relación con desconocidos', fichaValue(data, 'social_familiar.relacion_con_desconocidos', 'social.relacion_con_desconocidos', 'alumno.relacion_con_desconocidos'), { wide: true })
        ].join(''))
    ].join('');

    const documentRows = Object.entries(documentos).map(([key, documentValue]) => {
        const label = key.replaceAll('_', ' ').replace(/\b\w/g, letter => letter.toUpperCase());
        const isDocumentObject = documentValue !== null && typeof documentValue === 'object';
        const rawUrl = isDocumentObject ? (documentValue.url || documentValue.ruta) : documentValue;
        const url = safeFichaUrl(rawUrl);
        const status = isDocumentObject ? (documentValue.estado || (url ? 'Adjunto' : null)) : (url ? 'Adjunto' : documentValue);
        if (url) {
            return `<div class="ficha-field">
                <div class="ficha-field-label">${escapeFichaHtml(label)}</div>
                <div class="ficha-field-value"><a class="ficha-document-link" href="${escapeFichaHtml(url)}" target="_blank" rel="noopener noreferrer">Documento adjunto</a></div>
            </div>`;
        }
        return fichaField(label, status || 'No adjunto');
    }).join('');

    const page8 = [
        fichaSection('Documentación presentada', documentRows || [
            fichaField('Certificado de nacimiento', a.certificado_nacimiento_url ? 'Adjunto' : 'No adjunto'),
            fichaField('Libreta de vacunas', a.libreta_vacunas_url ? 'Adjunta' : 'No adjunta')
        ].join('')),
        fichaSection('Observaciones administrativas', [
            fichaField('Fecha de primera asistencia', a.fecha_primera_asistencia),
            fichaField('Fecha de baja', a.fecha_baja),
            fichaField('Motivo de baja', a.motivo_baja, { wide: true })
        ].join('')),
        '<p class="ficha-security-note">Por seguridad, este documento no muestra contraseñas ni credenciales de acceso.</p>'
    ].join('');

    const pages = [page1, ...tutorPages, page2, page3, page4, page5, page6, page7, page8];
    target.innerHTML = pages.map((body, index) => fichaPage(data, index + 1, pages.length, body)).join('');
}

window.verFichaCompleta = async (id) => {
    const target = document.getElementById('ficha-document');
    if (target) target.innerHTML = '<div class="ficha-loading"><i class="fas fa-spinner fa-spin"></i> Cargando ficha completa...</div>';
    openModal('modal-ficha');

    try {
        const res = await fetchAPI(`${API_BASE}/inscripciones/${id}/ficha`);
        if (!res.ok) throw new Error('No se pudo cargar la ficha');
        renderFichaDocument(await res.json());
    } catch (error) {
        if (target) target.innerHTML = '<div class="ficha-error">No se pudo cargar la ficha personal.</div>';
        showToast('Error cargando ficha personal', 'error');
        console.error(error);
    }
};

// --- LÓGICA DE ASIGNACIÓN ---

let tutorExistenteSeleccionado = null;

function escapeTutorHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

window.abrirPreinscribirHermano = (alumnoId, nombreCodificado, tutorCodificado) => {
    const form = document.getElementById('form-preinscribir-hermano');
    form?.reset();
    document.getElementById('hermano-alumno-origen-id').value = String(alumnoId);
    document.getElementById('hermano-alumno-origen-nombre').textContent = decodeURIComponent(nombreCodificado);
    document.getElementById('hermano-tutor-nombre').textContent = decodeURIComponent(tutorCodificado);
    const fecha = document.getElementById('hermano-fecha-nacimiento');
    if (fecha) fecha.max = new Date().toISOString().slice(0, 10);
    openModal('modal-preinscribir-hermano');
    document.getElementById('hermano-nombres')?.focus();
};

async function guardarPreinscripcionHermano(event) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!form.reportValidity()) return;

    const alumnoOrigenId = Number(document.getElementById('hermano-alumno-origen-id').value);
    const submit = form.querySelector('button[type="submit"]');
    const textoOriginal = submit.innerHTML;
    submit.disabled = true;
    submit.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Guardando...';
    try {
        const res = await fetchAPI(`${API_BASE}/inscripciones/${alumnoOrigenId}/preinscribir-hermano`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nombres: form.elements.nombres.value.trim(),
                apellidos: form.elements.apellidos.value.trim(),
                fecha_nacimiento: form.elements.fecha_nacimiento.value,
                genero: form.elements.genero.value,
            }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'No se pudo preinscribir al hermano');
        showToast(data.mensaje, 'success');
        closeModal('modal-preinscribir-hermano');
        await loadInscripciones(currentPage);
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        submit.disabled = false;
        submit.innerHTML = textoOriginal;
    }
}

window.abrirTutorExistente = async (alumnoId, nombreCodificado) => {
    const form = document.getElementById('form-tutor-existente');
    form.reset();
    tutorExistenteSeleccionado = null;
    document.getElementById('tutor-existente-alumno-id').value = alumnoId;
    document.getElementById('tutor-existente-alumno-nombre').textContent = `Alumno: ${decodeURIComponent(nombreCodificado)}`;
    document.getElementById('tutor-existente-id').value = '';
    document.getElementById('buscar-tutor-existente').value = '';
    document.getElementById('resultados-tutores-existentes').innerHTML = '<div class="py-6 text-center text-sm text-gray-500"><i class="fas fa-spinner fa-spin mr-2"></i>Cargando tutores...</div>';
    openModal('modal-tutor-existente');
    await Promise.all([buscarTutoresExistentes(), cargarOtrosAlumnosTutor(alumnoId)]);
};

async function cargarOtrosAlumnosTutor(alumnoIdActual) {
    const contenedor = document.getElementById('otros-alumnos-tutor');
    if (!contenedor) return;
    contenedor.innerHTML = '<div class="py-3 text-center text-sm text-gray-500"><i class="fas fa-spinner fa-spin mr-2"></i>Cargando alumnos...</div>';
    try {
        const params = new URLSearchParams({ page: 1, per_page: 100, search: '', estado: '', grupo: '' });
        const res = await fetchAPI(`${API_BASE}/inscripciones?${params}`);
        if (!res.ok) throw new Error('No se pudieron cargar los alumnos');
        const data = await res.json();
        const otros = (data.items || []).filter(item => Number(item.id) !== Number(alumnoIdActual) && item.estado !== 'INACTIVO');
        if (!otros.length) {
            contenedor.innerHTML = '<p class="py-3 text-center text-sm text-gray-500">No hay otros alumnos disponibles.</p>';
            return;
        }
        contenedor.innerHTML = otros.map(item => `
            <label class="flex items-center gap-3 rounded-lg border border-gray-200 px-3 py-2 text-sm hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-700">
                <input type="checkbox" name="otros_alumnos" value="${item.id}" class="rounded text-emerald-600">
                <span><strong class="block text-gray-900 dark:text-white">${escapeTutorHtml(item.nombre_alumno)}</strong><span class="text-xs text-gray-500">${escapeTutorHtml(item.codigo_inscripcion)} · ${escapeTutorHtml(item.estado)}</span></span>
            </label>
        `).join('');
    } catch (error) {
        contenedor.innerHTML = '<p class="py-3 text-center text-sm text-red-600">No se pudieron cargar los demás alumnos.</p>';
        console.error(error);
    }
}

async function buscarTutoresExistentes() {
    const alumnoId = document.getElementById('tutor-existente-alumno-id')?.value;
    const termino = document.getElementById('buscar-tutor-existente')?.value.trim() || '';
    const resultados = document.getElementById('resultados-tutores-existentes');
    if (!alumnoId || !resultados) return;

    resultados.innerHTML = '<div class="py-6 text-center text-sm text-gray-500"><i class="fas fa-spinner fa-spin mr-2"></i>Buscando...</div>';
    try {
        const params = new URLSearchParams({ alumno_id: alumnoId, termino });
        const res = await fetchAPI(`${API_BASE}/tutores/existentes?${params}`);
        if (!res.ok) throw new Error('No se pudieron cargar los tutores');
        const data = await res.json();
        const items = Array.isArray(data.items) ? data.items : [];
        if (!items.length) {
            resultados.innerHTML = '<div class="py-6 text-center text-sm text-gray-500">No se encontraron tutores disponibles.</div>';
            return;
        }
        resultados.innerHTML = items.map(tutor => `
            <button type="button" data-tutor-id="${tutor.id}" class="tutor-existente-opcion w-full rounded-lg border border-gray-200 p-3 text-left transition hover:border-emerald-500 hover:bg-emerald-50 dark:border-gray-600 dark:hover:bg-emerald-900/20">
                <span class="block font-semibold text-gray-900 dark:text-white">${escapeTutorHtml(tutor.nombre_completo)}</span>
                <span class="block text-xs text-gray-500 dark:text-gray-400">CI: ${escapeTutorHtml(tutor.ci_numero || 'S/N')} · Celular: ${escapeTutorHtml(tutor.celular || 'S/N')}</span>
                <span class="block text-xs text-gray-500 dark:text-gray-400">Cuenta: ${escapeTutorHtml(tutor.cuenta_usuario || 'Sin usuario')}</span>
                <span class="mt-1 block text-xs text-emerald-700 dark:text-emerald-400">${tutor.cantidad_alumnos} alumno(s) vinculado(s)${tutor.alumnos?.length ? `: ${escapeTutorHtml(tutor.alumnos.join(', '))}` : ''}</span>
            </button>
        `).join('');
        resultados.querySelectorAll('.tutor-existente-opcion').forEach(button => {
            button.addEventListener('click', () => seleccionarTutorExistente(button));
        });
    } catch (error) {
        resultados.innerHTML = '<div class="py-6 text-center text-sm text-red-600">Error al buscar tutores.</div>';
        console.error(error);
    }
}

function seleccionarTutorExistente(button) {
    document.querySelectorAll('.tutor-existente-opcion').forEach(option => {
        option.classList.remove('border-emerald-500', 'bg-emerald-50', 'ring-2', 'ring-emerald-200');
    });
    button.classList.add('border-emerald-500', 'bg-emerald-50', 'ring-2', 'ring-emerald-200');
    tutorExistenteSeleccionado = Number(button.dataset.tutorId);
    document.getElementById('tutor-existente-id').value = String(tutorExistenteSeleccionado);
}

async function guardarTutorExistente(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const alumnoId = Number(document.getElementById('tutor-existente-alumno-id').value);
    const tutorId = Number(document.getElementById('tutor-existente-id').value);
    if (!tutorId) {
        showToast('Selecciona un tutor existente', 'warning');
        return;
    }

    const submit = form.querySelector('button[type="submit"]');
    submit.disabled = true;
    try {
        const alumnosAdicionales = Array.from(form.querySelectorAll('[name="otros_alumnos"]:checked'))
            .map(input => Number(input.value));
        const res = await fetchAPI(`${API_BASE}/inscripciones/asignar-tutor-existente`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                alumno_ids: [alumnoId, ...alumnosAdicionales],
                tutor_id: tutorId,
                tipo_relacion: form.tipo_relacion.value,
                es_principal: form.es_principal.checked,
                tiene_custodia: form.tiene_custodia.checked,
                recibe_notificaciones: form.recibe_notificaciones.checked,
                autorizado_retirar: form.autorizado_retirar.checked,
            }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'No se pudo vincular el tutor');
        showToast(data.mensaje || 'Tutor vinculado correctamente', 'success');
        closeModal('modal-tutor-existente');
        await loadInscripciones(currentPage);
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        submit.disabled = false;
    }
}

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


window.imprimirFichaDetalle = async function() {
    const ficha = document.getElementById('ficha-document');
    if (!ficha || !ficha.querySelector('.ficha-page')) {
        showToast('Primero debe cargar una ficha personal', 'warning');
        return;
    }

    // Evita que el diálogo de impresión capture una foto o logo a medio cargar.
    const pendingImages = [...ficha.querySelectorAll('img')]
        .filter(image => !image.complete)
        .map(image => new Promise(resolve => {
            image.addEventListener('load', resolve, { once: true });
            image.addEventListener('error', resolve, { once: true });
        }));
    await Promise.all(pendingImages);

    const cleanup = () => document.body.classList.remove('ficha-print-mode');
    window.addEventListener('afterprint', cleanup, { once: true });
    document.body.classList.add('ficha-print-mode');

    // Dos frames permiten aplicar el CSS @media print al mismo DOM mostrado
    // en el modal antes de abrir el diálogo nativo del navegador.
    requestAnimationFrame(() => requestAnimationFrame(() => {
        try {
            window.print();
        } catch (error) {
            cleanup();
            console.error('No se pudo imprimir la ficha', error);
            showToast('No se pudo abrir la impresión', 'error');
        }
    }));
};
