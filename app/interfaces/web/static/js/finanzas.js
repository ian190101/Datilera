// app/interfaces/web/static/js/finanzas.js
import { fetchAPI, showToast, showConfirm } from './main.js';

const API_BASE = '/api/v1';
let currentTab = 'pagos';

window.openModal = (id) => document.getElementById(id)?.classList.remove('hidden');
window.closeModal = (id) => document.getElementById(id)?.classList.add('hidden');

function fmtMoney(n) {
  const v = Number(n || 0);
  return `Bs. ${v.toFixed(2)}`;
}

function todayISO() {
  return new Date().toISOString().split('T')[0];
}

async function fetchForm(url, { method = 'POST', formData }) {
  const res = await fetch(url, {
    method,
    credentials: 'include',
    body: formData,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || data.detail || 'Error de servidor');
  return data;
}

/* ========================= INIT ========================= */
document.addEventListener('DOMContentLoaded', async () => {
  const hoy = todayISO();
  const f1 = document.getElementById('pago_fecha');
  const f2 = document.getElementById('gasto_fecha');
  if (f1) f1.value = hoy;
  if (f2) f2.value = hoy;

  await cargarListaAlumnos();
  await cargarCategoriasParaFormularios();
  await cargarArqueoResumen();
  await cambiarTab('pagos');
});

/* ========================= TABS ========================= */
window.cambiarTab = async function (tabName) {
  currentTab = tabName;

  // 1. Definir las clases exactas (Doradas para activo, Gris claro para inactivo)
  const inactiveClass = 'inline-block p-4 border-b-2 border-transparent rounded-t-lg transition-colors text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300';
  
  const activeClass = 'inline-block p-4 border-b-2 rounded-t-lg transition-colors border-[#DD8E0A] text-[#DD8E0A] dark:text-[#DD8E0A] dark:border-[#DD8E0A]';

  // 2. Resetear todos los tabs a inactivos
  document.querySelectorAll('[id^="tab-"]').forEach((el) => {
    el.className = inactiveClass;
  });

  // 3. Activar el tab seleccionado
  const tabEl = document.getElementById(`tab-${tabName}`);
  if (tabEl) {
      tabEl.className = activeClass;
  }

  // 4. Mostrar/Ocultar Vistas
  ['pagos', 'deudas', 'arqueo', 'sueldos', 'movimientos'].forEach((v) => {
    const el = document.getElementById(`vista-${v}`);
    if (el) el.classList.add('hidden');
  });
  document.getElementById(`vista-${tabName}`)?.classList.remove('hidden');

  // 5. Cargar datos según el tab
  // Nota: He agrupado las llamadas para asegurar que se ejecuten en orden
  if (tabName === 'pagos') {
      await cargarHistorial();
  }
  if (tabName === 'deudas') {
      await cargarListaDeudores();
  }
  if (tabName === 'sueldos') {
      await cargarReporteSueldos();
  }
  
  // Siempre actualizar el resumen de caja (si esa era tu intención original)
  await cargarArqueoResumen();
};

/* ========================= ALUMNOS / CUOTAS ========================= */
async function cargarListaAlumnos() {
  try {
    const response = await fetchAPI(`${API_BASE}/alumnos-select/lista`);
    const data = await response.json();
    const alumnos = Array.isArray(data) ? data : (data.items || []);

    const selPago = document.getElementById('pago_alumno_id');
    const selPlan = document.getElementById('plan_alumno_id');

    if (selPago) {
      selPago.innerHTML = `<option value="">Seleccione un alumno...</option>`;
      alumnos.forEach((a) => {
        const opt = document.createElement('option');
        opt.value = a.id;
        opt.textContent = a.nombre;
        selPago.appendChild(opt);
      });
    }

    if (selPlan) {
      selPlan.innerHTML = `<option value="">Seleccione un alumno...</option>`;
      alumnos.forEach((a) => {
        const opt = document.createElement('option');
        opt.value = a.id;
        opt.textContent = a.nombre;
        selPlan.appendChild(opt);
      });
    }
  } catch (e) {
    console.error("Error cargando alumnos:", e);
  }
}

window.cargarCuotasDelAlumno = async function () {
  const alumnoId = document.getElementById('pago_alumno_id')?.value;
  const selectCuotas = document.getElementById('pago_cuota_id');
  if (!selectCuotas) return;

  if (!alumnoId) {
    selectCuotas.innerHTML = `<option value="">Seleccione primero al alumno...</option>`;
    return;
  }

  try {
    const response = await fetchAPI(`${API_BASE}/finanzas/alumno/${alumnoId}/cuotas-pendientes`);
    const data = await response.json();
    const cuotas = Array.isArray(data) ? data : [];

    selectCuotas.innerHTML = `<option value="">Seleccione qué pagar...</option>`;
    if (cuotas.length === 0) {
      selectCuotas.innerHTML = `<option value="">Al día (sin cuotas pendientes)</option>`;
      return;
    }

    cuotas.forEach((c) => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.dataset.monto = c.monto;
      opt.textContent = `${c.detalle || 'Cuota'} - Saldo: Bs. ${c.monto}`;
      selectCuotas.appendChild(opt);
    });
  } catch (e) {
    console.error(e);
  }
};

