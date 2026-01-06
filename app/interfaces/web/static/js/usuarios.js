// app/interfaces/web/static/js/usuarios.js
import { fetchAPI, showToast, showConfirm } from './main.js';

const API_BASE = '/api/v1';

let currentPage = 1;
let currentFilters = {
  search: '',
  rol: '',
  activo: '',
};
let cacheGruposParalelos = [];

/* =========================
   INIT
========================= */

document.addEventListener('DOMContentLoaded', () => {
  initEvents();
  loadUsuarios();
});

/* =========================
   EVENTS
========================= */

function initEvents() {
  document.getElementById('usuarios-aplicar-filtros')?.addEventListener('click', () => {
    currentFilters.search = document.getElementById('usuarios-search')?.value.trim() || '';
    currentFilters.rol = document.getElementById('usuarios-rol-filter')?.value || '';
    currentFilters.activo = document.getElementById('usuarios-activo-filter')?.value || '';
    currentPage = 1;
    loadUsuarios();
  });

  document.getElementById('usuarios-limpiar-filtros')?.addEventListener('click', () => {
    const s = document.getElementById('usuarios-search');
    const r = document.getElementById('usuarios-rol-filter');
    const a = document.getElementById('usuarios-activo-filter');
    if (s) s.value = '';
    if (r) r.value = '';
    if (a) a.value = '';
    currentFilters = { search: '', rol: '', activo: '' };
    currentPage = 1;
    loadUsuarios();
  });

  document.getElementById('usuarios-search')?.addEventListener(
    'input',
    debounce(e => {
      currentFilters.search = e.target.value.trim();
      currentPage = 1;
      loadUsuarios();
    }, 500),
  );

  document.getElementById('btn-nuevo-usuario')?.addEventListener('click', () => {
    openModal('modal-tipo-usuario');
  });

  document.getElementById('btn-cerrar-modal-tipo')?.addEventListener('click', () => {
    closeModal('modal-tipo-usuario');
  });

  document.getElementById('btn-crear-admin')?.addEventListener('click', () => {
    closeModal('modal-tipo-usuario');
    openModal('modal-admin');
  });

  document.getElementById('btn-crear-profesora')?.addEventListener('click', () => {
    closeModal('modal-tipo-usuario');
    openModal('modal-profesora');
  });

  // Modal Admin
  document.getElementById('btn-cerrar-modal-admin')?.addEventListener('click', () => {
    closeModal('modal-admin');
  });
  document.getElementById('btn-cancelar-admin')?.addEventListener('click', () => {
    closeModal('modal-admin');
  });
  document.getElementById('form-admin')?.addEventListener('submit', handleCrearAdmin);

  // Modal Profesora
  document.getElementById('btn-cerrar-modal-profesora')?.addEventListener('click', () => {
    closeModal('modal-profesora');
  });
  document.getElementById('btn-cancelar-profesora')?.addEventListener('click', () => {
    closeModal('modal-profesora');
  });
  document.getElementById('form-profesora')?.addEventListener('submit', handleCrearProfesora);

  // Modal código profesora
  document.getElementById('btn-cerrar-modal-prof-codigo')?.addEventListener('click', () => {
    closeModal('modal-profesora-codigo');
  });
  document.getElementById('btn-copiar-codigo-prof')?.addEventListener('click', copiarCodigoProfesora);
  document.getElementById('btn-whatsapp-prof')?.addEventListener('click', enviarWhatsAppProfesora);

  document.getElementById('btn-asignar-modal')?.addEventListener('click', () => {
    abrirModalAsignacion();
  });
}

/* =========================
   API - LISTA USUARIOS
========================= */

