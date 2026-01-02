import { fetchAPI, showToast } from './main.js'; // Ruta en la misma carpeta raíz
const API_BASE = '/api/v1';

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    loadGruposForSelect();
    
    document.getElementById('search-paralelo')?.addEventListener('input', (e) => loadData(e.target.value));
    document.getElementById('form-paralelo')?.addEventListener('submit', handleFormSubmit);
});

// --- FUNCIONES GLOBALES ---
window.openModal = (id) => document.getElementById(id).classList.remove('hidden');
window.closeModal = (id) => document.getElementById(id).classList.add('hidden');

window.nuevoParalelo = () => {
    limpiarFormulario();
    window.openModal('modal-paralelo');
}

window.editarParalelo = async (id) => {
    try {
        const res = await fetchAPI(`${API_BASE}/paralelos/${id}`);
        if (!res.ok) throw new Error("Error al obtener datos");
        const data = await res.json();
        
        // Llenar Modal
        document.getElementById('paralelo-id').value = data.id;
        document.getElementById('paralelo-grupo').value = data.grupo_id; // Select
        document.getElementById('paralelo-letra').value = data.letra;
        document.getElementById('paralelo-capacidad').value = data.capacidad;
        document.getElementById('paralelo-activo').checked = data.activo;
        
        // Cambiar título
        document.getElementById('modal-title').textContent = "Editar Paralelo";
        window.openModal('modal-paralelo');
        
    } catch (error) {
        console.error(error);
        showToast('No se pudo cargar la información', 'error');
    }
};

// --- LÓGICA PRIVADA ---

function limpiarFormulario() {
    const form = document.getElementById('form-paralelo');
    form.reset();
    document.getElementById('paralelo-id').value = "";
    document.getElementById('modal-title').textContent = "Nuevo Paralelo";
    document.getElementById('paralelo-activo').checked = true;
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
        data.activo = document.getElementById('paralelo-activo').checked;
        
        const id = data.id; 
        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_BASE}/paralelos/${id}` : `${API_BASE}/paralelos`;

        const res = await fetchAPI(url, { method: method, body: JSON.stringify(data) });
        
        if(res.ok) {
            showToast(id ? 'Paralelo actualizado' : 'Paralelo creado', 'success');
            window.closeModal('modal-paralelo');
            loadData();
        } else {
            const errData = await res.json();
            showToast(errData.detail || 'Error al guardar', 'error');
        }
    } catch(err) { showToast('Error de conexión', 'error'); } 
    finally { btn.disabled = false; btn.innerHTML = originalText; }
}

async function loadGruposForSelect() {
    try {
        const res = await fetchAPI(`${API_BASE}/grupos`);
        const data = await res.json();
        const sel = document.getElementById('paralelo-grupo'); // ID corregido
        if(sel && data.items) {
            sel.innerHTML = '<option value="">Seleccione grupo...</option>' + 
                data.items.map(g => `<option value="${g.id}">${g.nombre}</option>`).join('');
        }
    } catch(e) { console.error("Error cargando grupos", e); }
}

async function loadData(search = '') {
    const tbody = document.getElementById('tbody-paralelos');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4">Cargando...</td></tr>';
    
    try {
        const res = await fetchAPI(`${API_BASE}/paralelos?search=${search}`);
        const data = await res.json();
        
        if (!data.items || data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-gray-500 dark:text-gray-400">No hay paralelos registrados</td></tr>';
            return;
        }

        tbody.innerHTML = data.items.map(item => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b dark:border-gray-700">
                <td class="px-6 py-4 font-bold text-indigo-600 dark:text-indigo-400">${item.letra}</td>
                <td class="px-6 py-4 text-gray-900 dark:text-white">${item.grupo}</td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">${item.capacidad}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${item.activo ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}">
                        ${item.activo ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="px-6 py-4 text-right">
                    <button onclick="editarParalelo(${item.id})" class="text-primary-600 hover:text-primary-700 dark:text-primary-600 dark:hover:text-primary-700 transition-colors" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch(e) { 
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-red-500">Error al cargar</td></tr>'; 
    }
}