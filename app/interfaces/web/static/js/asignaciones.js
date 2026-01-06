import { fetchAPI, showToast, showConfirm } from './main.js';

const API_BASE = '/api/v1';
let cacheGruposParalelos = [];

// ==========================================
// INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    loadAsignaciones();
    initModalEvents();
});

function initModalEvents() {
    // Botón nueva asignación
    document.getElementById('btn-nueva-asignacion')?.addEventListener('click', () => {
        abrirModalAsignacion();
    });

    // Botones cerrar modal
    document.getElementById('btn-cerrar-modal')?.addEventListener('click', cerrarModalAsignacion);
    document.getElementById('btn-cancelar-modal')?.addEventListener('click', cerrarModalAsignacion);

    // Botón guardar
    document.getElementById('btn-guardar-modal')?.addEventListener('click', guardarAsignacion);

    // Change del select de grupo
    document.getElementById('select-grupo-asignar')?.addEventListener('change', cargarParalelosDelGrupo);
}

// ==========================================
// CARGAR TABLA (MODIFICADO: BOTÓN ELIMINAR)
// ==========================================
async function loadAsignaciones() {
    const tbody = document.getElementById('tabla-asignaciones');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-10 text-gray-500">Cargando datos...</td></tr>';
    
    try {
        const res = await fetchAPI(`${API_BASE}/asignaciones/lista`);
        const data = await res.json();
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-10 text-gray-500">No hay asignaciones registradas</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(item => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 transition border-b dark:border-gray-700">
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">
                    <div class="flex items-center gap-3">
                        <div class="w-9 h-9 rounded-full bg-[#DD8E0A]/10 text-[#DD8E0A] flex items-center justify-center font-semibold mr-3">
                            ${getInitials(item.profesora_nombre)}
                        </div>
                        ${item.profesora_nombre}
                    </div>
                </td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">${item.grupo_nombre}</td>
                <td class="px-6 py-4 font-bold text-indigo-600 dark:text-indigo-400">${item.paralelo_letra}</td>
                <td class="px-6 py-4 text-center text-gray-600 dark:text-gray-400">${item.gestion}</td>
                <td class="px-6 py-4 text-center">
                    <button onclick="window.eliminarAsignacion(${item.id})" 
                            class="bg-red-100 hover:bg-red-200 text-red-600 w-8 h-8 rounded-full shadow transition-transform hover:scale-110 flex items-center justify-center mx-auto border border-red-200" 
                            title="Quitar Asignación / Liberar Profesora">
                        <i class="fas fa-trash-alt text-xs"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        console.error(e);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-10 text-red-500">Error al cargar datos</td></tr>';
    }
}

// ==========================================
// ACCIÓN: ELIMINAR ASIGNACIÓN
// ==========================================

window.eliminarAsignacion = async function(id) {
    const confirm = await showConfirm(
        '¿Quitar asignación?',
        'La profesora quedará libre y podrá ser asignada a otro paralelo.',
        'Sí, quitar'
    );

    if (confirm.isConfirmed) {
        try {
            const res = await fetchAPI(`${API_BASE}/asignaciones/${id}`, {
                method: 'DELETE'
            });
            
            if (res.ok) {
                showToast('Asignación eliminada. La profesora está libre.', 'success');
                loadAsignaciones(); // Recargar tabla
            } else {
                showToast('No se pudo eliminar la asignación', 'error');
            }
        } catch (e) {
            console.error(e);
            showToast('Error de conexión', 'error');
        }
    }
}

// ==========================================
// LÓGICA DEL MODAL (NUEVA ASIGNACIÓN)
// ==========================================

async function abrirModalAsignacion() {
    const modal = document.getElementById('modal-asignacion-profesora');
    if (!modal) return;
    
    document.getElementById('modal-titulo').textContent = 'Asignar Aula';
    
    modal.classList.remove('hidden');
    const content = modal.querySelector('div');
    if(content) {
        content.classList.remove('scale-95', 'opacity-0');
        content.classList.add('scale-100', 'opacity-100');
    }

    // Cargar selects limpios
    await Promise.all([cargarProfesoresDisponibles(), cargarGruposYParalelos()]);
}

