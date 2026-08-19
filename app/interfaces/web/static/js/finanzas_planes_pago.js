import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';
window.openModal = (id) => document.getElementById(id)?.classList.remove('hidden');
window.closeModal = (id) => document.getElementById(id)?.classList.add('hidden');

function fmtMoney(n) {
  const v = Number(n || 0);
  return `Bs. ${v.toFixed(2)}`;
}

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
    await cargarAlumnosPlan();
});

async function cargarAlumnosPlan() {
  try {
      const res = await fetchAPI(`${API_BASE}/alumnos-select/lista`);
      const alumnos = await res.json();
    
      const sel = document.getElementById('pp_alumno_id');
      if (!sel) return;
    
      sel.innerHTML = `<option value="">Seleccione un alumno...</option>`;
      alumnos.forEach((a) => {
        const opt = document.createElement('option');
        opt.value = a.id;
        opt.textContent = a.nombre;
        sel.appendChild(opt);
      });
  } catch (e) {
      console.error("Error cargando alumnos:", e);
  }
}

window.cargarPlanPagoAlumno = async function () {
  const alumnoId = document.getElementById('pp_alumno_id')?.value;
  const tbody = document.getElementById('tabla-pp-body'); // Asegúrate que este ID exista en tu HTML
  
  if (!tbody) return;

  if (!alumnoId) {
    tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-gray-400">Seleccione un alumno primero.</td></tr>`;
    return;
  }

  tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-gray-400">Cargando plan...</td></tr>`;

  try {
    const res = await fetchAPI(`${API_BASE}/finanzas/planes-pago/gestion/alumno/${alumnoId}`);
    const data = await res.json();

    if (!data.tiene_plan) {
      tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-yellow-600">Este alumno no tiene un plan generado aún. <br><a href="/finanzas" class="underline">Ir a crear plan</a></td></tr>`;
      return;
    }

    const cuotas = data.cuotas || [];
    tbody.innerHTML = '';

    cuotas.forEach((c) => {
      // Definir colores según estado
      let badgeColor = 'bg-gray-100 text-gray-800';
      if (c.estado === 'PAGADA') badgeColor = 'bg-green-100 text-green-800';
      if (c.estado === 'PENDIENTE') badgeColor = 'bg-yellow-100 text-yellow-800';
      if (c.estado === 'MORA') badgeColor = 'bg-red-100 text-red-800 font-bold';

      const tr = document.createElement('tr');
      tr.className = "border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700";
      
      tr.innerHTML = `
        <td class="px-6 py-4 font-medium">Cuota ${c.numero} <span class="text-xs text-gray-500">(${c.mes})</span></td>
        <td class="px-6 py-4">${c.vencimiento}</td>
        <td class="px-6 py-4 text-right">${fmtMoney(c.monto_total)}</td>
        <td class="px-6 py-4 text-center">
            <span class="px-2 py-1 text-xs rounded ${badgeColor}">${c.estado}</span>
        </td>
        <td class="px-6 py-4 text-right text-sm">
            ${c.saldo > 0 ? `<span class="text-red-500">Debe: ${fmtMoney(c.saldo)}</span>` : '<span class="text-green-500">Completo</span>'}
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch (e) {
    console.error(e);
    tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-red-500">Error al cargar datos.</td></tr>`;
  }
}
