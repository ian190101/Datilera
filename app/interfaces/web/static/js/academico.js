import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';
let alumnosCache = [];

document.addEventListener('DOMContentLoaded', () => {
    // 1. Setear fecha de hoy (si no tiene valor)
    const dateInput = document.getElementById('global-date');
    if(dateInput && !dateInput.value) {
        dateInput.valueAsDate = new Date();
    }
    dateInput?.addEventListener('change', refreshData);

    // 2. Cargar Grupos (usando el endpoint que ya funciona en otras páginas)
    loadGrupos();
    
    // 3. Listener Grupo -> Paralelo
    const grupoSelect = document.getElementById('global-grupo-filter');
    const paraleloSelect = document.getElementById('global-paralelo-filter');
    
    grupoSelect?.addEventListener('change', async (e) => {
        const grupoId = e.target.value;
        paraleloSelect.innerHTML = '<option value="">-- Paralelo --</option>';
        paraleloSelect.disabled = true;
        
        if (grupoId) {
            await loadParalelos(grupoId);
            paraleloSelect.disabled = false;
        }
        refreshData();
    });

    paraleloSelect?.addEventListener('change', refreshData);

    // 4. Tabs
    initTabs();

    // 5. Cargar Datos Iniciales
    refreshData();
});

// --- CARGA DE GRUPOS (reutilizando la lógica que ya tienes en otros filtros) ---
async function loadGrupos() {
    try {
        const res = await fetchAPI(`${API_BASE}/grupos`);  // ← Endpoint que ya usas y funciona
        
        if (!res.ok) {
            console.error("Error al cargar grupos:", res.status, res.statusText);
            showToast("Error al cargar los grupos", "error");
            return;
        }

        const data = await res.json();
        const globalGrupoSelect = document.getElementById('global-grupo-filter');

        if (!globalGrupoSelect) {
            console.warn("No se encontró el select #global-grupo-filter");
            return;
        }

        // Limpiar y opción por defecto
        globalGrupoSelect.innerHTML = '<option value="">Seleccionar Grupo</option>';

        if (!data.items || data.items.length === 0) {
            globalGrupoSelect.innerHTML += '<option disabled>No hay grupos disponibles</option>';
            return;
        }

        data.items.forEach(g => {
            const option = document.createElement('option');
            option.value = g.id;
            // Ajusta según los campos que devuelve tu endpoint /grupos
            option.textContent = `${g.nombre} - ${g.gestion || new Date().getFullYear()}`;
            // Si tienes campo "turno":  ${g.turno ? ` (${g.turno})` : ''}
            globalGrupoSelect.appendChild(option);
        });

    } catch(e) {
        console.error("Error cargando grupos:", e);
        showToast("Error al cargar los grupos", "error");
    }
}

// --- CARGA DE PARALELOS (usando endpoint existente) ---
async function loadParalelos(grupoId) {
    try {
        const res = await fetchAPI(`${API_BASE}/paralelos?grupo_id=${grupoId}`);
        
        if (!res.ok) {
            console.error("Error al cargar paralelos:", res.status);
            return;
        }

        const data = await res.json();
        const paraleloSelect = document.getElementById('global-paralelo-filter');

        paraleloSelect.innerHTML = '<option value="">-- Paralelo --</option>';
        paraleloSelect.disabled = false;

        if (data.items && data.items.length > 0) {
            data.items.forEach(p => {
                const option = document.createElement('option');
                option.value = p.id;
                option.textContent = p.letra;
                paraleloSelect.appendChild(option);
            });
        } else {
            paraleloSelect.innerHTML += '<option disabled>No hay paralelos</option>';
        }

    } catch(e) {
        console.error("Error cargando paralelos:", e);
        document.getElementById('global-paralelo-filter').disabled = true;
        showToast("Error al cargar paralelos", "error");
    }
}

function refreshData() {
    console.log("refreshData llamado - Tab activo:", document.querySelector('.tab-content.active')?.id);
    const activeTab = document.querySelector('.tab-content.active');
    if(activeTab && activeTab.id === 'tab-diario') loadDiario();
    else if(activeTab && activeTab.id === 'tab-asistencia') loadAsistencia(); 
}

// --- UTILIDADES DE AVATAR (NUEVO) ---
function getAvatarHTML(url, name) {
  // FOTO Y NOMBRE - Avatar consistente y alineado perfectamente
  const safeName = name || '';
  const initial = safeName.charAt(0).toUpperCase();

  return `
    <div class="flex items-center">
      <div class="flex-shrink-0 w-10 h-10 rounded-full overflow-hidden shadow-sm border border-gray-100 dark:border-gray-600">
        ${
          url && url !== 'NULL' && url !== '' && url !== 'None'
            ? `<img src="${url}?t=${Date.now()}"
                    alt="${safeName}"
                    class="w-full h-full object-cover">`
            : `<div class="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                 <span class="text-primary-600 dark:text-primary-400 font-semibold text-lg">
                   ${initial}
                 </span>
               </div>`
        }
      </div>
    </div>
  `;
}


