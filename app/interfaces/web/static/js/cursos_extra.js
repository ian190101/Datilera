import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';
let currentCursoId = null;
let currentCursoData = null; // Para guardar datos del curso seleccionado (precios, etc)

document.addEventListener('DOMContentLoaded', () => {
    loadCursos();
});

/* ================== GESTIÓN DE CURSOS ================== */

window.loadCursos = async function() {
    const container = document.getElementById('grid-cursos');
    container.innerHTML = '<div class="col-span-full text-center py-12 text-gray-500"><i class="fas fa-circle-notch fa-spin mr-2"></i> Cargando...</div>';
    
    try {
        const res = await fetchAPI(`${API_BASE}/cursos-extra`);
        const data = await res.json();
        
        if (data.length === 0) {
            container.innerHTML = '<div class="col-span-full text-center py-12 text-gray-400">No hay cursos activos. Crea uno nuevo.</div>';
            return;
        }
        
        container.innerHTML = data.map(c => `
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-200 dark:border-gray-700 flex flex-col h-full">
                <div class="p-6 flex-1">
                    <div class="flex justify-between items-start mb-2">
                        <span class="bg-primary-100 text-primary-800 text-xs px-2 py-1 rounded font-bold uppercase">${c.gestion}</span>
                        <span class="text-xs text-gray-500"><i class="fas fa-user mr-1"></i> ${c.instructor}</span>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">${c.nombre}</h3>
                    <div class="text-sm text-gray-600 dark:text-gray-400 mb-4 space-y-1">
                        <p><i class="far fa-calendar-alt w-5"></i> ${c.fechas}</p>
                        <p><i class="fas fa-users w-5"></i> Inscritos: <b>${c.cupos.ocupados}</b> / ${c.cupos.max}</p>
                    </div>
                    <div class="flex gap-4 text-xs font-mono border-t pt-3 border-gray-100 dark:border-gray-700">
                        <div>
                            <span class="block text-gray-400">Ingresos</span>
                            <span class="text-green-600 font-bold">Bs. ${c.finanzas.ingresos}</span>
                        </div>
                        <div>
                            <span class="block text-gray-400">Gastos</span>
                            <span class="text-red-600 font-bold">Bs. ${c.finanzas.gastos}</span>
                        </div>
                    </div>
                </div>
                <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900/50 rounded-b-xl border-t border-gray-200 dark:border-gray-700">
                    <button onclick="verDetalleCurso(${c.id}, '${c.nombre}', '${c.instructor}')" class="w-full py-2 text-center text-primary-600 font-medium hover:text-primary-800 text-sm">
                        Administrar Curso <i class="fas fa-arrow-right ml-1"></i>
                    </button>
                </div>
            </div>
        `).join('');
        
    } catch (e) {
        console.error(e);
        container.innerHTML = '<div class="col-span-full text-center text-red-500">Error al cargar cursos.</div>';
    }
};

/* EN cursos_extra.js - Reemplazar la función crearCurso */

window.crearCurso = async function(e) {
    e.preventDefault();
    const form = e.target;
    
    // Captura automática de todos los inputs (incluido cupo_maximo)
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData);
    
    // Validación básica opcional en frontend
    if (parseInt(payload.cupo_maximo) < 1) {
        showToast("El cupo máximo debe ser al menos 1", "warning");
        return;
    }

    try {
        const res = await fetchAPI(`${API_BASE}/cursos-extra`, {
            method: 'POST', 
            body: JSON.stringify(payload)
        });
        
        if(!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Error creando curso");
        }
        
        showToast("Curso creado exitosamente", "success");
        closeModal('modal-nuevo-curso');
        form.reset();
        loadCursos(); // Recargar la lista para ver el nuevo curso
    } catch(err) { 
        showToast(err.message, 'error'); 
    }
};

/* ================== DETALLE Y NAVEGACIÓN ================== */

window.verDetalleCurso = async function(id, nombre, instructor) {
    currentCursoId = id;
    
    // UI Update
    document.getElementById('grid-cursos').classList.add('hidden');
    document.getElementById('seccion-detalle-curso').classList.remove('hidden');
    
    document.getElementById('detalle-titulo').textContent = nombre;
    document.getElementById('detalle-instructor').textContent = `Instructor: ${instructor}`;
    
    // Cargar datos
    loadInscritos();
};

window.cerrarDetalleCurso = function() {
    currentCursoId = null;
    document.getElementById('seccion-detalle-curso').classList.add('hidden');
    document.getElementById('grid-cursos').classList.remove('hidden');
    loadCursos(); // Refrescar por si hubo cambios
};

