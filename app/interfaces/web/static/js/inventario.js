import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';

/* =======================================================
   HELPERS GLOBALES (Faltaban en tu versión anterior)
   ======================================================= */
window.openModal = (id) => document.getElementById(id)?.classList.remove('hidden');
window.closeModal = (id) => document.getElementById(id)?.classList.add('hidden');

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/* =======================================================
   INICIALIZACIÓN Y TABS
   ======================================================= */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Inicializar Tabs
    const tabs = document.querySelectorAll('.tab-btn');
    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            // Quitar activo de todos
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('active', 'border-[#DD8E0A]', 'text-[#DD8E0A]');
                b.classList.add('border-transparent', 'text-gray-600');
            });
            document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
            
            // Activar seleccionado
            btn.classList.add('active', 'border-[#DD8E0A]', 'text-[#DD8E0A]');
            btn.classList.remove('border-transparent', 'text-gray-600');
            
            const targetId = `tab-${btn.dataset.tab}`;
            document.getElementById(targetId)?.classList.remove('hidden');
            
            // Cargar datos si es necesario
            if (btn.dataset.tab === 'productos') cargarInventario();
            if (btn.dataset.tab === 'movimientos') loadMovimientos(); 
        });
    });

    // 2. Carga inicial
    cargarInventario();
    cargarFamiliasSelect();
    loadMetricas();
    
    // 3. Buscador
    const buscador = document.getElementById('inv_buscador');
    if(buscador) {
        buscador.addEventListener('input', debounce(() => cargarInventario(buscador.value), 500));
    }
});

/* =======================================================
   CARGA DE DATOS
   ======================================================= */