// --- TABS LOGIC ---
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      // UI Update (botones)
      document.querySelectorAll('.tab-btn').forEach(b => {
        b.classList.remove('active', 'border-[#DD8E0A]', 'text-[#DD8E0A]');
        b.classList.add('border-transparent', 'text-gray-500');
      });
      btn.classList.add('active', 'border-[#DD8E0A]', 'text-[#DD8E0A]');
      btn.classList.remove('border-transparent', 'text-gray-500');

      // Content Update (tabs)
      document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.add('hidden');
        c.classList.remove('active');           // quitar active de todos
      });

      const targetTab = document.getElementById(`tab-${btn.dataset.tab}`);
      if (targetTab) {
        targetTab.classList.remove('hidden');
        targetTab.classList.add('active');      // poner active solo al tab seleccionado
      }

      // FORZAR RECARGA INMEDIATA
      if (btn.dataset.tab === 'diario') {
        loadDiario();
      } else if (btn.dataset.tab === 'asistencia') {
        loadAsistencia();
      }
    });
  });
}


// ===========================
// DIARIO (TABLA ICONOS)
// ===========================
async function loadDiario() {
  const tbody = document.getElementById('diario-tbody');
  tbody.innerHTML = '<tr><td colspan="16" class="text-center py-8"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></td></tr>';

  const fecha    = document.getElementById('global-date').value;
  const grupo    = document.getElementById('global-grupo-filter').value;
  const paralelo = document.getElementById('global-paralelo-filter').value;

  try {
    let url = `${API_BASE}/academico/diario?fecha=${fecha}`;
    if (grupo)    url += `&grupo_id=${grupo}`;
    if (paralelo) url += `&paralelo_id=${paralelo}`;

    const res  = await fetchAPI(url);
    const data = await res.json();

    // Llenar alumnosCache para el modal
    alumnosCache = (data.items || []).map(item => ({
      id: item.id,
      nombre_completo: item.nombre_completo || item.nombrecompleto || item.nombre_alumno || item.nombre
    }));

    renderTableDiario(data.items);
  } catch (e) {
    console.error('Error cargando diario:', e);
    tbody.innerHTML = '<tr><td colspan="16" class="text-center py-8 text-red-500">Error cargando datos</td></tr>';
  }
}