window.switchCursoTab = function(tab) {
    // Estilos botones
    const btnInsc = document.getElementById('tab-btn-inscritos');
    const btnFin = document.getElementById('tab-btn-finanzas');
    
    if(tab === 'inscritos') {
        btnInsc.className = "w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm border-primary-500 text-primary-600";
        btnFin.className = "w-1/2 py-4 px-1 text-center border-b-2 border-transparent text-primary-500 hover:text-primary-700";
        document.getElementById('view-inscritos').classList.remove('hidden');
        document.getElementById('view-finanzas').classList.add('hidden');
    } else {
        btnFin.className = "w-1/2 py-4 px-1 text-center border-b-2 font-medium text-sm border-primary-500 text-primary-600";
        btnInsc.className = "w-1/2 py-4 px-1 text-center border-b-2 border-transparent text-primary-500 hover:text-primary-700";
        document.getElementById('view-finanzas').classList.remove('hidden');
        document.getElementById('view-inscritos').classList.add('hidden');
        loadFinanzasCurso(); // Cargar datos financieros
    }
};

/* ================== INSCRIPCIONES ================== */

async function loadInscritos() {
    if(!currentCursoId) return;
    const tbody = document.getElementById('tabla-inscritos-body');
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4">Cargando...</td></tr>';
    
    try {
        const res = await fetchAPI(`${API_BASE}/cursos-extra/${currentCursoId}/inscritos`);
        const data = await res.json();
        
        if(data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-gray-400">No hay alumnos inscritos aún.</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.map(row => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700">
                <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white">${row.nombre}</td>
                <td class="px-4 py-3 text-xs"><span class="bg-gray-100 px-2 py-1 rounded">${row.tipo}</span></td>
                <td class="px-4 py-3 text-sm text-gray-500">${row.tutor} <br><span class="text-xs">${row.celular}</span></td>
                <td class="px-4 py-3 text-right font-mono text-sm text-gray-500">Bs. ${row.deuda_total}</td>
                <td class="px-4 py-3 text-right font-mono text-sm text-green-600">Bs. ${row.pagado}</td>
                <td class="px-4 py-3 text-right font-mono text-sm text-red-600 font-bold">Bs. ${row.saldo}</td>
                <td class="px-4 py-3 text-center">
                    ${row.saldo > 0 ? 
                        `<button onclick="prepararPago(${row.balance_id}, ${row.saldo})" class="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-bold hover:bg-green-200">
                            <i class="fas fa-dollar-sign mr-1"></i> Cobrar
                        </button>` : 
                        `<span class="text-green-500 text-xs"><i class="fas fa-check-circle"></i> Pagado</span>`
                    }
                </td>
            </tr>
        `).join('');
        
    } catch(e) { console.error(e); }
}

window.openModalInscripcion = async function() {
    openModal('modal-inscripcion');
    const sel = document.getElementById('sel-alumno-interno');
    
    // Cargar lista solo si está vacía
    if(sel.options.length <= 1) {
        try {
            const res = await fetchAPI('/api/v1/alumnos-select/lista'); 
            const data = await res.json();
            
            sel.innerHTML = '<option value="">Seleccione...</option>' + 
                data.map(a => `<option value="${a.id}">${a.nombre}</option>`).join('');
                
        } catch(e) {
            console.error("Error cargando alumnos:", e);
        }
    }
};

window.toggleTipoAlumno = function(tipo) {
    document.getElementById('insc-tipo').value = tipo;
    const btnInt = document.getElementById('btn-tipo-interno');
    const btnExt = document.getElementById('btn-tipo-externo');
    const fInt = document.getElementById('fields-interno');
    const fExt = document.getElementById('fields-externo');
    
    if(tipo === 'INTERNO') {
        btnInt.className = "w-1/2 py-1 rounded-md text-sm font-bold bg-white text-teal-700 shadow";
        btnExt.className = "w-1/2 py-1 rounded-md text-sm font-bold text-gray-500";
        fInt.classList.remove('hidden');
        fExt.classList.add('hidden');
        document.getElementById('sel-alumno-interno').required = true;
    } else {
        btnExt.className = "w-1/2 py-1 rounded-md text-sm font-bold bg-white text-blue-700 shadow";
        btnInt.className = "w-1/2 py-1 rounded-md text-sm font-bold text-gray-500";
        fExt.classList.remove('hidden');
        fInt.classList.add('hidden');
        document.getElementById('sel-alumno-interno').required = false;
    }
};

window.guardarInscripcion = async function(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData);
    
    // Ajustes finales
    payload.curso_id = currentCursoId;
    if(payload.tipo_alumno === 'INTERNO') {
        payload.alumno_id = document.getElementById('sel-alumno-interno').value;
    }
    
    try {
        const res = await fetchAPI(`${API_BASE}/cursos-extra/inscripcion`, {
            method: 'POST', body: JSON.stringify(payload)
        });
        if(!res.ok) throw new Error((await res.json()).detail);
        
        showToast("Inscripción exitosa", "success");
        closeModal('modal-inscripcion');
        form.reset();
        loadInscritos();
    } catch(err) { showToast(err.message, 'error'); }
};

/* ================== PAGOS ================== */

window.prepararPago = function(balanceId, saldo) {
    document.getElementById('pago-balance-id').value = balanceId;
    document.getElementById('pago-saldo-display').textContent = `Bs. ${saldo}`;
    document.querySelector('input[name="monto"]').max = saldo;
    document.querySelector('input[name="monto"]').value = saldo; // Sugerir pago total
    openModal('modal-pago-curso');
};

window.guardarPagoCurso = async function(e) {
    e.preventDefault();
    const payload = Object.fromEntries(new FormData(e.target));
    
    try {
        const res = await fetchAPI(`${API_BASE}/cursos-extra/pagos`, {
            method: 'POST', body: JSON.stringify(payload)
        });
        if(!res.ok) throw new Error("Error en pago");
        
        showToast("Pago registrado", "success");
        closeModal('modal-pago-curso');
        loadInscritos(); // Recargar tabla
    } catch(err) { showToast(err.message, 'error'); }
};

/* ================== FINANZAS (Visualización simple) ================== */
async function loadFinanzasCurso() {
    // Reutilizamos el endpoint de lista de cursos que ya trae el resumen financiero
    // Esto es un truco para no crear otro endpoint GET específico de finanzas si no es necesario
    // Pero idealmente debería haber uno. Por agilidad, recargamos la lista y buscamos el ID.
    try {
        const res = await fetchAPI(`${API_BASE}/cursos-extra`);
        const data = await res.json();
        const curso = data.find(c => c.id === currentCursoId);
        
        if(curso && curso.finanzas) {
            const f = curso.finanzas;
            document.getElementById('fin-ingresos').textContent = `Bs. ${f.ingresos.toFixed(2)}`;
            document.getElementById('fin-gastos').textContent = `Bs. ${f.gastos.toFixed(2)}`;
            const utilidad = f.ingresos - f.gastos;
            document.getElementById('fin-utilidad').textContent = `Bs. ${utilidad.toFixed(2)}`;
            
            // Colores
            const utilEl = document.getElementById('fin-utilidad');
            utilEl.className = utilidad >= 0 ? "text-2xl font-mono text-blue-800 mt-1" : "text-2xl font-mono text-red-600 mt-1";
            
            // Split (esto venía en el objeto si modificaste el endpoint listar_cursos, si no, hay que calcularlo aprox)
            document.getElementById('fin-split-inst').textContent = `Bs. ${f.ganancia_institucion.toFixed(2)}`;
            const prof = utilidad - f.ganancia_institucion;
            document.getElementById('fin-split-prof').textContent = `Bs. ${prof.toFixed(2)}`;
            
            document.getElementById('detalle-ganancia').textContent = `Bs. ${f.ganancia_institucion.toFixed(2)}`;
        }
    } catch(e) {}
}

// ===== Modales (helpers globales) =====
window.openModal = (id) => {
  const el = document.getElementById(id);
  if (!el) return;

  el.classList.remove('hidden');

  // Opcional: cerrar al hacer click fuera del contenido
  // (solo si el modal tiene overlay como contenedor principal)
  el.addEventListener('click', (e) => {
    if (e.target === el) window.closeModal(id);
  }, { once: true });

  // Opcional: cerrar con ESC
  const onEsc = (e) => {
    if (e.key === 'Escape') {
      window.closeModal(id);
      document.removeEventListener('keydown', onEsc);
    }
  };
  document.addEventListener('keydown', onEsc);
};

window.closeModal = (id) => {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.add('hidden');
};

/* ================== GASTOS ================== */

// 1. Abrir Modal
window.openModalGasto = function() {
    if (!currentCursoId) return;
    document.getElementById('gasto-curso-id').value = currentCursoId;
    openModal('modal-gasto');
};

// 2. Guardar Gasto
window.guardarGasto = async function(e) {
    e.preventDefault();
    const form = e.target;
    const payload = Object.fromEntries(new FormData(form));
    
    try {
        const res = await fetchAPI(`${API_BASE}/cursos-extra/gastos`, {
            method: 'POST', 
            body: JSON.stringify(payload)
        });
        
        if(!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Error registrando gasto");
        }
        
        showToast("Gasto registrado", "success");
        closeModal('modal-gasto');
        form.reset();
        
        // Actualizar datos financieros en pantalla
        loadFinanzasCurso();
        
    } catch(err) { 
        showToast(err.message, 'error'); 
    }
};