async function loadUsuarios(page = 1) {
  currentPage = page;
  const tbody = document.getElementById('usuarios-tbody');
  if (!tbody) return;

  tbody.innerHTML = `
    <tr>
      <td colspan="6" class="px-6 py-10 text-center text-gray-500">
        <div class="flex flex-col items-center">
          <div class="loader mb-3"></div>
          <p>Cargando usuarios...</p>
        </div>
      </td>
    </tr>
  `;

  try {
    const params = new URLSearchParams();
    params.set('page', String(currentPage));
    params.set('per_page', '10');
    if (currentFilters.search) params.set('search', currentFilters.search);
    if (currentFilters.rol) params.set('rol', currentFilters.rol);
    if (currentFilters.activo !== '') params.set('activo', currentFilters.activo);

    const response = await fetchAPI(`${API_BASE}/usuarios?${params.toString()}`);
    const data = await response.json();
    const items = data.items || data || [];
    const total = data.total || items.length;

    renderUsuarios(items);
    renderUsuariosPagination(total, currentPage, 10);

    const totalSpan = document.getElementById('usuarios-total');
    if (totalSpan) totalSpan.textContent = String(total);
  } catch (err) {
    console.error(err);
    showToast('Error al cargar usuarios', 'error');
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="px-6 py-10 text-center text-gray-500">
          <i class="fas fa-exclamation-triangle text-red-500 text-3xl mb-2"></i>
          <p>No se pudieron cargar los usuarios.</p>
        </td>
      </tr>
    `;
  }
}

function renderUsuarios(usuarios) {
  const tbody = document.getElementById('usuarios-tbody');
  if (!tbody) return;

  if (!usuarios || usuarios.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="px-6 py-10 text-center text-gray-500 dark:text-gray-400">
          <i class="fas fa-inbox text-5xl mb-3 opacity-50"></i>
          <p>No se encontraron usuarios.</p>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = usuarios
    .map(u => {
      const rol = u.rol_nombre || u.rol || u.role || 'Sin Rol';
      const activo = u.activo ?? u.is_active ?? true;
      const nombres = u.nombres || u.first_name || '';
      const apellidos = u.apellidos || u.last_name || '';
      const nombreCompleto = `${nombres} ${apellidos}`.trim() || (u.nombre_completo || '');
      const telefono = u.telefono || u.phone || '';
      const email = u.email || '';
      const username = u.username || u.nombre_usuario || '';
      const fotoUrl = u.foto_perfil_url; // <--- Asegúrate que el backend envíe este campo

      const estadoBadge = activo
        ? '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Activo</span>'
        : '<span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Inactivo</span>';

      // LÓGICA DE FOTO VS INICIALES
      let avatarHTML;
      if (fotoUrl) {
          avatarHTML = `<img src="${fotoUrl}" alt="${username}" class="w-9 h-9 rounded-full object-cover mr-3 border border-gray-200 dark:border-gray-600">`;
      } else {
          avatarHTML = `
            <div class="w-9 h-9 rounded-full bg-[#DD8E0A]/10 text-[#DD8E0A] flex items-center justify-center font-semibold mr-3">
              ${getInitials(nombreCompleto || username)}
            </div>`;
      }

      return `
        <tr class="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
          <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
            <div class="flex items-center">
              ${avatarHTML}
              <div>
                <p class="font-medium">${username}</p>
              </div>
            </div>
          </td>
          <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
            ${nombreCompleto || '-'}
          </td>
          <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
            ${formatRol(rol)}
          </td>
          <td class="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
            ${email ? `<p>${email}</p>` : ''}
            ${telefono ? `<p class="text-xs text-gray-500 dark:text-gray-400">+591 ${telefono}</p>` : ''}
          </td>
          <td class="px-6 py-4 text-sm">
            ${estadoBadge}
          </td>
        </tr>
      `;
    })
    .join('');
}

function renderUsuariosPagination(total, page, perPage) {
  const container = document.getElementById('usuarios-pagination');
  if (!container) return;

  const totalPages = Math.max(1, Math.ceil(total / perPage));
  if (totalPages <= 1) {
    container.innerHTML = '';
    return;
  }

  const prevDisabled = page <= 1;
  const nextDisabled = page >= totalPages;

  container.innerHTML = `
    <button
      class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-lg text-sm
             ${prevDisabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}"
      ${prevDisabled ? 'disabled' : ''}
      data-page="${page - 1}">
      <i class="fas fa-chevron-left"></i>
    </button>
    <span class="text-sm text-gray-600 dark:text-gray-400">
      Página ${page} de ${totalPages}
    </span>
    <button
      class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-lg text-sm
             ${nextDisabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100 dark:hover:bg-gray-700'}"
      ${nextDisabled ? 'disabled' : ''}
      data-page="${page + 1}">
      <i class="fas fa-chevron-right"></i>
    </button>
  `;

  container.querySelectorAll('button[data-page]').forEach(btn => {
    btn.addEventListener('click', e => {
      const newPage = parseInt(e.currentTarget.getAttribute('data-page'), 10);
      if (!Number.isNaN(newPage)) {
        loadUsuarios(newPage);
      }
    });
  });
}

/* =========================
   CREAR ADMIN / DUEÑO
========================= */

async function handleCrearAdmin(e) {
  e.preventDefault();

  const username = document.getElementById('admin-username')?.value.trim();
  const password = document.getElementById('admin-password')?.value.trim();
  const nombres = document.getElementById('admin-nombres')?.value.trim();
  const apellidos = document.getElementById('admin-apellidos')?.value.trim();
  const email = document.getElementById('admin-email')?.value.trim();
  const telefono = document.getElementById('admin-telefono')?.value.trim();
  const ci = document.getElementById('admin-ci')?.value.trim();
  const direccion = document.getElementById('admin-direccion')?.value.trim();
  const activo = document.getElementById('admin-activo')?.checked ?? true;

  if (!username || !password || !nombres || !apellidos) {
    showToast('Usuario, contraseña, nombres y apellidos son obligatorios', 'error');
    return;
  }

  const payload = {
    username,
    password,
    nombres,
    apellidos,
    email: email || null,
    telefono: telefono || null,
    ci_numero: ci || null,
    direccion: direccion || null,
    rol: 'ADMINISTRADOR', // o DUENO, aquí lo dejamos fijo en mock
    activo,
  };

  const btn = e.target.querySelector('button[type="submit"]');
  const originalHtml = btn ? btn.innerHTML : null;
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Guardando...';
  }

  try {
    const response = await fetchAPI(`${API_BASE}/usuarios`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error('Error al crear usuario');

    showToast('Usuario creado correctamente', 'success');
    closeModal('modal-admin');
    e.target.reset();
    loadUsuarios();
  } catch (err) {
    console.error(err);
    showToast('No se pudo crear el usuario', 'error');
  } finally {
    if (btn && originalHtml) {
      btn.disabled = false;
      btn.innerHTML = originalHtml;
    }
  }
}

/* =========================
   CREAR PROFESORA
========================= */

let lastProfCodigo = null;
let lastProfTelefono = null;
let lastProfNombre = null;

async function handleCrearProfesora(e) {
  e.preventDefault();

  const nombres = document.getElementById('prof-nombres')?.value.trim();
  const apellidos = document.getElementById('prof-apellidos')?.value.trim();
  const telefono = document.getElementById('prof-telefono')?.value.trim();
  const email = document.getElementById('prof-email')?.value.trim();

  if (!nombres || !apellidos || !telefono) {
    showToast('Nombres, apellidos y teléfono son obligatorios', 'error');
    return;
  }

  const payload = {
    tipo: 'PROFESORA',
    nombres,
    apellidos,
    telefono,
    email: email || null,
  };

  const btn = e.target.querySelector('button[type="submit"]');
  const originalHtml = btn ? btn.innerHTML : null;
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Creando...';
  }

  try {
    const response = await fetchAPI(`${API_BASE}/usuarios/profesora`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || 'Error al crear profesora');

    const codigo = data.codigo || data.codigo_acceso || data.codigo_profesora || 'ABC123';
    lastProfCodigo = codigo;
    lastProfTelefono = telefono;
    lastProfNombre = `${nombres} ${apellidos}`.trim();

    const codigoSpan = document.getElementById('prof-codigo-display');
    if (codigoSpan) codigoSpan.textContent = codigo;

    closeModal('modal-profesora');
    openModal('modal-profesora-codigo');
    e.target.reset();
    loadUsuarios();
  } catch (err) {
    console.error(err);
    showToast('No se pudo crear la profesora', 'error');
  } finally {
    if (btn && originalHtml) {
      btn.disabled = false;
      btn.innerHTML = originalHtml;
    }
  }
}

function copiarCodigoProfesora() {
  if (!lastProfCodigo) return;
  navigator.clipboard
    .writeText(lastProfCodigo)
    .then(() => showToast('Código copiado al portapapeles', 'success'))
    .catch(() => showToast('No se pudo copiar el código', 'error'));
}

function enviarWhatsAppProfesora() {
  if (!lastProfCodigo || !lastProfTelefono) {
    showToast('No hay datos de profesora generados', 'error');
    return;
  }

  const appUrl = window.location.origin;
  const nombre = lastProfNombre || '';
  const mensaje = encodeURIComponent(
    `Hola ${nombre}, te damos la bienvenida a Datilera.\n\nTu código de acceso es: ${lastProfCodigo}\n\nPara completar tu registro, ingresa a:\n${appUrl}/registro-profesora\n\nEste código es personal e intransferible.`,
  );
  const url = `https://wa.me/591${lastProfTelefono}?text=${mensaje}`;
  window.open(url, '_blank');
}

/* =========================
   HELPERS
========================= */

function openModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('hidden');
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('hidden');
}

function getInitials(name) {
  if (!name) return '?';
  const parts = name.trim().split(' ');
  if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
  return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase();
}

function formatRol(rol) {
  if (!rol) return 'Sin Rol';
  if (rol === 'ADMINISTRADOR') return 'Admin';
  if (rol === 'DUENO') return 'Dueño'
  if (rol === 'PROFESORA') return 'Profesora';
  if (rol === 'TUTOR') return 'Tutor';
  return rol;
}

function debounce(fn, wait) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), wait);
  };
}