function renderTableDiario(items) {
    const tbody = document.getElementById('diario-tbody');
    tbody.innerHTML = '';

    if(!items || !items.length) {
        tbody.innerHTML = '<tr><td colspan="16" class="text-center py-8 text-gray-500">No hay alumnos para mostrar</td></tr>';
        return;
    }

    items.forEach(item => {
        const acts = item.actividades || {};
        
        // Helper para las celdas de contadores
        const cell = (key) => {
            const count = acts[key] || 0;
            return count > 0 
                ? `<div class="flex justify-center"><span class="font-bold text-gray-800 dark:text-white bg-gray-100 dark:bg-gray-700 min-w-[24px] text-center rounded-md text-sm">${count}</span></div>` 
                : `<span class="text-gray-300">-</span>`;
        };

        // --- NUEVA LÓGICA DE AVATAR (Solicitada) ---
        // Adaptada para usar item.nombre_completo y colores del tema (Orange/Dorado)
        let avatarHTML = `
            <div class="flex items-center">
                <div class="flex-shrink-0 w-10 h-10 rounded-full overflow-hidden shadow-sm border border-gray-100 dark:border-gray-600">
                    ${item.foto_url && item.foto_url !== 'NULL'
                        ? `<img src="${item.foto_url}?t=${Date.now()}" 
                                alt="${item.nombre_completo}"
                                class="w-full h-full object-cover">`
                        : `<div class="w-full h-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center">
                            <span class="text-[#DD8E0A] dark:text-orange-400 font-bold text-lg">
                                ${item.nombre_completo.charAt(0).toUpperCase()}
                            </span>
                        </div>`
                    }
                </div>
                <div class="ml-3">
                    <div class="font-medium text-gray-900 dark:text-white truncate max-w-[160px]" title="${item.nombre_completo}">
                        ${item.nombre_completo}
                    </div>
                </div>
            </div>
        `;
        // -------------------------------------------

        const tr = document.createElement('tr');
        tr.className = "bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition";
        
        tr.innerHTML = `
            <td class="px-6 py-3 whitespace-nowrap sticky left-0 bg-white dark:bg-gray-800 z-10 border-r border-gray-100 dark:border-gray-700 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]">
                ${avatarHTML}
            </td>
            
            <td class="text-center px-1 py-3">${cell('ALIMENTACION')}</td>
            <td class="text-center px-1 py-3">${cell('HIGIENE')}</td>
            <td class="text-center px-1 py-3">${cell('APRENDIZAJE')}</td>
            <td class="text-center px-1 py-3">${cell('FOTO')}</td>
            <td class="text-center px-1 py-3">${cell('ANIMO')}</td>
            <td class="text-center px-1 py-3">${cell('SIESTA')}</td>
            <td class="text-center px-1 py-3">${cell('LOGROS')}</td>
            <td class="text-center px-1 py-3">${cell('OBSERVACION')}</td>
            <td class="text-center px-1 py-3">${cell('SALUD')}</td>
            <td class="text-center px-1 py-3">${cell('VIDEO')}</td>
            <td class="text-center px-1 py-3">${cell('MEDICAMENTO')}</td>
            <td class="text-center px-1 py-3">${cell('ACCIDENTE')}</td>
            <td class="text-center px-1 py-3">${cell('TAREA')}</td>
            
            <td class="text-center px-4 py-3">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-medium whitespace-nowrap border ${item.badge_color ? item.badge_color.replace('bg-', 'bg-opacity-20 border-') : ''} ${item.badge_color}">
                    ${item.estado_reporte}
                </span>
            </td>

            <td class="text-right px-6 py-3 whitespace-nowrap">
                <div class="flex justify-end gap-2">
                    <button onclick="window.abrirModalReporte(${item.id})" 
                        class="text-[#DD8E0A] hover:text-[#b87608] bg-yellow-50 hover:bg-yellow-100 dark:bg-yellow-900/30 dark:text-yellow-300 p-1.5 rounded-lg transition flex items-center gap-1" title="Ver Reporte">
                        Ver <i class="fas fa-chevron-right text-xs"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}



// (MANTENER EL CÓDIGO DE ASISTENCIA Y MODAL ROJO QUE YA TE PASÉ ANTES)
// Asegúrate de copiar las funciones window.abrirModalReporte, window.closeModal, loadAsistencia, setAsistencia, guardarAsistencia del bloque anterior.

// ===========================
// MODAL ROJO (REPORTE DETALLADO)
// ===========================
window.abrirModalReporte = async (alumnoId) => {
    const modal = document.getElementById('modal-reporte');
    const container = document.getElementById('modal-lista-actividades');
    const fecha = document.getElementById('global-date').value;

    modal.classList.remove('hidden');
    container.innerHTML = '<div class="text-center py-10"><i class="fas fa-spinner fa-spin text-gray-400 text-2xl"></i></div>';
    
    // Reset Data Header
    document.getElementById('modal-nombre').textContent = 'Cargando...';

    try {
        const res = await fetchAPI(`${API_BASE}/academico/diario/${alumnoId}/detalle?fecha=${fecha}`);
        const data = await res.json();

               // Fill Header - NUEVO AVATAR CONSISTENTE
        document.getElementById('modal-nombre').textContent = data.alumno.nombre;

        const avatarContainer = document.getElementById('modal-avatar-container');
        
        if (data.alumno.foto_url && data.alumno.foto_url !== 'NULL' && data.alumno.foto_url.trim() !== '') {
            // Hay foto → crear img
            avatarContainer.innerHTML = `
                <img src="${data.alumno.foto_url}?t=${Date.now()}" 
                    alt="${data.alumno.nombre}"
                    class="w-full h-full object-cover">
            `;
        } else {
            // Sin foto → inicial en fondo coloreado
            const inicial = data.alumno.nombre.charAt(0).toUpperCase();
            avatarContainer.innerHTML = `
                <div class="w-full h-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                    <span class="text-primary-600 dark:text-primary-400 font-bold text-3xl">
                        ${inicial}
                    </span>
                </div>
            `;
        }

        document.getElementById('modal-fecha').textContent = data.fecha_str;

        // Fill List
        container.innerHTML = '';
        if(data.actividades.length === 0) {
            container.innerHTML = `
                <div class="text-center py-10 text-gray-400 flex flex-col items-center">
                    <i class="far fa-calendar-times text-4xl mb-3 opacity-50"></i>
                    <p>No hay actividades registradas en esta fecha</p>
                </div>`;
            return;
        }

        data.actividades.forEach(act => {
            // 1. OBTENER CONFIGURACIÓN VISUAL (ICONO/COLOR)
            // Usamos ACTIVITY_TYPES global para garantizar consistencia con la tabla
            const config = ACTIVITY_TYPES.find(t => t.code === act.tipo) || { 
                icon: 'fa-circle', 
                color: 'text-gray-400', 
                bg: 'bg-gray-100',
                label: act.tipo 
            };

            // 2. DETERMINAR TÍTULO PRINCIPAL
            // Si es ANIMO, mostramos el valor (ej: FELIZ) como título
            let mainTitle = config.label; // Por defecto el nombre del tipo
            let mainValue = act.descripcion || '';

            if (act.tipo === 'ANIMO' && act.valor) {
                mainTitle = act.valor; // Título: FELIZ
                // Icono extra si es feliz, etc (opcional, ya tenemos el icono del tipo)
            } else if (act.valor) {
                // Para otros tipos (Salud: 38°C, Comida: Todo), agregamos el valor al título
                mainTitle += `: ${act.valor}`; 
            }

            // 3. RENDERIZAR MULTIMEDIA (FOTOS/VIDEOS)
            let mediaHTML = '';
            if (act.media_url) {
                if (act.media_tipo === 'video') {
                    mediaHTML = `
                        <div class="mt-3 mb-2 rounded-lg overflow-hidden shadow-sm border border-gray-100">
                            <video controls class="w-full h-48 object-cover bg-black">
                                <source src="${act.media_url}" type="video/mp4">
                                Tu navegador no soporta video.
                            </video>
                        </div>`;
                } else {
                    mediaHTML = `
                        <div class="mt-3 mb-2 rounded-lg overflow-hidden shadow-sm border border-gray-100 group cursor-pointer">
                            <img src="${act.media_url}" class="w-full h-48 object-cover transform group-hover:scale-105 transition duration-500" onclick="window.open(this.src, '_blank')">
                        </div>`;
                }
            }

            // 4. CONSTRUIR CARD
            const div = document.createElement('div');
            // Diseño de tarjeta limpia con borde izquierdo de color
            div.className = "flex gap-4 p-4 bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 shadow-sm mb-3 relative overflow-hidden";
            
            div.innerHTML = `
                <div class="flex-shrink-0 relative z-10">
                    <div class="w-12 h-12 rounded-full ${config.bg} flex items-center justify-center shadow-inner">
                        <i class="fas ${config.icon} ${config.color} text-xl"></i>
                    </div>
                    <div class="absolute top-12 left-1/2 -translate-x-1/2 w-0.5 h-full bg-gray-100 -z-10"></div>
                </div>

                <div class="flex-1 min-w-0">
                    <div class="flex justify-between items-start mb-1">
                        <h4 class="font-bold text-gray-800 dark:text-white text-base capitalize truncate pr-2">
                            ${mainTitle.toLowerCase()}
                        </h4>
                        
                    </div>
                    
                    ${mainValue ? `<p class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">${mainValue}</p>` : ''}
                    
                    ${mediaHTML}
                    
                    <div class="flex justify-between items-center mt-3 pt-2 border-t border-gray-50 dark:border-gray-700">
                        <div class="flex items-center gap-1.5 text-xs text-gray-400">
                            <span class="font-medium">Creado por:</span>
                            <span class="font-medium">${act.creador}</span>
                        </div>
                        <div class="flex items-center gap-1.5 text-xs font-mono text-[#DD8E0A] bg-orange-50 px-2 py-0.5 rounded">
                            <i class="far fa-clock"></i>
                            ${act.hora}
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });

    } catch(e) {
        console.error(e);
        showToast('Error cargando detalles del reporte', 'error');
    }
};

