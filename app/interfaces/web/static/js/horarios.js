import { fetchAPI, showToast } from './main.js'; // Ajusta la ruta si no usas carpetas
const API_BASE = '/api/v1/academico';

document.addEventListener('DOMContentLoaded', () => {
    loadData();
    document.getElementById('search-horario')?.addEventListener('input', (e) => loadData(e.target.value));
    
    // Form Submit
    document.getElementById('form-horario')?.addEventListener('submit', handleFormSubmit);
});

// --- FUNCIONES GLOBALES ---
window.openModal = (id) => document.getElementById(id).classList.remove('hidden');
window.closeModal = (id) => document.getElementById(id).classList.add('hidden');

window.nuevoHorario = () => {
    limpiarFormulario();
    window.openModal('modal-horario');
}

window.editarHorario = async (id) => {
    try {
        const res = await fetchAPI(`${API_BASE}/horarios/${id}`);
        if (!res.ok) throw new Error("Error al obtener datos");
        const data = await res.json();
        
        // Llenar Modal
        document.getElementById('horario-id').value = data.id;
        document.getElementById('horario-nombre').value = data.nombre;
        document.getElementById('horario-inicio').value = data.hora_inicio;
        document.getElementById('horario-fin').value = data.hora_fin;
        
        document.getElementById('modal-title').textContent = "Editar Horario";
        window.openModal('modal-horario');
        
    } catch (error) {
        console.error(error);
        showToast('No se pudo cargar la información', 'error');
    }
};

// --- LÓGICA PRIVADA ---
function limpiarFormulario() {
    const form = document.getElementById('form-horario');
    form.reset();
    document.getElementById('horario-id').value = "";
    document.getElementById('modal-title').textContent = "Nuevo Horario";
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
        
        const id = data.id; 
        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_BASE}/horarios/${id}` : `${API_BASE}/horarios`;

        const res = await fetchAPI(url, { method: method, body: JSON.stringify(data) });
        
        if(res.ok) {
            showToast(id ? 'Horario actualizado' : 'Horario creado', 'success');
            window.closeModal('modal-horario');
            loadData();
        } else {
            const errData = await res.json();
            showToast(errData.detail || 'Error al guardar', 'error');
        }
    } catch(err) { showToast('Error de conexión', 'error'); }
    finally { btn.disabled = false; btn.innerHTML = originalText; }
}

async function loadData(search = '') {
    const tbody = document.getElementById('tbody-horarios');
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4">Cargando...</td></tr>';
    
    try {
        const res = await fetchAPI(`${API_BASE}/horarios?search=${search}`);
        const data = await res.json();
        
        if (!data.items || data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-gray-500">No hay horarios registrados</td></tr>';
            return;
        }

        tbody.innerHTML = data.items.map(item => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b dark:border-gray-700 transition-colors">
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">${item.nombre}</td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">${item.hora_inicio}</td>
                <td class="px-6 py-4 text-gray-700 dark:text-gray-300">${item.hora_fin}</td>
                <td class="px-6 py-4 text-right">
                    <button onclick="editarHorario(${item.id})" class="text-teal-600 hover:text-teal-800 dark:text-teal-400 dark:hover:text-teal-300 transition-colors" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    } catch(e) { tbody.innerHTML = '<tr><td colspan="4" class="text-center text-red-500">Error al cargar datos</td></tr>'; }
}