window.actualizarMontoPagar = function () {
  const select = document.getElementById('pago_cuota_id');
  const montoInput = document.getElementById('pago_monto');
  if (!select || !montoInput) return;

  const opt = select.options[select.selectedIndex];
  if (opt?.dataset?.monto) {
    // Convertir a número y reemplazar coma por punto
    let montoStr = String(opt.dataset.monto).replace(',', '.');
    let montoNum = parseFloat(montoStr);

    if (!isNaN(montoNum)) {
      montoInput.value = montoNum.toFixed(2); // o simplemente montoNum si prefieres sin formato
    } else {
      montoInput.value = ''; // o valor por defecto
    }
  }
};

window.toggleCamposComprobante = function () {
  const metodo = document.getElementById('pago_metodo')?.value;
  const div = document.getElementById('div-comprobante');
  if (!div) return;
  if (metodo === 'QR' || metodo === 'TRANSFERENCIA') div.classList.remove('hidden');
  else div.classList.add('hidden');
};

/* ========================= CATEGORÍAS ========================= */
async function cargarCategoriasParaFormularios() {
  try {
    const [ingRes, egrRes] = await Promise.all([
      fetchAPI(`${API_BASE}/finanzas/categorias/gestion?tipo=ingreso`),
      fetchAPI(`${API_BASE}/finanzas/categorias/gestion?tipo=egreso`),
    ]);
    const ingreso = await ingRes.json();
    const egreso = await egrRes.json();

    const selIngreso = document.getElementById('pago_categoria_id');
    if (selIngreso && Array.isArray(ingreso)) {
      selIngreso.innerHTML = `<option value="">Seleccione...</option>`;
      ingreso.filter((c) => c.activo).forEach((c) => {
          const opt = document.createElement('option');
          opt.value = c.id;
          opt.textContent = c.nombre;
          selIngreso.appendChild(opt);
        });
    }

    const selEgreso = document.getElementById('gasto_categoria');
    if (selEgreso && Array.isArray(egreso)) {
      selEgreso.innerHTML = `<option value="">Seleccione...</option>`;
      egreso.filter((c) => c.activo).forEach((c) => {
          const opt = document.createElement('option');
          opt.value = c.nombre;
          opt.textContent = c.nombre;
          selEgreso.appendChild(opt);
        });
    }
  } catch (e) {
    console.error("Error cargando categorías:", e);
  }
}

