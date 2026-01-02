import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';

window.openModal = (id) => document.getElementById(id)?.classList.remove('hidden');
window.closeModal = (id) => document.getElementById(id)?.classList.add('hidden');

async function cargarTabla(tipo) {
  const tbodyId = tipo === 'ingreso' ? 'tabla-categorias-ingresos' : 'tabla-categorias-egresos';
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="3" class="px-6 py-8 text-center text-gray-400">Cargando...</td></tr>`;

  const res = await fetchAPI(`${API_BASE}/finanzas/categorias/gestion?tipo=${tipo}`);
  const data = await res.json();

  tbody.innerHTML = '';
  if (!data || data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="3" class="px-6 py-8 text-center text-gray-400">Sin categorías.</td></tr>`;
    return;
  }

  data.forEach((c) => {
    const tr = document.createElement('tr');
    const estado = c.activo
      ? `<span class="px-2 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">ACTIVO</span>`
      : `<span class="px-2 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">INACTIVO</span>`;

    const btnLabel = c.activo ? 'Desactivar' : 'Activar';
    const btnClass = c.activo
      ? 'text-red-600 hover:underline'
      : 'text-primary-600 hover:underline';

    tr.innerHTML = `
      <td class="px-6 py-4 font-medium text-gray-900 dark:text-gray-100">${c.nombre}</td>
      <td class="px-6 py-4 text-center">${estado}</td>
      <td class="px-6 py-4 text-center">
        <button class="${btnClass}" onclick="toggleCategoria(${c.id}, '${tipo}', ${!c.activo})">${btnLabel}</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

window.toggleCategoria = async function (id, tipo, activo) {
  try {
    const res = await fetchAPI(`${API_BASE}/finanzas/categorias/${id}/estado?tipo=${tipo}&activo=${activo}`, {
      method: 'PUT',
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'No se pudo actualizar');

    showToast('Estado actualizado', 'success');
    await cargarTabla(tipo);
  } catch (e) {
    showToast(e.message, 'error');
  }
};

document.addEventListener('DOMContentLoaded', async () => {
  // Detecta por cuál tabla existe
  if (document.getElementById('tabla-categorias-ingresos')) await cargarTabla('ingreso');
  if (document.getElementById('tabla-categorias-egresos')) await cargarTabla('egreso');
});