window.closeModal = (id) => {
    document.getElementById(id).classList.add('hidden');
};

// ===========================
// ASISTENCIA - VERSIÓN CORREGIDA Y FUNCIONAL
// ===========================
async function loadAsistencia() {
    const tbody = document.getElementById('asistencia-tbody');
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></td></tr>';

    const fecha = document.getElementById('global-date').value;
    const grupo = document.getElementById('global-grupo-filter').value;

    try {
        let url = `${API_BASE}/academico/asistencia?fecha=${fecha}`;
        if (grupo) url += `&grupo_id=${grupo}`;

        const res = await fetchAPI(url);
        if (!res.ok) {
            throw new Error(`Error ${res.status}`);
        }
        const data = await res.json();

        renderAsistenciaTable(data.items || []);

    } catch (e) {
        console.error("Error cargando asistencia:", e);
        tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-red-500">Error al cargar la asistencia</td></tr>';
    }
}

/* EN ACADEMICO.JS - Reemplaza la función renderAsistenciaTable */

function renderAsistenciaTable(items) {
    const tbody = document.getElementById('asistencia-tbody');
    tbody.innerHTML = '';

    // 1. DETECCIÓN DE ROL (MODO LECTURA)
    // Verificamos si el botón "Guardar Asistencia" tiene la clase 'hidden' (puesta por Jinja)
    const saveBtn = document.querySelector('button[onclick="guardarAsistencia()"]');
    const isReadOnly = saveBtn ? saveBtn.classList.contains('hidden') : true;

    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8 text-gray-500">No hay alumnos en este grupo</td></tr>';
        return;
    }

    items.forEach(item => {
        const asis = item.asistencia || { estado: 'PENDIENTE', hora_retraso: '', observacion: '' };
        const estado = asis.estado || 'PENDIENTE';

        const tr = document.createElement('tr');
        tr.className = "bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700";
        tr.dataset.alumnoId = item.id;

        // --- HELPER PARA GENERAR BOTONES CON ESTILOS CONDICIONALES ---
        const makeBtn = (type, icon, activeClasses) => {
            const isSelected = estado === type;
            let classes = "btn-estado p-2 rounded-lg transition ";
            
            if (isReadOnly) {
                // ESTILOS PARA TUTOR (Lectura)
                classes += "cursor-not-allowed "; 
                if (isSelected) {
                    classes += activeClasses; // Mantiene el color si es el estado actual
                } else {
                    classes += "bg-gray-50 text-gray-300 opacity-50"; // Muy tenue si no es el estado
                }
            } else {
                // ESTILOS PARA PROFESORA/ADMIN (Edición)
                if (isSelected) {
                    classes += activeClasses;
                } else {
                    classes += "bg-gray-100 text-gray-500 hover:bg-gray-200 hover:scale-105";
                }
            }

            return `
                <button type="button" 
                        data-estado="${type}" 
                        ${isReadOnly ? 'disabled' : ''} 
                        class="${classes}">
                    <i class="fas ${icon}"></i>
                </button>
            `;
        };

        // --- HTML DE LA FILA ---
        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center gap-3">
                    ${getAvatarHTML(item.foto_url, item.nombre)}
                    <span class="font-medium text-gray-900 dark:text-white">${item.nombre}</span>
                </div>
            </td>
            <td class="px-6 py-4 text-center">
                <div class="flex justify-center gap-2">
                    ${makeBtn('PRESENTE', 'fa-check', 'bg-green-100 text-green-700 ring-2 ring-green-500')}
                    ${makeBtn('AUSENTE', 'fa-times', 'bg-red-100 text-red-700 ring-2 ring-red-500')}
                    ${makeBtn('RETRASO', 'fa-clock', 'bg-yellow-100 text-yellow-700 ring-2 ring-yellow-500')}
                    ${makeBtn('JUSTIFICADO', 'fa-file-medical', 'bg-blue-100 text-blue-700 ring-2 ring-blue-500')}
                </div>
                <input type="hidden" class="input-estado" value="${estado}">
            </td>
            <td class="px-6 py-4 text-center">
                <input type="time" 
                       class="input-hora border-gray-300 rounded-lg px-3 py-1.5 text-sm w-28 
                              ${estado !== 'RETRASO' ? 'hidden' : ''} 
                              ${isReadOnly ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : ''}" 
                       value="${asis.hora_retraso || ''}"
                       ${isReadOnly ? 'disabled readonly' : ''}>
            </td>
            <td class="px-6 py-4">
                <input type="text" 
                       class="input-obs w-full border-gray-300 rounded-lg px-3 py-2 text-sm 
                              ${isReadOnly ? 'bg-gray-50 text-gray-500 border-transparent cursor-default focus:ring-0' : ''}" 
                       placeholder="${isReadOnly ? (asis.observacion ? '' : '-') : 'Observación...'}" 
                       value="${asis.observacion || ''}"
                       ${isReadOnly ? 'readonly' : ''}>
            </td>
        `;

        // 2. SOLO AGREGAR LISTENERS SI NO ES MODO LECTURA
        if (!isReadOnly) {
            tr.querySelectorAll('.btn-estado').forEach(btn => {
                btn.addEventListener('click', function() {
                    const nuevoEstado = this.dataset.estado;
                    const row = this.closest('tr');

                    // Reset visual de todos los botones en la fila
                    row.querySelectorAll('.btn-estado').forEach(b => {
                        b.className = 'btn-estado p-2 rounded-lg transition bg-gray-100 text-gray-500 hover:bg-gray-200 hover:scale-105';
                    });

                    // Colorear el seleccionado
                    let colorClass = '';
                    if (nuevoEstado === 'PRESENTE') colorClass = 'bg-green-100 text-green-700 ring-2 ring-green-500';
                    if (nuevoEstado === 'AUSENTE') colorClass = 'bg-red-100 text-red-700 ring-2 ring-red-500';
                    if (nuevoEstado === 'RETRASO') colorClass = 'bg-yellow-100 text-yellow-700 ring-2 ring-yellow-500';
                    if (nuevoEstado === 'JUSTIFICADO') colorClass = 'bg-blue-100 text-blue-700 ring-2 ring-blue-500';

                    this.className = `btn-estado p-2 rounded-lg transition ${colorClass}`;

                    // Actualizar valor oculto
                    row.querySelector('.input-estado').value = nuevoEstado;

                    // Lógica del campo Hora
                    const horaInput = row.querySelector('.input-hora');
                    if (nuevoEstado === 'RETRASO') {
                        horaInput.classList.remove('hidden');
                        if (!horaInput.value) {
                            const now = new Date();
                            horaInput.value = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
                        }
                    } else {
                        horaInput.classList.add('hidden');
                        horaInput.value = '';
                    }
                });
            });
        }

        tbody.appendChild(tr);
    });
}

// ===========================
// GUARDAR ASISTENCIA (ENVÍA TODOS LOS ALUMNOS)
// ===========================
window.guardarAsistencia = async () => {
    const fecha = document.getElementById('global-date').value;
    const rows = document.querySelectorAll('#asistencia-tbody tr');

    const asistencias = [];

    rows.forEach(tr => {
        if (!tr.dataset.alumnoId) return;

        const estado = tr.querySelector('.input-estado').value;
        const horaInput = tr.querySelector('.input-hora');
        const obsInput = tr.querySelector('.input-obs');

        asistencias.push({
            id: parseInt(tr.dataset.alumnoId),
            estado: estado,
            hora_retraso: estado === 'RETRASO' ? horaInput.value : '',
            observacion: obsInput.value.trim()
        });
    });

    if (asistencias.length === 0) {
        showToast('No hay datos para guardar', 'warning');
        return;
    }

    try {
        const res = await fetchAPI(`${API_BASE}/academico/asistencia`, {
            method: 'POST',
            body: JSON.stringify({
                fecha: fecha,
                asistencias: asistencias
            })
        });

        const data = await res.json();
        if (data.success) {
            showToast('Asistencia guardada correctamente', 'success');
            // Opcional: recargar para ver confirmación visual
            // loadAsistencia();
        } else {
            showToast('Error al guardar asistencia', 'error');
        }
    } catch (err) {
        console.error(err);
        showToast('Error de conexión al guardar', 'error');
    }
};

// Agrega esto en renderAsistenciaTable dentro del forEach:
// tr.dataset.alumnoId = item.id;

// ... (imports y código existente de carga de tablas) ...

// ==========================================
// CONFIGURACIÓN DE TIPOS (13 TIPOS EXACTOS)
// ==========================================
const ACTIVITY_TYPES = [
    { code: 'ALIMENTACION', label: 'Alimentación', icon: 'fa-apple-alt', color: 'text-red-500', bg: 'bg-red-50' },
    { code: 'HIGIENE', label: 'Higiene', icon: 'fa-toilet', color: 'text-purple-500', bg: 'bg-purple-50' },
    { code: 'APRENDIZAJE', label: 'Aprendizaje', icon: 'fa-shapes', color: 'text-orange-500', bg: 'bg-orange-50' },
    { code: 'FOTO', label: 'Foto', icon: 'fa-images', color: 'text-blue-500', bg: 'bg-blue-50' },
    { code: 'ANIMO', label: 'Ánimo', icon: 'fa-smile', color: 'text-yellow-500', bg: 'bg-yellow-50' },
    { code: 'SIESTA', label: 'Siesta', icon: 'fa-bed', color: 'text-indigo-500', bg: 'bg-indigo-50' },
    { code: 'LOGROS', label: 'Logros', icon: 'fa-trophy', color: 'text-yellow-600', bg: 'bg-yellow-50' },
    { code: 'OBSERVACION', label: 'Observación', icon: 'fa-book', color: 'text-gray-600', bg: 'bg-gray-100' },
    { code: 'SALUD', label: 'Salud', icon: 'fa-thermometer-half', color: 'text-red-600', bg: 'bg-red-50' },
    { code: 'VIDEO', label: 'Video', icon: 'fa-video', color: 'text-blue-600', bg: 'bg-blue-50' },
    { code: 'MEDICAMENTO', label: 'Medicamento', icon: 'fa-pills', color: 'text-pink-500', bg: 'bg-pink-50' },
    { code: 'ACCIDENTE', label: 'Accidente', icon: 'fa-user-injured', color: 'text-red-700', bg: 'bg-red-50' },
    { code: 'TAREA', label: 'Tarea', icon: 'fa-book-open', color: 'text-indigo-600', bg: 'bg-indigo-50' }
];

// ===========================
// LÓGICA DEL MODAL VISUAL
// ===========================

window.abrirModalNuevaActividad = () => {
    const modal = document.getElementById('modal-nueva-actividad');
    modal.classList.remove('hidden');
    
    // Preparar Vista 1: Grid
    document.getElementById('step-select-type').classList.remove('hidden');
    document.getElementById('step-details').classList.add('hidden');
    document.getElementById('modal-actividad-titulo').textContent = 'Nueva Actividad';
    document.getElementById('modal-actividad-subtitulo').textContent = 'Selecciona el tipo de registro';
    document.getElementById('modal-actividad-icon-header').innerHTML = '';

    // Generar Grid
    const grid = document.getElementById('step-select-type');
    grid.innerHTML = '';
    
    ACTIVITY_TYPES.forEach(t => {
        const btn = document.createElement('button');
        // Clases para parecerse a la imagen (Card blanco, sombra suave, icono centrado)
        btn.className = `flex flex-col items-center justify-center p-4 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-[#DD8E0A] transition-all bg-white group h-28`;
        btn.onclick = () => seleccionarTipo(t);
        
        btn.innerHTML = `
            <div class="mb-2 p-3 rounded-full ${t.bg} group-hover:scale-110 transition-transform">
                <i class="fas ${t.icon} ${t.color} text-2xl"></i>
            </div>
            <span class="text-xs font-bold text-gray-600 uppercase">${t.label}</span>
        `;
        grid.appendChild(btn);
    });

    // Resetear formulario
    document.getElementById('form-actividad-detalle').reset();
    
    // Llenar select de alumnos (usamos la variable global alumnosCache que ya tenías o la cargamos)
    const sel = document.getElementById('act-alumno-select');
    sel.innerHTML = '<option value="">Seleccionar Alumno</option>';
    // Nota: alumnosCache se llena en loadGruposYAlumnos() o similar
    if(typeof alumnosCache !== 'undefined') {
        alumnosCache.forEach(a => {
            // Ajuste: verificar si el objeto tiene 'id' y 'nombre_completo' o adaptarlo
            const nombre = a.nombre_completo || `${a.nombre} ${a.apellido_paterno}`;
            sel.innerHTML += `<option value="${a.id}">${nombre}</option>`;
        });
    }

    // Configurar visibilidad de campos (Modo General)
    document.getElementById('container-select-alumno').classList.remove('hidden');
    document.getElementById('container-nombre-alumno').classList.add('hidden');
    document.getElementById('act-alumno-id').value = '';
}