/* ==========================================
   NUEVA LÓGICA: ASIGNACIÓN DE AULA
   ========================================== */

// Se hacen globales (window) para que funcionen con los onclick="..." del HTML si es necesario
// o simplemente se llaman desde el listener que acabamos de agregar.

window.abrirModalAsignacion = async function() {
  const modal = document.getElementById('modal-asignacion-profesora');
  if (!modal) return;
  
  modal.classList.remove('hidden');
  
  // Animación suave de entrada (opcional)
  const content = modal.querySelector('div');
  if(content) {
      content.classList.remove('scale-95', 'opacity-0');
      content.classList.add('scale-100', 'opacity-100');
  }

  // Cargar datos en paralelo
  await Promise.all([cargarProfesoresDisponibles(), cargarGruposYParalelos()]);
}

window.cerrarModalAsignacion = function() {
  const modal = document.getElementById('modal-asignacion-profesora');
  if (!modal) return;

  modal.classList.add('hidden');
  
  // Limpiar selects visualmente para la próxima vez
  const selectProf = document.getElementById('select-profesora-asignar');
  if(selectProf) selectProf.innerHTML = '<option value="">Cargando...</option>';
  
  const selectParalelo = document.getElementById('select-paralelo-asignar');
  if(selectParalelo) {
    selectParalelo.innerHTML = '<option value="">Esperando grupo...</option>';
    selectParalelo.disabled = true;
    selectParalelo.className = "w-full px-4 py-2.5 bg-gray-100 dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg text-gray-500 dark:text-gray-300 cursor-not-allowed";
  }

  const msgError = document.getElementById('msg-no-paralelos');
  if(msgError) msgError.classList.add('hidden');
}

