// app/interfaces/web/static/js/main.js

/* ============================================================
   CONFIGURACIÓN GLOBAL
   ============================================================ */
const API_BASE = '/api/v1';
// CAMBIO: Detectar protocolo seguro (wss) automáticamente
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_BASE = `${WS_PROTOCOL}//${window.location.host}/api/v1`;

/* ============================================================
   HELPERS DE FETCH CON RETRY Y REFRESH TOKEN
   ============================================================ */
export async function fetchAPI(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Para enviar cookies
    };


    const config = { ...defaultOptions, ...options };
    
    // Merge headers
    if (options.headers) {
        config.headers = { ...defaultOptions.headers, ...options.headers };
    }

    // Manejo correcto de Content-Type para FormData y JSON
    if (options.body instanceof FormData) {
        // Dejar que el navegador establezca el boundary automáticamente
        delete config.headers['Content-Type'];
    } else if (!config.headers['Content-Type']) {
        // Solo agregar application/json si no está definido y no es FormData
        config.headers['Content-Type'] = 'application/json';
    }

    try {
        let response = await fetch(url, config);

        // Si es 401 (token expirado), intentar refresh
        if (response.status === 401) {
            const refreshed = await refreshAccessToken();
            if (refreshed) {
                // NO tocar Authorization; la cookie HttpOnly ya se actualizó
                response = await fetch(url, config);
            } else {
                window.location.href = '/login';
                throw new Error('Session expired');
            }
            }


        // Si es 5xx, reintentar con backoff
        if (response.status >= 500 && response.status < 600) {
            return await retryWithBackoff(url, config);
        }

        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

async function refreshAccessToken() {
    try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
    });
    return response.ok;
    } catch (error) {
    console.error('Error refreshing token:', error);
    return false;
    }
}


async function retryWithBackoff(url, config, maxRetries = 3) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch(url, config);
            if (response.ok || response.status < 500) {
                return response;
            }
            // Backoff exponencial: 1s, 2s, 4s
            await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        } catch (error) {
            if (i === maxRetries - 1) throw error;
        }
    }
    throw new Error('Max retries reached');
}

/* ============================================================
   SWEETALERT2 WRAPPERS
   ============================================================ */
export function showToast(message, type = 'success') {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer);
            toast.addEventListener('mouseleave', Swal.resumeTimer);
        }
    });

    Toast.fire({
        icon: type,
        title: message
    });
}

export function showConfirm(title, text, confirmText = 'Confirmar') {
    return Swal.fire({
        title: title,
        text: text,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#f59e0b',
        cancelButtonColor: '#6b7280',
        confirmButtonText: confirmText,
        cancelButtonText: 'Cancelar',
        reverseButtons: true
    });
}

/* ============================================================
   THEME MANAGEMENT (Dark/Light Mode)
   ============================================================ */
export function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;

    // Detectar preferencia del sistema
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Cargar preferencia del usuario desde localStorage (temporal)
    // TODO: Sincronizar con BD después
    let currentTheme = localStorage.getItem('theme');
    
    if (!currentTheme) {
        currentTheme = systemPrefersDark ? 'dark' : 'light';
        localStorage.setItem('theme', currentTheme);
    }

    // Aplicar tema
    applyTheme(currentTheme);

    // Toggle theme
    themeToggle.addEventListener('click', async () => {
        const newTheme = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
        applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        
        // TODO: Guardar en BD
        await saveThemeToServer(newTheme);
    });

    // Escuchar cambios del sistema
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });
}

