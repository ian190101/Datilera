import { fetchAPI, showToast } from './main.js'; // Ruta en misma carpeta raíz
const API_BASE = '/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    document.getElementById('search-turno')?.addEventListener('input', (e) => loadData(e.target.value));
    document.getElementById('form-turno')?.addEventListener('submit', handleFormSubmit);
});

// --- FUNCIONES GLOBALES ---
window.openModal = (id) => document.getElementById(id).classList.remove('hidden');
window.closeModal = (id) => document.getElementById(id).classList.add('hidden');

window.nuevoTurno = () => {
    limpiarFormulario();
    window.openModal('modal-turno');
}

window.editarTurno = async (id) => {
    try {
        const res = await fetchAPI(`${API_BASE}/turnos/${id}`);
        if (!res.ok) throw new Error("Error al obtener datos");
        const data = await res.json();
        
        // Llenar Modal con los IDs correctos
        document.getElementById('turno-id').value = data.id;
        document.getElementById('turno-nombre').value = data.nombre;
        document.getElementById('turno-inicio').value = data.hora_inicio;
        document.getElementById('turno-fin').value = data.hora_fin;
        document.getElementById('turno-activo').checked = data.activo;
        
        // Cambiar título
        document.getElementById('modal-title').textContent = "Editar Turno";
        window.openModal('modal-turno');
        
    } catch (error) {
        console.error(error);
        showToast('No se pudo cargar la información', 'error');
    }
};

// --- LÓGICA PRIVADA ---

function limpiarFormulario() {
    const form = document.getElementById('form-turno');
    form.reset();
    document.getElementById('turno-id').value = "";
    document.getElementById('modal-title').textContent = "Nuevo Turno";
    document.getElementById('turno-activo').checked = true;
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
        data.activo = document.getElementById('turno-activo').checked;
        
        const id = data.id; 
        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_BASE}/turnos/${id}` : `${API_BASE}/turnos`;

        const res = await fetchAPI(url, { method: method, body: JSON.stringify(data) });
        
        if(res.ok) {
            showToast(id ? 'Turno actualizado' : 'Turno creado', 'success');
            window.closeModal('modal-turno');
            loadData();
        } else {
            const errData = await res.json();
            showToast(errData.detail || 'Error al guardar', 'error');
        }
    } catch(err) { showToast('Error de conexión', 'error'); } 
    finally { btn.disabled = false; btn.innerHTML = originalText; }
}

async function loadData(search = '') {
    const tbody = document.getElementById('tbody-turnos');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4">Cargando...</td></tr>';
    
    try {
        const res = await fetchAPI(`${API_BASE}/turnos?search=${search}`);
        const data = await res.json();
        
        if (!data.items || data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-gray-500 dark:text-gray-400">No hay turnos registrados</td></tr>';
            return;
        }

        tbody.innerHTML = data.items.map(item => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b dark:border-gray-700">
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">${item.nombre}</td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">${item.hora_inicio}</td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">${item.hora_fin}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${item.activo ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}">
                        ${item.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="px-6 py-4 text-right">
                    <button onclick="editarTurno(${item.id})" class="text-primary-600 hover:text-primary-700 dark:text-primary-600 dark:hover:text-primary-700 transition-colors" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch(e) { 
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-red-500">Error al cargar datos</td></tr>'; 
    }
}