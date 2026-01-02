import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    document.getElementById('search-grupo')?.addEventListener('input', (e) => loadData(e.target.value));
    
    // Configurar envío del formulario
    document.getElementById('form-grupo')?.addEventListener('submit', handleFormSubmit);
});

// --- FUNCIONES GLOBALES ---

window.openModal = (id) => {
    document.getElementById(id).classList.remove('hidden');
    // CORRECCIÓN: Quitamos la llamada a limpiarFormulario() de aquí
}

window.closeModal = (id) => {
    document.getElementById(id).classList.add('hidden');
}

// Nueva función para el botón "Nuevo Grupo"
window.nuevoGrupo = () => {
    limpiarFormulario(); // Borra datos viejos
    window.openModal('modal-grupo'); // Abre el modal limpio
}

window.editarGrupo = async (id) => {
    try {
        const res = await fetchAPI(`${API_BASE}/grupos/${id}`);
        if (!res.ok) throw new Error("Error al obtener datos");
        const data = await res.json();
        
        // 1. Llenar Modal
        document.getElementById('grupo-id').value = data.id;
        document.getElementById('grupo-nombre').value = data.nombre;
        document.getElementById('grupo-gestion').value = data.gestion;
        document.getElementById('grupo-activo').checked = data.activo;
        
        // 2. Cambiar título
        document.getElementById('modal-title').textContent = "Editar Grupo";
        
        // 3. Abrir Modal (Ahora ya no se borrará)
        window.openModal('modal-grupo');
        
    } catch (error) {
        console.error(error);
        showToast('No se pudo cargar la información', 'error');
    }
};

// --- LÓGICA PRIVADA ---

function limpiarFormulario() {
    const form = document.getElementById('form-grupo');
    form.reset();
    document.getElementById('grupo-id').value = ""; // Limpiar ID
    document.getElementById('modal-title').textContent = "Nuevo Grupo";
    document.getElementById('grupo-activo').checked = true;
}

async function handleFormSubmit(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

    try {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());
        data.activo = document.getElementById('grupo-activo').checked;
        
        const id = data.id; 
        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_BASE}/grupos/${id}` : `${API_BASE}/grupos`;

        const res = await fetchAPI(url, { method: method, body: JSON.stringify(data) });
        
        if(res.ok) {
            showToast(id ? 'Grupo actualizado' : 'Grupo creado', 'success');
            window.closeModal('modal-grupo');
            loadData();
        } else {
            const errData = await res.json();
            showToast(errData.detail || 'Error al guardar', 'error');
        }
    } catch(err) { showToast('Error de conexión', 'error'); } 
    finally { btn.disabled = false; btn.innerHTML = originalText; }
}

async function loadData(search = '') {
    const tbody = document.getElementById('tbody-grupos');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4">Cargando...</td></tr>';
    
    try {
        const res = await fetchAPI(`${API_BASE}/grupos?search=${search}`);
        const data = await res.json();
        
        if (!data.items || data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-gray-500">No hay grupos</td></tr>';
            return;
        }

        tbody.innerHTML = data.items.map(item => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b dark:border-gray-700">
                <td class="px-6 py-4 dark:text-white">${item.nombre}</td>
                <td class="px-6 py-4 dark:text-gray-300">${item.gestion}</td>
                <td class="px-6 py-4 text-gray-500 dark:text-gray-400">${item.creado_en}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${item.activo ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}">
                        ${item.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="px-6 py-4 text-right">
                    <button onclick="editarGrupo(${item.id})" class="text-primary-600 hover:primary-blue-400"><i class="fas fa-edit"></i></button>
                </td>
                
            </tr>
        `).join('');
    } catch(e) { tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red-500">Error</td></tr>'; }
}