function applyTheme(theme) {
    if (theme === 'dark') {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
}

async function saveThemeToServer(theme) {
    try {
        await fetchAPI(`${API_BASE}/usuarios/me/preferencias`, {
            method: 'PATCH',
            body: JSON.stringify({ theme }),
        });
    } catch (error) {
        console.error('Error saving theme:', error);
    }
}

/* ============================================================
   WEBSOCKET - NOTIFICACIONES EN TIEMPO REAL
   ============================================================ */
let ws = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

export function initWebSocket() {
    // CAMBIO 1: Usamos /ws/chat para todo (Notificaciones y Chat unificados)
    // CAMBIO 2: No enviamos token en URL, usamos la Cookie HttpOnly automática
    const wsUrl = `${WS_BASE}/ws/chat`; 
    
    console.log(`📡 Conectando Notificaciones a: ${wsUrl}`);
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ Sistema de Notificaciones Conectado');
        reconnectAttempts = 0;
    };

    ws.onmessage = (event) => {
        try {
            const payload = JSON.parse(event.data);
            
            // CAMBIO 3: Manejar estructura de eventos { type, data }
            // Tu backend (events.py) envía: type="notification.new"
            if (payload.type === 'notification.new') {
                handleNotification(payload.data);
            }
            // Puedes agregar más tipos aquí si es necesario
            
        } catch (e) {
            console.error("Error procesando notificación:", e);
        }
    };

    ws.onerror = (error) => {
        // Silenciar error en consola para no ensuciar, el onclose reconecta
        // console.error('WebSocket error:', error); 
    };

    ws.onclose = (e) => {
        console.warn('WebSocket desconectado (Notificaciones)');
        
        // Intentar reconectar con backoff exponencial
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            const delay = Math.pow(2, reconnectAttempts) * 1000;
            reconnectAttempts++;
            
            console.log(`Reconectando en ${delay}ms... (intento ${reconnectAttempts})`);
            setTimeout(initWebSocket, delay);
        } else {
            console.log('Dejando de intentar reconexión automática (Notificaciones)');
        }
    };
}

function handleNotification(notification) {
    console.log('Nueva notificación recibida:', notification);
    
    // 1. Actualizar badge (campanita)
    updateNotificationBadge();
    
    // 2. Mostrar toast flotante
    // Nota: 'mensaje' viene dentro de 'notification' según tu events.py
    showToast(notification.mensaje || notification.titulo, 'info');
    
    // 3. Si el panel está abierto, agregar a la lista
    const panel = document.getElementById('notifications-panel');
    if (panel && !panel.classList.contains('translate-x-full')) {
        addNotificationToList(notification);
    }
    
    // 4. Reproducir sonido
    playNotificationSound();
}

/* ============================================================
   NOTIFICATIONS PANEL
   ============================================================ */
export function initNotifications() {
    const notificationsBtn = document.getElementById('notifications-btn');
    const notificationsPanel = document.getElementById('notifications-panel');
    const notificationsOverlay = document.getElementById('notifications-overlay');
    const closeBtn = document.getElementById('close-notifications');

    if (!notificationsBtn) return;

    // Abrir panel
    notificationsBtn.addEventListener('click', () => {
        notificationsPanel.classList.remove('translate-x-full');
        notificationsOverlay.classList.remove('hidden');
        loadNotifications();
    });

    // Cerrar panel
    closeBtn.addEventListener('click', closeNotificationsPanel);
    notificationsOverlay.addEventListener('click', closeNotificationsPanel);

    // Filtros
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active', 'bg-primary-100', 'dark:bg-primary-900', 'text-primary-700', 'dark:text-primary-300'));
            e.target.classList.add('active', 'bg-primary-100', 'dark:bg-primary-900', 'text-primary-700', 'dark:text-primary-300');
            
            const filter = e.target.dataset.filter;
            loadNotifications(filter);
        });
    });

    // Cargar notificaciones iniciales
    loadNotifications();
    updateNotificationBadge();
}

function closeNotificationsPanel() {
    const notificationsPanel = document.getElementById('notifications-panel');
    const notificationsOverlay = document.getElementById('notifications-overlay');
    
    notificationsPanel.classList.add('translate-x-full');
    notificationsOverlay.classList.add('hidden');
}