async function cargarProfesoresDisponibles() {
  const select = document.getElementById('select-profesora-asignar');
  if(!select) return;

  try {
      // Usa tu función fetchAPI de main.js
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
      showToast('Error al cargar profesoras disponibles', 'error');
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
  const grupoId = parseInt(document.getElementById('select-grupo-asignar').value);
  const selectParalelo = document.getElementById('select-paralelo-asignar');
  const msgError = document.getElementById('msg-no-paralelos');
  
  // Resetear estado del select paralelo
  if(selectParalelo) {
      selectParalelo.innerHTML = '<option value="">Seleccione Paralelo...</option>';
      selectParalelo.disabled = true;
      selectParalelo.className = "w-full px-4 py-2.5 bg-gray-100 dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg text-gray-500 dark:text-gray-300 cursor-not-allowed";
  }
  if(msgError) msgError.classList.add('hidden');

  if (!grupoId) return;

  // Buscar en caché
  const grupo = cacheGruposParalelos.find(g => g.id === grupoId);
  
  if (grupo && grupo.paralelos && grupo.paralelos.length > 0) {
      // Habilitar Select
      selectParalelo.disabled = false;
      selectParalelo.className = "w-full px-4 py-2.5 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500";

      grupo.paralelos.forEach(p => {
          const opt = document.createElement('option');
          opt.value = p.id;
          opt.textContent = p.nombre;
          selectParalelo.appendChild(opt);
      });
  } else {
      // Mostrar alerta
      showToast('Este grupo no tiene paralelos disponibles. Cree uno en Académico.', 'warning');
      if(msgError) msgError.classList.remove('hidden'); 
  }
}

window.guardarAsignacion = async function() {
  const profesorId = document.getElementById('select-profesora-asignar').value;
  const paraleloId = document.getElementById('select-paralelo-asignar').value;

  if (!profesorId || !paraleloId) {
      showToast('Debe seleccionar Profesora y Paralelo', 'warning');
      return;
  }

  const btnGuardar = document.querySelector('#modal-asignacion-profesora button:last-child');
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
          showToast('Profesora asignada correctamente', 'success');
          cerrarModalAsignacion();
          // Recargar tabla de usuarios si la función existe
          if (typeof loadUsuarios === 'function') loadUsuarios(currentPage);
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