window.seleccionarTipo = (typeObj) => {
    // Cambiar a Vista 2: Formulario
    document.getElementById('step-select-type').classList.add('hidden');
    document.getElementById('step-details').classList.remove('hidden');
    
    // Setear datos
    document.getElementById('act-tipo-codigo').value = typeObj.code;
    
    // Actualizar Header del Modal para dar contexto
    document.getElementById('modal-actividad-titulo').textContent = typeObj.label;
    document.getElementById('modal-actividad-subtitulo').textContent = 'Completa los detalles';
    document.getElementById('modal-actividad-icon-header').innerHTML = `<i class="fas ${typeObj.icon} ${typeObj.color} text-2xl"></i>`;

    // Hora actual por defecto
    const now = new Date();
    const timeStr = now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
    document.getElementById('act-hora').value = timeStr;

    // Foco
    setTimeout(() => document.getElementById('act-valor').focus(), 100);
}

window.volverSeleccionTipo = () => {
    document.getElementById('step-details').classList.add('hidden');
    document.getElementById('step-select-type').classList.remove('hidden');
    document.getElementById('modal-actividad-titulo').textContent = 'Nueva Actividad';
    document.getElementById('modal-actividad-icon-header').innerHTML = '';
}

window.closeModalActividad = () => {
    document.getElementById('modal-nueva-actividad').classList.add('hidden');
}