function cerrarModalAsignacion() {
    const modal = document.getElementById('modal-asignacion-profesora');
    if (!modal) return;

    modal.classList.add('hidden');
    
    // Reset UI
    document.getElementById('select-profesora-asignar').innerHTML = '<option value="">Cargando...</option>';
    
    const selectParalelo = document.getElementById('select-paralelo-asignar');
    if(selectParalelo) {
        selectParalelo.innerHTML = '<option value="">Esperando grupo...</option>';
        selectParalelo.disabled = true;
        selectParalelo.className = "w-full px-4 py-2.5 bg-gray-100 dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg text-gray-500 dark:text-gray-300 cursor-not-allowed";
    }
    
    const selectGrupo = document.getElementById('select-grupo-asignar');
    if(selectGrupo) selectGrupo.value = "";

    document.getElementById('msg-no-paralelos')?.classList.add('hidden');
}

// ==========================================
// CARGA DE DATOS (API)
// ==========================================

async function cargarProfesoresDisponibles() {
    const select = document.getElementById('select-profesora-asignar');
    if(!select) return;

    try {
        const res = await fetchAPI(`${API_BASE}/profesoras/disponibles`);
        const data = await res.json();
        
        select.innerHTML = '<option value="">Seleccione una profesora...</option>';
        
        if (data.length === 0) {
            select.innerHTML += '<option disabled>No hay profesoras libres</option>';
        }

        data.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.nombre_completo;
            select.appendChild(opt);
        });
    } catch (e) {
        console.error(e);
        showToast('Error al cargar profesoras', 'error');
    }
}

async function cargarGruposYParalelos() {
    try {
        const res = await fetchAPI(`${API_BASE}/academico/grupos-paralelos-tree`);
        cacheGruposParalelos = await res.json();
        
        const selectGrupo = document.getElementById('select-grupo-asignar');
        if(selectGrupo) {
            selectGrupo.innerHTML = '<option value="">Seleccione Grupo...</option>';
            cacheGruposParalelos.forEach(g => {
                const opt = document.createElement('option');
                opt.value = g.id;
                opt.textContent = g.nombre;
                selectGrupo.appendChild(opt);
            });
        }
    } catch (e) {
        console.error("Error cargando grupos", e);
        showToast('Error cargando estructura académica', 'error');
    }
}

window.cargarParalelosDelGrupo = function() {
    const selectGrupo = document.getElementById('select-grupo-asignar');
    const grupoId = parseInt(selectGrupo.value);
    const selectParalelo = document.getElementById('select-paralelo-asignar');
    const msgError = document.getElementById('msg-no-paralelos');
    
    // Reset
    if(selectParalelo) {
        selectParalelo.innerHTML = '<option value="">Seleccione Paralelo...</option>';
        selectParalelo.disabled = true;
        selectParalelo.className = "w-full px-4 py-2.5 bg-gray-100 dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg text-gray-500 dark:text-gray-300 cursor-not-allowed";
    }
    if(msgError) msgError.classList.add('hidden');

    if (!grupoId) return;

    const grupo = cacheGruposParalelos.find(g => g.id === grupoId);
    
    if (grupo && grupo.paralelos && grupo.paralelos.length > 0) {
        selectParalelo.disabled = false;
        selectParalelo.className = "w-full px-4 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500";

        grupo.paralelos.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.nombre;
            selectParalelo.appendChild(opt);
        });
    } else {
        if(msgError) msgError.classList.remove('hidden');
    }
}

async function guardarAsignacion() {
    const profesorId = document.getElementById('select-profesora-asignar').value;
    const paraleloId = document.getElementById('select-paralelo-asignar').value;

    if (!profesorId || !paraleloId) {
        showToast('Debe seleccionar Profesora y Paralelo', 'warning');
        return;
    }

    const btnGuardar = document.getElementById('btn-guardar-modal');
    const originalText = btnGuardar ? btnGuardar.innerHTML : 'Guardar';
    
    if(btnGuardar) {
        btnGuardar.disabled = true;
        btnGuardar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    }

    try {
        const res = await fetchAPI(`${API_BASE}/asignar-profesor-paralelo`, {
            method: 'POST',
            body: JSON.stringify({ profesor_id: profesorId, paralelo_id: paraleloId })
        });
        
        const data = await res.json();
        
        if (res.ok) {
            showToast('Asignación guardada correctamente', 'success');
            cerrarModalAsignacion();
            loadAsignaciones(); // Recargar la tabla
        } else {
            showToast(data.detail || data.message || 'Error al guardar', 'error');
        }
    } catch (e) {
        console.error(e);
        showToast('Error de conexión con el servidor', 'error');
    } finally {
        if(btnGuardar) {
            btnGuardar.disabled = false;
            btnGuardar.innerHTML = originalText;
        }
    }
}

function getInitials(name) {
    if (!name) return '?';
    const parts = name.trim().split(' ');
    if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
    return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase();
}