window.submitCategoria = async function (e, tipo) {
    e.preventDefault();
    const form = e.target;
    const nombre = form.nombre.value.trim();
    
    if (!nombre) {
        showToast('Ingrese un nombre para la categoría', 'error');
        return;
    }
    
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    
    try {
        btn.disabled = true;
        btn.textContent = 'Guardando...';
        
        const response = await fetch(`${API_BASE}/finanzas/categorias/crear`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nombre, tipo })
        });
        
        const data = await response.json();
        
        // ✅ IMPORTANTE: Verificar si la respuesta es exitosa
        if (!response.ok) {
            // El servidor devolvió un error (400, 500, etc.)
            throw new Error(data.detail || data.message || 'No se pudo crear la categoría');
        }
        
        // ✅ Éxito
        showToast('Categoría creada exitosamente', 'success');
        form.reset();
        closeModal(tipo === 'ingreso' ? 'modal-cat-ingreso' : 'modal-cat-egreso');
        
        // Recargar las categorías en los formularios
        await cargarCategoriasParaFormularios();
        
    } catch (err) {
        // ✅ Mostrar el error con SweetAlert2
        console.error('Error creando categoría:', err);
        showToast(err.message, 'error');
        
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
};


/* ========================= PAGO (INGRESO) ========================= */
window.guardarPago = async function (e) {
  e.preventDefault();
  const form = document.getElementById('form-pago');
  const btn = form.querySelector('button[type="submit"]');
  const original = btn.textContent;

  try {
    btn.disabled = true; btn.textContent = 'Procesando...';
    const fd = new FormData(form);
    await fetchForm(`${API_BASE}/ingresos/cobrar`, { method: 'POST', formData: fd });
    showToast('Ingreso registrado', 'success');
    closeModal('modal-pago');
    form.reset();
    await cargarHistorial();
    await cargarArqueoResumen();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false; btn.textContent = original;
  }
};

/* ========================= GASTO (EGRESO) ========================= */
window.guardarGasto = async function (e) {
  e.preventDefault();
  const form = document.getElementById('form-gasto');
  const btn = form.querySelector('button[type="submit"]');
  const original = btn.textContent;

  try {
    btn.disabled = true; btn.textContent = 'Procesando...';
    const fd = new FormData(form);
    await fetchForm(`${API_BASE}/finanzas/gastos`, { method: 'POST', formData: fd });
    showToast('Egreso registrado', 'success');
    closeModal('modal-gasto');
    form.reset();
    await cargarHistorial();
    if (currentTab === 'arqueo') await cargarArqueoResumen();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false; btn.textContent = original;
  }
};