// ===========================
// ASIGNAR TAREA (Directo)
// ===========================
window.abrirAsignarTarea = (alumnoId, nombreAlumno) => {
    const modal = document.getElementById('modal-nueva-actividad');
    modal.classList.remove('hidden');
    
    // Buscar tipo TAREA
    const tareaType = ACTIVITY_TYPES.find(t => t.code === 'TAREA');
    
    // Saltar directo al paso 2
    seleccionarTipo(tareaType);
    
    // Pre-seleccionar alumno
    document.getElementById('act-alumno-id').value = alumnoId;
    document.getElementById('act-nombre-display').textContent = nombreAlumno;
    
    document.getElementById('container-select-alumno').classList.add('hidden');
    document.getElementById('container-nombre-alumno').classList.remove('hidden');
    
    document.getElementById('modal-actividad-titulo').textContent = 'Asignar Tarea';
}

// ===========================
// GUARDAR (Submit)
// ===========================
document.getElementById('form-actividad-detalle')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Determinar ID de alumno
    let id = document.getElementById('act-alumno-id').value;
    if(!id) id = document.getElementById('act-alumno-select').value;
    
    if(!id) {
        showToast('Selecciona un alumno', 'error');
        return;
    }

    const payload = {
        alumno_id: id,
        fecha: document.getElementById('global-date').value,
        tipo: document.getElementById('act-tipo-codigo').value,
        hora: document.getElementById('act-hora').value,
        valor: document.getElementById('act-valor').value,
        descripcion: document.getElementById('act-descripcion').value
    };

    try {
        await fetchAPI(`${API_BASE}/academico/actividades`, {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        showToast('Actividad registrada', 'success');
        closeModalActividad();
        // Recargar tabla
        const btnRefresh = document.getElementById('global-date'); 
        if(btnRefresh) btnRefresh.dispatchEvent(new Event('change')); // Truco para recargar
        
    } catch(err) {
        showToast('Error al guardar', 'error');
    }
});