window.cargarInventario = async function(search = '') {
    const tbody = document.getElementById('tabla-inventario-body');
    if(!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-8">Cargando inventario...</td></tr>';
    
    try {
        let url = `${API_BASE}/inventarios/items`;
        if(search) url += `?search=${search}`;
        
        const res = await fetchAPI(url);
        const data = await res.json();
        
        // Actualizar KPIs (Simple)
        if(document.getElementById('kpi-total-productos')) 
            document.getElementById('kpi-total-productos').textContent = data.length;
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-8 text-gray-500">No hay productos registrados.</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.map(item => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700">
                <td class="px-6 py-4 font-mono text-xs font-bold text-gray-600 dark:text-gray-300">${item.codigo}</td>
                <td class="px-6 py-4">
                    <div class="font-medium text-gray-900 dark:text-white">${item.nombre}</div>
                    <div class="text-xs text-gray-500 flex flex-wrap gap-1 mt-1">
                        ${Object.entries(item.atributos).map(([k,v]) => 
                            `<span class="bg-gray-100 dark:bg-gray-600 px-1.5 py-0.5 rounded border border-gray-200 dark:border-gray-500">${k}: ${v}</span>`
                        ).join('')}
                    </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500">
                    <span class="block text-xs font-bold text-indigo-600 uppercase">${item.familia}</span>
                    <span class="block text-gray-600 dark:text-gray-400">${item.categoria}</span>
                </td>
                <td class="px-6 py-4 text-right font-medium">Bs. ${item.precio.toFixed(2)}</td>
                <td class="px-6 py-4 text-center">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${item.stock < 5 ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'}">
                        ${item.stock} ${item.unidad}
                    </span>
                </td>
                <td class="px-6 py-4 text-center">
                    <div class="flex justify-center gap-2">
                        <button onclick="prepararMovimiento(${item.id}, '${item.nombre}', 'entrada')" class="p-1 text-green-600 hover:bg-green-50 rounded" title="Entrada Stock">
                            <i class="fas fa-arrow-down"></i>
                        </button>
                        <button onclick="prepararMovimiento(${item.id}, '${item.nombre}', 'salida')" class="p-1 text-red-600 hover:bg-red-50 rounded" title="Salida Stock">
                            <i class="fas fa-arrow-up"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
        
    } catch (e) {
        console.error(e);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-red-500">Error cargando datos.</td></tr>';
    }
};

/* =======================================================
   GESTIÓN SELECTORES (Familia/Categoria)
   ======================================================= */
async function cargarFamiliasSelect() {
    try {
        const res = await fetchAPI(`${API_BASE}/inventarios/familias`);
        const data = await res.json();
        
        // Llenar select del modal categoría
        const selCat = document.getElementById('cat_familia_id');
        if (selCat) {
            selCat.innerHTML = data.map(f => `<option value="${f.id}">${f.nombre}</option>`).join('');
        }
        
        // Llenar select del modal Item
        const selItem = document.getElementById('item_familia');
        if (selItem) {
            selItem.innerHTML = '<option value="">Seleccione...</option>' + 
                                data.map(f => `<option value="${f.id}">${f.nombre}</option>`).join('');
        }
    } catch (e) { console.error(e); }
}

window.cargarCategoriasEnItem = async function(familiaId) {
    const sel = document.getElementById('item_categoria');
    if(!familiaId) {
        sel.innerHTML = '<option value="">Primero seleccione familia</option>';
        return;
    }
    try {
        const res = await fetchAPI(`${API_BASE}/inventarios/categorias?familia_id=${familiaId}`);
        const data = await res.json();
        sel.innerHTML = data.map(c => `<option value="${c.id}">${c.nombre}</option>`).join('');
    } catch(e) { console.error(e); }
};

/* =======================================================
   GUARDAR DATOS (Familia, Categoria, Item)
   ======================================================= */
window.guardarFamilia = async function(e) {
    e.preventDefault();
    const form = e.target;
    try {
        await fetchAPI(`${API_BASE}/inventarios/familias`, {
            method: 'POST', body: JSON.stringify({ nombre: form.nombre.value, descripcion: form.descripcion.value })
        });
        showToast('Familia creada', 'success');
        closeModal('modal-familia');
        cargarFamiliasSelect();
        form.reset();
    } catch(e) { showToast(e.message || 'Error', 'error'); }
};

window.guardarCategoria = async function(e) {
    e.preventDefault();
    const form = e.target;
    try {
        await fetchAPI(`${API_BASE}/inventarios/categorias`, {
            method: 'POST', body: JSON.stringify({ nombre: form.nombre.value, familia_id: form.familia_id.value })
        });
        showToast('Categoría creada', 'success');
        closeModal('modal-categoria');
        form.reset();
    } catch(e) { showToast(e.message || 'Error', 'error'); }
};

/* --- ITEMS DINÁMICOS --- */
window.agregarFilaAtributo = function() {
    const div = document.createElement('div');
    div.className = "grid grid-cols-2 gap-2 bg-gray-50 p-2 rounded dark:bg-gray-700/50 relative group animate-fade-in";
    div.innerHTML = `
        <input type="text" placeholder="Atributo (ej: Color)" class="attr-name w-full rounded border-gray-300 text-xs px-2 py-1">
        <input type="text" placeholder="Valor (ej: Azul)" class="attr-val w-full rounded border-gray-300 text-xs px-2 py-1">
        <button type="button" onclick="this.parentElement.remove()" class="absolute -right-2 -top-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity">
            <i class="fas fa-times"></i>
        </button>
    `;
    document.getElementById('contenedor-atributos').appendChild(div);
};

/* EN inventario.js - Reemplaza toda la función guardarItem */

window.guardarItem = async function(e) {
    e.preventDefault();
    const form = e.target; // Referencia directa al formulario <form>
    
    // 1. OBTENCIÓN DE DATOS (CORREGIDO)
    const nombre = form.nombre.value;
    const catId = form.categoria_id.value;
    const precio = form.precio.value;
    
    // Para descripción, validamos si existe el campo
    const desc = form.querySelector('textarea[name="descripcion"]')?.value || ""; 

    // Para STOCK y MINIMO usamos los IDs específicos que pusimos en el paso anterior
    // Usamos el operador '?.' para que no explote si por alguna razón no encuentra el ID
    const stockInicial = document.getElementById('prod-stock')?.value || 0;
    const stockMin = document.getElementById('prod-stock-min')?.value || 5;
    
    // 2. LÓGICA DE UNIDAD DE MEDIDA
    // Aquí sí necesitamos el ID para la lógica de "OTRA"
    const selectUnidad = document.getElementById('prod-unidad');
    let unidadFinal = selectUnidad ? selectUnidad.value : 'UNIDAD';
    
    if (unidadFinal === 'OTRA') {
        const inputCustom = document.getElementById('prod-unidad-custom');
        unidadFinal = inputCustom ? inputCustom.value.trim().toUpperCase() : '';
        
        if (!unidadFinal) {
            return showToast('Especifique la unidad de medida', 'warning');
        }
    }

    // 3. ATRIBUTOS DINÁMICOS
    const attrs = [];
    document.querySelectorAll('#contenedor-atributos > div').forEach(div => {
        const n = div.querySelector('.attr-name').value.trim();
        const v = div.querySelector('.attr-val').value.trim();
        if(n && v) attrs.push({ nombre: n, valor: v });
    });
    
    // 4. PREPARAR PAYLOAD
    const payload = {
        categoria_id: parseInt(catId),
        nombre: nombre,
        descripcion: desc,
        precio: parseFloat(precio),
        unidad: unidadFinal,
        stock_inicial: parseFloat(stockInicial),
        stock_minimo: parseFloat(stockMin),
        atributos: attrs
    };
    
    // 5. ENVIAR AL BACKEND
    try {
        const res = await fetchAPI(`${API_BASE}/inventarios/items`, {
            method: 'POST', body: JSON.stringify(payload)
        });
        if(!res.ok) throw new Error((await res.json()).detail);
        
        showToast('Producto creado exitosamente', 'success');
        
        // Cerrar y Limpiar
        if (typeof closeNewProductModal === 'function') {
            closeNewProductModal(); // Si usas la función antigua
        } else {
            closeModal('modal-item'); // Si usas la nueva
        }
        
        form.reset();
        document.getElementById('contenedor-atributos').innerHTML = '';
        
        // Ocultar input custom si quedó abierto
        const customInput = document.getElementById('prod-unidad-custom');
        if(customInput) customInput.classList.add('hidden');
        
        cargarInventario();
        if(typeof loadMetricas === 'function') loadMetricas();
        
    } catch(e) { 
        console.error(e);
        showToast(e.message || 'Error al guardar', 'error'); 
    }
};

/* =======================================================
   MOVIMIENTOS
   ======================================================= */
window.prepararMovimiento = function(id, nombre, tipo) {
    document.getElementById('mov_item_id').value = id;
    document.getElementById('mov_nombre_item').textContent = `${tipo.toUpperCase()}: ${nombre}`;
    document.getElementById('mov_tipo').value = tipo;
    openModal('modal-movimiento');
};

window.guardarMovimiento = async function(e) {
    e.preventDefault();
    const form = e.target;
    try {
        const res = await fetchAPI(`${API_BASE}/inventarios/movimientos`, {
            method: 'POST', 
            body: JSON.stringify({
                item_id: form.item_id.value,
                tipo: form.tipo.value,
                cantidad: parseFloat(form.cantidad.value),
                motivo: form.motivo.value
            })
        });
        if(!res.ok) throw new Error((await res.json()).detail);
        
        showToast('Stock actualizado', 'success');
        closeModal('modal-movimiento');
        form.reset();
        cargarInventario();
    } catch(e) { showToast(e.message, 'error'); }
};

/* ================== HISTORIAL MOVIMIENTOS ================== */

window.loadMovimientos = async function() {
    const tbody = document.getElementById('tabla-movimientos-body');
    if (!tbody) return;
    
    // Obtener filtros
    const tipo = document.getElementById('filter-tipo-movimiento')?.value || '';
    const desde = document.getElementById('filter-fecha-desde')?.value || '';
    const hasta = document.getElementById('filter-fecha-hasta')?.value || '';
    
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-gray-500">Cargando historial...</td></tr>';
    
    try {
        let url = `${API_BASE}/inventarios/movimientos?_=${new Date().getTime()}`;
        if (tipo) url += `&tipo=${tipo}`;
        if (desde) url += `&start_date=${desde}`;
        if (hasta) url += `&end_date=${hasta}`;
        
        const res = await fetchAPI(url);
        const data = await res.json();
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8 text-gray-500">No hay movimientos registrados.</td></tr>';
            return;
        }
        
        tbody.innerHTML = data.map(m => `
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700">
                <td class="px-6 py-4 text-sm text-gray-500">${m.fecha}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 rounded-full text-xs font-semibold ${
                        m.tipo === 'ENTRADA' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' 
                        : m.tipo === 'SALIDA' 
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300' // <--- ESTO FALTABA
                    }">
                        ${m.tipo}
                    </span>
                </td>
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">${m.item}</td>
                <td class="px-6 py-4 text-sm text-gray-500">${m.motivo} <span class="text-xs text-gray-400">(${m.usuario})</span></td>
                <td class="px-6 py-4 text-right font-mono font-bold ${m.tipo === 'ENTRADA' ? 'text-green-600' : 'text-red-600'}">
                    ${m.tipo === 'SALIDA' ? '-' : '+'}${m.cantidad}
                </td>
            </tr>
        `).join('');
        
    } catch (e) {
        console.error(e);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-red-500">Error al cargar historial.</td></tr>';
    }
};

window.loadMetricas = async function() {
    try {
        const res = await fetchAPI(`${API_BASE}/inventarios/metricas`);
        const data = await res.json();
        
        // Función helper para animar números (opcional, o asignación directa)
        const animateValue = (id, value, prefix = '') => {
            const el = document.getElementById(id);
            if(el) el.textContent = prefix + value;
        };

        // Formateador de moneda
        const fmtMoney = (n) => 'Bs. ' + Number(n).toLocaleString('es-BO', { minimumFractionDigits: 2 });

        animateValue('kpi-total-productos', data.total_productos);
        animateValue('kpi-valor-total', fmtMoney(data.valor_inventario));
        animateValue('kpi-stock-bajo', data.stock_bajo);
        animateValue('kpi-movimientos', data.movimientos_hoy);
        
        // Cambiar color de stock bajo si es crítico
        const elBajo = document.getElementById('kpi-stock-bajo');
        if (elBajo && data.stock_bajo > 0) {
            elBajo.classList.add('text-red-600');
            elBajo.classList.remove('text-orange-600');
        }

    } catch (error) {
        console.error("Error cargando métricas:", error);
    }
};

window.toggleOtraUnidad = function(select) {
    const customInput = document.getElementById('prod-unidad-custom');
    if (select.value === 'OTRA') {
        customInput.classList.remove('hidden');
        customInput.required = true;
        customInput.focus();
    } else {
        customInput.classList.add('hidden');
        customInput.required = false;
        customInput.value = '';
    }
};