/* ========================= PLAN DE PAGO ========================= */
window.submitPlanPago = async function (e) {
  e.preventDefault();
  const form = document.getElementById('form-plan-pago');
  const btn = form.querySelector('button[type="submit"]');
  const original = btn.textContent;

  try {
    btn.disabled = true;
    btn.textContent = 'Generando...';

    // OJO: tu HTML tiene name="alumnoid" (NO alumno_id)
    const alumnoid = Number(form.elements['alumnoid']?.value || 0);
    if (!alumnoid) throw new Error('Seleccione un alumno');

    // OJO: tu HTML tiene name="fecha_ingreso" (NO fechaingreso)
    const fecha_ingreso = form.elements['fecha_ingreso']?.value;
    if (!fecha_ingreso) throw new Error('Seleccione la fecha de ingreso');

    const mensualidad = Number(form.elements['mensualidad']?.value || 0);
    if (!mensualidad) throw new Error('Ingrese la mensualidad');

    const incluyeMaterial = (form.elements['incluye_material']?.value || 'SI').toUpperCase();

    const payload = {
      // Backend actual espera alumnoid / fechaingreso / montomaterial / tipopago
      alumnoid,
      fechaingreso: fecha_ingreso,
      mensualidad,
      montomaterial:
        incluyeMaterial === 'SI'
          ? Number(form.elements['monto_material']?.value || 3400)
          : 0,
      tipopago: form.elements['tipo_pago']?.value || 'MENSUAL',
      // montomerienda: 0, // si luego agregas campo en HTML, aquí lo conectas
    };

    const res = await fetchAPI(`${API_BASE}/finanzas/planes-pago/generar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || data.message || 'No se pudo generar el plan');

    showToast(data.mensaje || 'Plan generado', 'success');
    closeModal('modal-plan-pago');
    form.reset();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = original;
  }
};


/* ========================= HISTORIAL (Pestaña Principal) ========================= */

async function cargarHistorial() {
    const tbody = document.getElementById('tabla-historial-body');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-gray-500">Cargando movimientos del día...</td></tr>`;

    try {
        // Consultamos movimientos de HOY
        const hoy = new Date().toISOString().split('T')[0];
        const res = await fetchAPI(`${API_BASE}/finanzas/movimientos?fecha_desde=${hoy}&fecha_hasta=${hoy}&limit=50`);
        
        if (!res.ok) throw new Error("Error cargando historial");
        
        const data = await res.json();
        const items = data.items || [];

        if (items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-gray-400">No hay movimientos registrados hoy.</td></tr>`;
            return;
        }

        tbody.innerHTML = items.map(m => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700">
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">${m.fecha}</td>
                
                <td class="px-4 py-3">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${
                        m.tipo === 'INGRESO' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'}
                    }">
                        ${m.tipo}
                    </span>
                </td>
                
                <td class="px-4 py-3 text-sm text-gray-900 dark:text-white font-medium">
                    ${m.detalle} <span class="text-xs text-gray-400 block">${m.categoria || ''}</span>
                </td>

                <td class="px-4 py-3">
                    <span class="px-2 py-1 rounded bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300">
                        ${m.metodo}
                    </span>
                </td>

                <td class="px-6 py-3 text-right">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${
                        m.tipo === 'INGRESO' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    }">
                        ${fmtMoney(m.monto)}
                    </span>
                </td> 

                <td class="px-6 py-3 text-center">
                    ${m.tipo === 'INGRESO' && m.pago_id ? `
                        <button onclick="descargarRecibo(${m.pago_id})" 
                                class="text-gray-400 hover:text-primary-600 transition-colors" 
                                title="Descargar Recibo">
                            <i class="fas fa-file-pdf fa-lg"></i>
                        </button>
                    ` : '<span class="text-gray-300">-</span>'}
                </td>
                
               

            </tr>
        `).join('');

    } catch (error) {
        console.error('Error historial:', error);
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-red-500 py-4">Error de conexión</td></tr>`;
    }
}


// Función auxiliar para descargar recibos
window.descargarRecibo = async function(pagoId) {
    try {
        window.open(`${API_BASE}/finanzas/recibo/${pagoId}`, '_blank');
        showToast('Descargando recibo...', 'success');
    } catch (e) {
        showToast('Error al descargar recibo', 'error');
    }
};


async function cargarArqueoResumen() {
  const cont = document.getElementById('reporte-eeff-container');
  if (!cont) return;
  cont.innerHTML = `<div class="text-gray-400 text-center py-8">Cargando Estados Financieros...</div>`;
  const now = new Date();
  
  try {
    const res = await fetchAPI(`${API_BASE}/finanzas/arqueo?mes=${now.getMonth()+1}&anio=${now.getFullYear()}`);
    const data = await res.json();
    actualizarCards(data)

    let htmlIngresos = '';
    for (const [concepto, monto] of Object.entries(data.detalles_ingreso || {})) {
        htmlIngresos += `<li class="flex justify-between border-b border-gray-100 dark:border-gray-700 py-1"><span>${concepto}</span><span class="font-mono text-gray-700 dark:text-gray-700">${fmtMoney(monto)}</span></li>`;
    }

    let htmlGastos = '';
    (data.detalles_gasto || []).forEach(g => {
        htmlGastos += `<li class="flex justify-between border-b border-gray-100 dark:border-gray-700 py-1"><span>${g.categoria}</span><span class="font-mono text-gray-700 dark:text-gray-700">${fmtMoney(g.monto)}</span></li>`;
    });

    cont.innerHTML = `
      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
        <h3 class="text-xl font-bold mb-4 dark:text-white">EEFF - ${now.getMonth()+1}/${now.getFullYear()}</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div class="bg-green-50 p-4 rounded-lg"><h4 class="font-bold text-green-700 mb-2">INGRESOS</h4><ul>${htmlIngresos}</ul><div class="mt-4 font-bold text-right text-green-800">TOTAL: ${fmtMoney(data.resumen?.ingreso_real)}</div></div>
          <div class="bg-red-50 p-4 rounded-lg"><h4 class="font-bold text-red-700 mb-2">EGRESOS</h4><ul>${htmlGastos}</ul><div class="mt-4 font-bold text-right text-red-800">TOTAL: ${fmtMoney(data.resumen?.total_gastos)}</div></div>
        </div>
        <div class="mt-6 p-4 rounded-xl text-center bg-primary-600 text-white shadow-lg"><div class="text-sm uppercase">Utilidad Operativa</div><div class="text-3xl font-bold mt-1">${fmtMoney(data.resumen?.utilidad)}</div></div>
      </div>
    `;
  } catch (e) {
    console.error(e);
    cont.innerHTML = `<div class="text-red-500 text-center py-4">Error cargando reporte.</div>`;
  }
}

// Cargar lista de deudores
// Cargar lista de deudores (CORREGIDO)
window.cargarListaDeudores = async function() {
    const tbody = document.getElementById('tabla-deudas-body'); // OJO: Verifica si tu HTML usa 'tabla-deudas-body' o 'tabla-deudores'
    // En tu código anterior usabas 'tabla-deudores', asegúrate que coincida con el ID en tu HTML
    // Si en tu HTML es id="tabla-deudores", cambia la línea de arriba.
    
    // Vamos a intentar buscar ambos por si acaso
    const targetTable = document.getElementById('tabla-deudas-body') || document.getElementById('tabla-deudores');

    if (!targetTable) {
        console.error("No se encontró la tabla de deudores en el HTML");
        return;
    }
    
    targetTable.innerHTML = '<tr><td colspan="5" class="text-center py-4">Consultando deudas...</td></tr>';
    
    try {
        const res = await fetchAPI(`${API_BASE}/finanzas/deudores`);
        
        if (!res.ok) throw new Error("Error al consultar API");

        const data = await res.json();
        
        // ✅ CORRECCIÓN CRÍTICA:
        // El backend devuelve una lista directa [ ... ], no { items: ... }
        // Aquí validamos ambas formas para que no falle.
        const listaDeudores = Array.isArray(data) ? data : (data.items || []);
        
        if (listaDeudores.length === 0) {
            targetTable.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-green-600 font-medium">¡Excelente! No existen deudas registradas.</td></tr>';
            return;
        }
        
        targetTable.innerHTML = listaDeudores.map(d => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700">
                <td class="px-4 py-3 font-medium text-gray-900 dark:text-white">
                    ${d.nombrecompleto || d.alumno_nombre}
                </td>
                <td class="px-4 py-3 text-sm text-gray-500 dark:text-gray-300">
                    ${d.concepto}
                </td>
                <td class="px-4 py-3 text-center">
                    <span class="px-2 py-1 text-xs rounded font-bold ${d.diasatraso > 30 ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'}">
                        ${d.diasatraso || d.dias_atraso} días
                    </span>
                </td>
                <td class="px-4 py-3 text-right font-mono font-bold text-red-600">
                    ${fmtMoney(d.totalexigible || d.monto_deuda || d.monto)}
                </td>
                <td class="px-4 py-3 text-center">
                    <button onclick="irAComunicacionesDeuda()" 
                            class="text-primary-600 hover:text-primary-800 font-medium text-sm transition-colors"
                            title="Enviar recordatorio de pago">
                        <i class="fas fa-bell mr-1"></i> Avisar
                    </button>
                </td>
            </tr>
        `).join('');
        
    } catch (error) {
        console.error('Error cargando deudores:', error);
        targetTable.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-red-600">No se pudo cargar la lista de deudores.</td></tr>';
    }
};

/* ========================= FUNCIONES PARA CARDS (KPIs) ========================= */

function actualizarCards(data) {
    // Validamos que venga la data correcta del backend
    if (!data || !data.resumen) return;

    // Referencias a los elementos del HTML (IDs deben coincidir con tu HTML)
    const elIngreso = document.getElementById('kpi_ingresos');
    const elGasto = document.getElementById('kpi_gastos');
    const elSaldo = document.getElementById('kpi_saldo');

    // 1. Actualizar Ingresos
    if (elIngreso) {
        elIngreso.textContent = fmtMoney(data.resumen.ingreso_real);
    }

    // 2. Actualizar Gastos
    if (elGasto) {
        elGasto.textContent = fmtMoney(data.resumen.total_gastos);
    }

    // 3. Actualizar Utilidad/Saldo (con color rojo si es negativo)
    if (elSaldo) {
        const utilidad = data.resumen.utilidad;
        elSaldo.textContent = fmtMoney(utilidad);
        
        // Lógica de colores visual
        if (utilidad < 0) {
            elSaldo.classList.add('text-red-600');
            elSaldo.classList.remove('text-green-600', 'text-blue-600');
        } else {
            elSaldo.classList.remove('text-red-600');
            elSaldo.classList.add('text-green-600'); // O el color que prefieras para positivo
        }
    }
}

/* ========================= PESTAÑA MOVIMIENTOS ========================= */

window.cargarMovimientosCaja = async function() {
    const tbody = document.getElementById('tabla-movimientos-body');
    if (!tbody) return;

    // 1. Filtros
    const fInicio = document.getElementById('mov_fecha_inicio')?.value;
    const fFin = document.getElementById('mov_fecha_fin')?.value;
    const fTipo = document.getElementById('mov_tipo')?.value;

    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-gray-500">Actualizando...</td></tr>`;

    try {
        let url = `${API_BASE}/finanzas/movimientos?limit=200`;
        if (fInicio) url += `&fecha_desde=${fInicio}`;
        if (fFin) url += `&fecha_hasta=${fFin}`;
        if (fTipo && fTipo !== 'TODOS') url += `&tipo=${fTipo}`;

        const res = await fetchAPI(url);
        const data = await res.json();
        
        // 2. ACTUALIZAR ETIQUETAS (SALDO)
        // Verificamos que los elementos existan antes de asignar
        const elIng = document.getElementById('mov_total_ingresos');
        const elEgr = document.getElementById('mov_total_egresos');
        const elSal = document.getElementById('mov_saldo_periodo');

        if (data.resumen) {
            if (elIng) elIng.textContent = fmtMoney(data.resumen.total_ingresos);
            if (elEgr) elEgr.textContent = fmtMoney(data.resumen.total_egresos);
            
            if (elSal) {
                const s = data.resumen.saldo;
                elSal.textContent = fmtMoney(s);
            }
        }

        // 3. PINTAR TABLA ORDENADA
        const items = data.items || [];
        
        if (items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-gray-400">Sin movimientos.</td></tr>`;
            return;
        }

        tbody.innerHTML = items.map(m => `
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">${m.fecha}</td>
                
               <td class="px-6 py-4">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${
                        m.tipo === 'INGRESO' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                    }">
                        ${m.tipo}
                    </span>
                </td>

                <td class="px-4 py-3 text-sm text-gray-600 font-medium">
                    ${m.categoria || '-'}
                </td>

                <td class="px-4 py-3 text-sm text-gray-800 dark:text-gray-200">
                    ${m.detalle}
                </td>

                <td class="px-4 py-3 text-center text-xs">
                    <span class="px-2 py-1 rounded bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-300">
                        ${m.metodo}
                    </span>
                </td>

                <td class="px-4 py-3 text-right font-mono font-bold ${
                    m.tipo === 'INGRESO' ? 'text-green-600' : 'text-red-600'
                }">
                    ${m.tipo === 'EGRESO' ? '-' : ''}${fmtMoney(m.monto)}
                </td>

            </tr>
        `).join('');

    } catch (e) {
        console.error(e);
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-red-500">Error cargando datos.</td></tr>`;
    }
};


// Redirige a comunicaciones indicando que es una notificación de deuda
window.irAComunicacionesDeuda = function() {
    // Agregamos 'context=deuda' para saber qué texto poner, 
    // pero NO enviamos ID de alumno para evitar confusiones.
    window.location.href = `/comunicaciones?action=nueva_notificacion&context=deuda`;
};

/* ========================= LÓGICA SUELDOS ========================= */

// 1. Detectar cambio en Categoría para mostrar select de Profesora
document.addEventListener('DOMContentLoaded', () => {
    // ... tu código existente ...
    
    const selCat = document.getElementById('gasto_categoria');
    if (selCat) {
        selCat.addEventListener('change', async (e) => {
            const txt = e.target.options[e.target.selectedIndex].text.toUpperCase();
            const divProfe = document.getElementById('div-gasto-profesora');
            
            if (txt.includes('SUELDO') || txt.includes('PLANILLA')) {
                divProfe.classList.remove('hidden');
                // Cargar profesoras si está vacío
                const selProfe = document.getElementById('gasto_profesora');
                if (selProfe.options.length <= 1) {
                    await cargarListaProfesorasSelect();
                }
            } else {
                divProfe.classList.add('hidden');
                document.getElementById('gasto_profesora').value = "";
            }
        });
    }
    
    // Setear mes actual en filtro sueldos
    const selMesSueldo = document.getElementById('sueldo_mes');
    if(selMesSueldo) selMesSueldo.value = new Date().getMonth() + 1;
});

async function cargarListaProfesorasSelect() {
    try {
        // Usamos el endpoint de usuarios filtrando por rol (asumiendo que existe o reutilizamos lista)
        const res = await fetchAPI(`${API_BASE}/usuarios?rol=PROFESORA&activo=1`);
        const data = await res.json();
        const lista = data.items || [];
        
        const sel = document.getElementById('gasto_profesora');
        sel.innerHTML = '<option value="">-- Seleccione --</option>';
        
        lista.forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.nombre_completo; // Usamos nombre para guardarlo en el detalle
            opt.textContent = u.nombre_completo;
            sel.appendChild(opt);
        });
    } catch (e) {
        console.error("Error cargando profes:", e);
    }
}

// 2. Interceptar el guardado de gasto para agregar el nombre al detalle
const originalGuardarGasto = window.guardarGasto; // Guardamos ref si existe, o reescribimos

window.guardarGasto = async function (e) {
    e.preventDefault();
    const form = document.getElementById('form-gasto');
    
    // Si hay profesora seleccionada, la concatenamos al detalle
    const selProfe = document.getElementById('gasto_profesora');
    const inputDetalle = form.querySelector('input[name="detalle"]');
    
    // Guardamos el valor original para restaurarlo después (por si falla)
    const detalleOriginal = inputDetalle.value; 
    
    if (selProfe && selProfe.value && !document.getElementById('div-gasto-profesora').classList.contains('hidden')) {
        // Formato Estandarizado para que el Backend lo detecte
        inputDetalle.value = `${detalleOriginal} - ${selProfe.value}`;
    }

    // Llamamos a la lógica original de envío (reutilizando tu fetchForm)
    // O copiamos la lógica aquí si prefieres ser explícito.
    // Como tu función original usa `new FormData(form)`, tomará el valor modificado del input.
    
    const btn = form.querySelector('button[type="submit"]');
    const txtOriginal = btn.textContent;
    
    try {
        btn.disabled = true; btn.textContent = 'Procesando...';
        const fd = new FormData(form);
        await fetchForm(`${API_BASE}/finanzas/gastos`, { method: 'POST', formData: fd });
        
        showToast('Egreso registrado', 'success');
        closeModal('modal-gasto');
        form.reset();
        
        // Restaurar input detalle por si acaso
        // (aunque el reset lo limpia, es buena práctica si no cerramos modal)
        
        // Recargar tablas
        if (currentTab === 'pagos') await cargarHistorial();
        if (currentTab === 'sueldos') await cargarReporteSueldos();
        await cargarArqueoResumen();
        
    } catch (err) {
        showToast(err.message, 'error');
        inputDetalle.value = detalleOriginal; // Restaurar si falló para que el usuario corrija
    } finally {
        btn.disabled = false; btn.textContent = txtOriginal;
    }
};

// 3. Cargar Reporte de Sueldos (Nueva Pestaña)
window.cargarReporteSueldos = async function() {
    const tbody = document.getElementById('tabla-sueldos-body');
    const anio = document.getElementById('sueldo_anio').value;
    const mes = document.getElementById('sueldo_mes').value;
    const estado = document.getElementById('sueldo_estado').value;
    
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-gray-400">Analizando planilla...</td></tr>';
    
    try {
        const url = `${API_BASE}/finanzas/reporte-sueldos?mes=${mes}&anio=${anio}&estado=${estado}`;
        const res = await fetchAPI(url);
        const data = await res.json(); // Array directo
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-gray-400">No se encontraron resultados.</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.map(item => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700">
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">
                    ${item.nombre}
                </td>
                <td class="px-6 py-4 text-center">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${
                        item.estado === 'PAGADO' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                        : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' 
                        
                    }">
                    
                        ${item.estado}
                    </span>
                </td>
                <td class="px-6 py-4 text-right font-mono text-gray-700 dark:text-gray-300">
                    ${item.monto > 0 ? fmtMoney(item.monto) : '-'}
                </td>
                <td class="px-6 py-4 text-center text-sm text-gray-500">
                    ${item.fecha_pago}
                </td>
                <td class="px-6 py-4 text-center">
                    ${item.estado === 'PENDIENTE' ? `
                        <button onclick="prepararPagoSueldo('${item.nombre}')" class="text-blue-600 hover:text-blue-800 text-sm font-medium hover:underline">
                            <i class="fas fa-hand-holding-usd mr-1"></i>Pagar
                        </button>
                    ` : '<span class="text-gray-300"><i class="fas fa-check"></i></span>'}
                </td>
            </tr>
        `).join('');
        
    } catch (e) {
        console.error(e);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-red-500">Error al cargar planilla.</td></tr>';
    }
};

// Función extra: Clic en "Pagar" desde la tabla abre el modal y pre-llena datos
window.prepararPagoSueldo = async function(nombreProfe) {
    // 1. Abrir Modal
    openModal('modal-gasto');
    
    // 2. Seleccionar Categoría SUELDOS (buscarla en el select)
    const selCat = document.getElementById('gasto_categoria');
    for (let i = 0; i < selCat.options.length; i++) {
        if (selCat.options[i].text.toUpperCase().includes('SUELDO')) {
            selCat.selectedIndex = i;
            // Disparar evento change manualmente para mostrar el select de profes
            selCat.dispatchEvent(new Event('change'));
            break;
        }
    }
    
    // 3. Esperar un poco a que cargue el select de profes y seleccionar la correcta
    setTimeout(() => {
        const selProfe = document.getElementById('gasto_profesora');
        // Buscar opción por texto
        for (let i = 0; i < selProfe.options.length; i++) {
            if (selProfe.options[i].text === nombreProfe) {
                selProfe.selectedIndex = i;
                break;
            }
        }
        
        // 4. Pre-llenar detalle
        const mes = document.getElementById('sueldo_mes').options[document.getElementById('sueldo_mes').selectedIndex].text;
        document.querySelector('#form-gasto input[name="detalle"]').value = `Sueldo ${mes}`;
        
    }, 500);
};