// ... (código anterior: carga de grupos, tabs, etc.)

// LISTA DE ÁNIMOS (Para los botones)
const MOODS = [
    { label: 'Feliz', icon: 'fa-smile-beam', color: 'text-yellow-400', value: 'FELIZ' },
    { label: 'Triste', icon: 'fa-frown', color: 'text-blue-400', value: 'TRISTE' },
    { label: 'Enojado', icon: 'fa-angry', color: 'text-red-500', value: 'ENOJADO' },
    { label: 'Participativo', icon: 'fa-hand-paper', color: 'text-green-500', value: 'PARTICIPATIVO' },
    { label: 'Cansado', icon: 'fa-tired', color: 'text-gray-400', value: 'CANSADO' },
    { label: 'Molesto', icon: 'fa-meh-rolling-eyes', color: 'text-orange-500', value: 'MOLESTO' },
    { label: 'Lloroso', icon: 'fa-sad-tear', color: 'text-blue-300', value: 'LLOROSO' },
    { label: 'Asustado', icon: 'fa-flushed', color: 'text-purple-400', value: 'ASUSTADO' }
];

window.seleccionarTipo = (typeObj) => {
    // 1. UI Transitions
    document.getElementById('step-select-type').classList.add('hidden');
    document.getElementById('step-details').classList.remove('hidden');
    
    // 2. Setear datos base
    document.getElementById('act-tipo-codigo').value = typeObj.code;
    document.getElementById('modal-actividad-titulo').textContent = typeObj.label;
    document.getElementById('modal-actividad-icon-header').innerHTML = `<i class="fas ${typeObj.icon} ${typeObj.color} text-2xl"></i>`;
    
    // Hora por defecto
    const now = new Date();
    document.getElementById('act-hora').value = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;

    // 3. GENERAR FORMULARIO DINÁMICO SEGÚN TIPO
    const container = document.getElementById('dynamic-form-fields');
    container.innerHTML = ''; // Limpiar campos anteriores

    // CASO A: FOTO O VIDEO (Subir archivo)
    if (['FOTO', 'VIDEO'].includes(typeObj.code)) {
        const accept = typeObj.code === 'VIDEO' ? 'video/*' : 'image/*';
        const icon = typeObj.code === 'VIDEO' ? 'fa-video' : 'fa-camera';
        
        container.innerHTML = `
            <div class="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:bg-gray-50 transition cursor-pointer relative" id="dropzone">
                <input type="file" id="act-archivo" accept="${accept}" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onchange="previewFile(this)">
                <div id="file-preview-area">
                    <i class="fas ${icon} text-4xl text-gray-300 mb-2"></i>
                    <p class="text-sm text-gray-500 font-medium">Toca para subir ${typeObj.label}</p>
                </div>
            </div>
            <div>
                <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Título / Descripción</label>
                <textarea id="act-descripcion" rows="2" class="w-full border-gray-300 rounded-xl p-3" placeholder="Descripción de la imagen/video..."></textarea>
            </div>
        `;
    } 
    // CASO B: ESTADO DE ÁNIMO (Botones)
    else if (typeObj.code === 'ANIMO') {
        let moodHTML = `<div class="grid grid-cols-4 gap-3 mb-4">`;
        MOODS.forEach(m => {
            moodHTML += `
                <button type="button" onclick="selectMood('${m.value}', this)" class="mood-btn flex flex-col items-center p-3 rounded-xl border border-gray-200 hover:border-[#DD8E0A] hover:bg-orange-50 transition bg-white">
                    <i class="fas ${m.icon} ${m.color} text-2xl mb-1"></i>
                    <span class="text-[10px] font-bold text-gray-600 uppercase">${m.label}</span>
                </button>
            `;
        });
        moodHTML += `</div>`;
        moodHTML += `<input type="hidden" id="act-valor">`; // Input oculto para guardar el valor
        
        // Campo obs opcional
        moodHTML += `
            <div>
                <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Observación (Opcional)</label>
                <input type="text" id="act-descripcion" class="w-full border-gray-300 rounded-xl p-2.5" placeholder="Algo más que agregar...">
            </div>
        `;
        container.innerHTML = moodHTML;
    }
    // CASO C: ESTÁNDAR (Alimentación, Higiene, Tarea, etc.)
    else {
        let placeholderValor = "Ej: Todo, Normal, 38°C";
        if(typeObj.code === 'ALIMENTACION') placeholderValor = "Ej: Todo, La mitad, Poco";
        if(typeObj.code === 'SIESTA') placeholderValor = "Ej: 1 hora, 30 min, No durmió";
        
        container.innerHTML = `
            <div class="grid grid-cols-1 gap-4">
                <div>
                    <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Valor / Cantidad</label>
                    <input type="text" id="act-valor" placeholder="${placeholderValor}" class="w-full border-gray-300 rounded-xl p-2.5 focus:ring-[#DD8E0A]" dark:bg-gray-800 dark:text-white>
                </div>
                <div>
                    <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1">Detalle</label>
                    <textarea id="act-descripcion" rows="3" class="w-full border-gray-300 rounded-xl p-3" placeholder="Detalles adicionales..."></textarea>
                </div>
            </div>
        `;
        // Auto-focus
        setTimeout(() => document.getElementById('act-valor')?.focus(), 100);
    }
}