async function loadNotifications(filter = 'all') {
    const list = document.getElementById('notifications-list');
    list.innerHTML = '<div class="text-center py-4"><i class="fas fa-spinner fa-spin text-2xl text-gray-400"></i></div>';

    try {
        const url = filter === 'unread' 
            ? `${API_BASE}/notificaciones?leida=false` 
            : `${API_BASE}/notificaciones`;
        
        const response = await fetchAPI(url);
        const data = await response.json();

        if (data.items && data.items.length > 0) {
            list.innerHTML = data.items.map(n => createNotificationHTML(n)).join('');
            
            // Agregar event listeners para marcar como leída
            document.querySelectorAll('.notification-item').forEach(item => {
                item.addEventListener('click', () => markAsRead(item.dataset.id));
            });
        } else {
            list.innerHTML = `
                <div class="text-center text-gray-500 dark:text-gray-400 py-8">
                    <i class="fas fa-bell-slash text-4xl mb-2"></i>
                    <p>No hay notificaciones</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        list.innerHTML = '<div class="text-center text-red-500 py-4">Error al cargar notificaciones</div>';
    }
}

function createNotificationHTML(notification) {
    const unreadClass = !notification.leida ? 'unread' : '';
    const timeAgo = formatTimeAgo(notification.fecha_creacion);
    
    return `
        <div class="notification-item ${unreadClass}" data-id="${notification.id}">
            <div class="flex items-start space-x-3">
                <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                        <i class="fas fa-${getNotificationIcon(notification.tipo)} text-primary-600 dark:text-primary-400"></i>
                    </div>
                </div>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white">${notification.titulo}</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">${notification.mensaje}</p>
                    <p class="text-xs text-gray-400 dark:text-gray-500 mt-2">${timeAgo}</p>
                </div>
                ${!notification.leida ? '<div class="flex-shrink-0"><div class="w-2 h-2 bg-primary-500 rounded-full"></div></div>' : ''}
            </div>
        </div>
    `;
}

function getNotificationIcon(tipo) {
    const icons = {
        'PAGO': 'dollar-sign',
        'ACADEMICO': 'graduation-cap',
        'MENSAJE': 'comment',
        'SISTEMA': 'info-circle',
        'ALERTA': 'exclamation-triangle',
    };
    return icons[tipo] || 'bell';
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Ahora';
    if (diffMins < 60) return `Hace ${diffMins} min`;
    if (diffHours < 24) return `Hace ${diffHours} h`;
    if (diffDays < 7) return `Hace ${diffDays} d`;
    return date.toLocaleDateString('es-BO');
}

async function markAsRead(notificationId) {
    try {
        await fetchAPI(`${API_BASE}/notificaciones/${notificationId}/leer`, {
            method: 'PATCH',
        });
        updateNotificationBadge();
    } catch (error) {
        console.error('Error marking notification as read:', error);
    }
}

async function updateNotificationBadge() {
    try {
        const response = await fetchAPI(`${API_BASE}/notificaciones?leida=false`);
        const data = await response.json();
        
        const badge = document.getElementById('notification-badge');
        const count = data.total || 0;
        
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    } catch (error) {
        console.error('Error updating notification badge:', error);
    }
}

function addNotificationToList(notification) {
    const list = document.getElementById('notifications-list');
    if (!list) return;

    // Si la lista está vacía, limpiarla
    if (list.querySelector('.text-center')) {
        list.innerHTML = '';
    }

    // Agregar notificación al principio
    const html = createNotificationHTML(notification);
    list.insertAdjacentHTML('afterbegin', html);
}

function playNotificationSound() {
    // Opcional: reproducir sonido
    // const audio = new Audio('/static/sounds/notification.mp3');
    // audio.play().catch(e => console.log('Could not play sound:', e));
}

/* ============================================================
   LOGOUT
   ============================================================ */
window.logout = async function() {
    const result = await showConfirm(
        '¿Cerrar sesión?',
        'Se cerrará tu sesión actual',
        'Sí, cerrar'
    );

    if (result.isConfirmed) {
        try {
            await fetchAPI(`${API_BASE}/auth/logout`, {
                method: 'POST',
            });

            // Limpiar tokens
            sessionStorage.removeItem('access_token');
            
            // Cerrar WebSocket
            if (ws) {
                ws.close();
            }

            // Redirigir a login
            window.location.href = '/login';
        } catch (error) {
            console.error('Error logging out:', error);
            showToast('Error al cerrar sesión', 'error');
        }
    }
}

/* ============================================================
   INICIALIZACIÓN GLOBAL
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initNotifications();
    initWebSocket();
});