// Helpers para el formulario dinámico
window.previewFile = (input) => {
    const file = input.files[0];
    if(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const area = document.getElementById('file-preview-area');
            // Si es imagen
            if(file.type.startsWith('image/')) {
                area.innerHTML = `<img src="${e.target.result}" class="h-32 object-contain mx-auto rounded-lg shadow-sm">`;
            } else {
                area.innerHTML = `<i class="fas fa-file-video text-4xl text-green-500 mb-2"></i><p class="text-sm font-bold text-green-600">${file.name}</p>`;
            }
        };
        reader.readAsDataURL(file);
    }
}

window.selectMood = (val, btn) => {
    // UI Update
    document.querySelectorAll('.mood-btn').forEach(b => {
        b.classList.remove('ring-2', 'ring-[#DD8E0A]', 'bg-orange-100');
        b.classList.add('bg-white');
    });
    btn.classList.remove('bg-white');
    btn.classList.add('ring-2', 'ring-[#DD8E0A]', 'bg-orange-100');
    
    // Set Value
    document.getElementById('act-valor').value = val;
}

// 4. GUARDAR (Updated to FormData)
document.getElementById('form-actividad-detalle')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    let id = document.getElementById('act-alumno-id').value;
    if(!id) id = document.getElementById('act-alumno-select').value;
    
    if(!id) { showToast('Selecciona un alumno', 'error'); return; }

    const tipo = document.getElementById('act-tipo-codigo').value;
    
    // Usamos FormData para soportar archivos
    const formData = new FormData();
    formData.append('alumno_id', id);
    formData.append('fecha', document.getElementById('global-date').value);
    formData.append('tipo', tipo);
    formData.append('hora', document.getElementById('act-hora').value);
    
    // Obtener campos dinámicos (pueden no existir según el tipo)
    const valorInput = document.getElementById('act-valor');
    if(valorInput) formData.append('valor', valorInput.value);
    
    const descInput = document.getElementById('act-descripcion');
    if(descInput) formData.append('descripcion', descInput.value);
    
    const fileInput = document.getElementById('act-archivo');
    if(fileInput && fileInput.files[0]) {
        formData.append('archivo', fileInput.files[0]);
    }

    // Validación específica para Ánimo
    if(tipo === 'ANIMO' && !valorInput.value) {
        showToast('Selecciona un estado de ánimo', 'warning');
        return;
    }

    try {
        await fetchAPI(`${API_BASE}/academico/actividades`, {
            method: 'POST',
            body: formData,
            // Importante: No poner Content-Type manualmente al usar fetchAPI wrapper modificado
            // Si tu fetchAPI wrapper sobreescribe headers, asegúrate de manejar FormData
        });
        showToast('Actividad registrada', 'success');
        closeModalActividad();
        loadDiario();
    } catch(err) {
        showToast('Error al guardar', 'error');
    }
});

// ===========================
// LÓGICA PLANIFICACIÓN (NUEVO)
// ===========================

window.abrirModalPlanificacion = () => {
    document.getElementById('modal-planificacion').classList.remove('hidden');
    document.getElementById('form-planificacion').reset();
    document.getElementById('plan-file-preview').innerHTML = `
        <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 group-hover:text-primary-500 mb-2 transition"></i>
        <p class="text-sm text-gray-500 font-medium">Click para subir PDF</p>
    `;
}

window.closeModalPlanificacion = () => {
    document.getElementById('modal-planificacion').classList.add('hidden');
}

window.previewPDFName = (input) => {
    const file = input.files[0];
    if(file) {
        if(file.type !== 'application/pdf') {
            showToast('Solo se permiten archivos PDF', 'warning');
            input.value = '';
            return;
        }
        document.getElementById('plan-file-preview').innerHTML = `
            <i class="fas fa-file-pdf text-3xl text-red-500 mb-2"></i>
            <p class="text-sm text-gray-800 font-bold truncate px-4">${file.name}</p>
        `;
    }
}

document.getElementById('form-planificacion')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('duracion', document.getElementById('plan-duracion').value);
    
    const titulo = document.getElementById('plan-titulo').value;
    if(titulo) formData.append('titulo', titulo);
    
    const fileInput = document.getElementById('plan-archivo');
    if(fileInput.files[0]) {
        formData.append('archivo', fileInput.files[0]);
    }

    try {
        await fetchAPI(`${API_BASE}/academico/planificaciones`, {
            method: 'POST',
            body: formData
        });
        showToast('Planificación subida correctamente', 'success');
        closeModalPlanificacion();
    } catch(err) {
        console.error(err);
        showToast('Error al subir planificación', 'error');
    }
});


