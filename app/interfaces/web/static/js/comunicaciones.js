// app/interfaces/web/static/js/comunicaciones.js

import { fetchAPI, showToast, showConfirm } from './main.js';

const API_BASE = '/api/v1';
// Detectar si estamos en https para usar wss (WebSocket Secure)
const WS_PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_BASE = `${WS_PROTOCOL}//${window.location.host}/api/v1`;

/* ============================================================
   VARIABLES GLOBALES
   ============================================================ */
let chatWebSocket = null;
let currentConversationId = null;
let currentUserId = null; // Se llenará al iniciar
let currentFilter = 'all';
let currentMensajesPage = 1;
let isTyping = false;
let typingTimeout = null;
let usersCache = []; // Cache para el buscador de destinatarios

/* ============================================================
   INICIALIZACIÓN
   ============================================================ */
document.addEventListener('DOMContentLoaded', async () => {
    // 1. Obtener ID del usuario actual para saber "quién soy" en el chat
    await loadCurrentUser();

    initTabs();
    initChat();
    loadConversations();
    loadMensajes();
    loadComunicados();
    initModals();
    initSearchFilters();
    
   
    loadRecipients();

    
    const params = new URLSearchParams(window.location.search);
    
    if (params.get('action') === 'nueva_notificacion') {
        // Damos un pequeño tiempo (800ms) para asegurar que el HTML y listas de usuarios carguen
        setTimeout(() => {
            // 1. Abrir el modal de notificación
            // Asegúrate que esta función exista abajo (ya la tienes definida como window.openNewNotificaacionModal)
            if (typeof openNewNotificaacionModal === 'function') {
                openNewNotificaacionModal();
            } else {
                // Fallback por si acaso
                document.getElementById('new-notificacion-modal')?.classList.remove('hidden');
            }

            // 2. Si viene por tema de deuda, pre-llenamos los textos
            if (params.get('context') === 'deuda') {
                const tituloInput = document.getElementById('notif-titulo');
                const mensajeInput = document.getElementById('notif-mensaje');
                const prioridadSelect = document.getElementById('notif-prioridad');
                const tipoSelect = document.getElementById('notif-tipo');

                if (tituloInput) tituloInput.value = "Recordatorio de Pago de Mensualidad";
                if (mensajeInput) mensajeInput.value = "Estimado padre de familia/tutor, le recordamos amablemente pasar por administración para regularizar las cuotas pendientes.";
                
                if (prioridadSelect) prioridadSelect.value = "ALTA"; 
                
                // Intenta poner PAGOS, si no existe en tu select, pone RECORDATORIO
                if (tipoSelect) {
                    const tienePagos = [...tipoSelect.options].some(o => o.value === 'PAGOS');
                    tipoSelect.value = tienePagos ? "PAGOS" : "RECORDATORIO";
                }
                
                showToast('Complete el destinatario manualmente', 'info');
            }

            // 3. Limpiar la URL para que no se abra de nuevo al recargar la página
            window.history.replaceState({}, document.title, window.location.pathname);
        }, 800); 
    }
    
});

// Función para identificar al usuario actual (necesaria para el chat)
async function loadCurrentUser() {
    try {
        const res = await fetchAPI(`${API_BASE}/usuarios/me`); 
        if (res.ok) {
            const user = await res.json();
            currentUserId = user.id;
        }
    } catch (e) {
        console.warn("No se pudo identificar al usuario actual para el chat");
    }
}

/* ============================================================
   GESTIÓN DE TABS
   ============================================================ */
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            
            // Actualizar botones
            tabButtons.forEach(b => {
                b.classList.remove('active', 'border-primary-600', 'text-primary-600', 'dark:text-primary-500');
                b.classList.add('border-transparent', 'text-gray-600', 'dark:text-gray-400');
            });
            
            btn.classList.add('active', 'border-primary-600', 'text-primary-600', 'dark:text-primary-500');
            btn.classList.remove('border-transparent', 'text-gray-600', 'dark:text-gray-400');
            
            // Mostrar contenido correspondiente
            tabContents.forEach(content => {
                content.classList.add('hidden');
                content.classList.remove('active');
            });
            
            const activeContent = document.getElementById(`tab-${tabName}`);
            activeContent.classList.remove('hidden');
            activeContent.classList.add('active');
            
            // Cargar datos según el tab
            if (tabName === 'mensajes') {
                loadMensajes();
            } else if (tabName === 'comunicados') {
                loadComunicados();
            } else if (tabName === 'historial') {
                loadHistorial();
            }
        });
    });
}

/* ============================================================
   CHAT EN TIEMPO REAL - WEBSOCKET
   ============================================================ */
function initChat() {
    const wsUrl = `${WS_BASE}/ws/chat`;
    console.log(`Conectando WS a: ${wsUrl}`);
    
    chatWebSocket = new WebSocket(wsUrl);
    
    chatWebSocket.onopen = () => {
        console.log('✅ Chat WebSocket connected');
    };
    
    chatWebSocket.onmessage = (event) => {
        try {
            const payload = JSON.parse(event.data);
            handleWebSocketEvent(payload);
        } catch (e) {
            console.error("Error procesando mensaje WS:", e);
        }
    };
    
    chatWebSocket.onerror = (error) => {
        // console.error('Chat WebSocket error:', error); // Silenciado para evitar ruido en reconexión
    };
    
    chatWebSocket.onclose = () => {
        console.warn('Chat WebSocket disconnected');
        setTimeout(initChat, 3000);
    };
    
    // Formulario de envío de mensaje
    const form = document.getElementById('send-message-form');
    if(form) form.addEventListener('submit', handleSendMessage);
    
    // Auto-resize del textarea
    const textarea = document.getElementById('message-input');
    if(textarea) {
        textarea.addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
            sendTypingIndicator();
        });
    }
}

function handleWebSocketEvent(payload) {
    const { type, data } = payload;
    // console.log("WS Event:", type, data);

    switch (type) {
        case 'chat.message': 
            if (currentConversationId && data.conversacion_id == currentConversationId) {
                const msgFormatted = {
                    id: data.mensaje_id,
                    contenido: data.texto,
                    emisor_id: data.remitente_id,
                    emisor_nombre: data.remitente_nombre,
                    fecha_envio: data.enviado_en,
                    es_mio: data.remitente_id === currentUserId,
                    leido: false
                };
                appendMessageToChat(msgFormatted);
                scrollChatToBottom();
                if (!msgFormatted.es_mio) markMessageAsRead(msgFormatted.id);
            } else {
                updateConversationBadge(data.conversacion_id); 
                const exists = document.querySelector(`.conversation-item[data-conversation-id="${data.conversacion_id}"]`);
                if (!exists) loadConversations();
                else showToast(`Nuevo mensaje de ${data.remitente_nombre || 'chat'}`, 'info');
            }
            break;

        case 'chat.typing': 
            if (currentConversationId && data.conversation_id == currentConversationId && data.user_id !== currentUserId) {
                showTypingIndicator(data.user_name || 'Alguien');
            }
            break;

        case 'chat.stop_typing':
            hideTypingIndicator();
            break;

        case 'notification.new':
            showToast(data.mensaje || data.titulo, 'info');
            break;
            
        case 'chat.read':
             if (currentConversationId && data.conversation_id == currentConversationId) {
                 updateMessageReadStatus(data.mensaje_id);
             }
             break;
    }
}

function sendTypingIndicator() {
    if (!currentConversationId || !chatWebSocket || chatWebSocket.readyState !== WebSocket.OPEN) return;
    
    if (!isTyping) {
        isTyping = true;
        chatWebSocket.send(JSON.stringify({
            type: 'typing',
            conversation_id: currentConversationId,
            target_user_id: getTargetUserId()
        }));
    }
    
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        isTyping = false;
        chatWebSocket.send(JSON.stringify({
            type: 'stop_typing',
            conversation_id: currentConversationId,
            target_user_id: getTargetUserId()
        }));
    }, 1000);
}

function getTargetUserId() {
    return null; // El backend gestiona el broadcast a la sala
}

function showTypingIndicator(userName) {
    const container = document.getElementById('chat-messages');
    const existing = document.getElementById('typing-indicator');
    if (existing) existing.remove();
    
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 p-2';
    indicator.innerHTML = `
        <span class="font-medium text-xs">${userName} está escribiendo</span>
        <div class="flex space-x-1">
            <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
            <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
        </div>
    `;
    container.appendChild(indicator);
    scrollChatToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

/* ============================================================
   CARGAR CONVERSACIONES
   ============================================================ */
async function loadConversations() {
    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/conversaciones`);
        const data = await response.json();
        const container = document.getElementById('conversations-list');
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = data.items.map(conv => {
                
                // LÓGICA DE AVATAR:
                // Si hay foto, usamos <img>. Si no, usamos tu diseño original con degradado.
                const avatarHTML = conv.usuario_avatar
                    ? `<img src="${conv.usuario_avatar}" 
                           alt="${conv.usuario_nombre}" 
                           class="w-12 h-12 rounded-full object-cover mr-3 flex-shrink-0 border border-gray-200 dark:border-gray-600">`
                    : `<div class="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold mr-3 flex-shrink-0">
                           ${getInitials(conv.usuario_nombre)}
                       </div>`;

                return `
                <div class="conversation-item p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-200 dark:border-gray-700 ${conv.id === currentConversationId ? 'bg-primary-50 dark:bg-primary-900/20' : ''}" 
                     data-conversation-id="${conv.id}"
                     onclick="openConversation(${conv.id})">
                    <div class="flex items-start">
                        
                        ${avatarHTML}

                        <div class="flex-1 min-w-0">
                            <div class="flex items-center justify-between mb-1">
                                <h4 class="font-semibold text-gray-900 dark:text-white truncate">${conv.usuario_nombre}</h4>
                                <span class="text-xs text-gray-500 dark:text-gray-400">${formatTime(conv.ultimo_mensaje_fecha)}</span>
                            </div>
                            <p class="text-sm text-gray-600 dark:text-gray-400 truncate">${conv.ultimo_mensaje || 'Sin mensajes'}</p>
                            ${conv.no_leidos > 0 ? `
                            <span class="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full mt-1">
                                ${conv.no_leidos}
                            </span>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `}).join('');
        } else {
            container.innerHTML = `
                <div class="flex items-center justify-center h-full p-8">
                    <div class="text-center">
                        <i class="fas fa-inbox text-5xl text-gray-300 dark:text-gray-700 mb-4"></i>
                        <p class="text-gray-600 dark:text-gray-400">No hay conversaciones</p>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
    }
}
window.openConversation = async function(conversationId) {
    currentConversationId = conversationId;
    
    try {
        // 1. Obtener datos de la conversación
        const response = await fetchAPI(`${API_BASE}/comunicaciones/conversaciones/${conversationId}`);
        const data = await response.json();
        
        // 2. Extraer variables (DEFINIRLAS AQUÍ)
        const nombreUsuario = data.usuario_nombre || 'Usuario';
        let avatarUrl = data.usuario_avatar;
        if (avatarUrl && (avatarUrl.length < 4 || !avatarUrl.includes('/'))) {
            avatarUrl = null;
}
        const rolUsuario = data.usuario_rol || '';

        // 3. Mostrar la interfaz del chat
        const header = document.getElementById('chat-header');
        const inputContainer = document.getElementById('chat-input-container');
        if (header) header.classList.remove('hidden');
        if (inputContainer) inputContainer.classList.remove('hidden');
        
        // 4. Actualizar Nombre y Rol
        const headerName = document.getElementById('chat-name');
        const headerRole = document.getElementById('chat-role');
        if (headerName) headerName.textContent = nombreUsuario;
        if (headerRole) headerRole.textContent = rolUsuario;

        // 5. ACTUALIZAR AVATAR (Usando el Wrapper)
        const headerWrapper = document.getElementById('chat-header-avatar-wrapper');
        
        if (headerWrapper) {
            if (avatarUrl) {
                // OPCIÓN A: Tiene Foto -> Ponemos la imagen
                headerWrapper.innerHTML = `
                    <img src="${avatarUrl}" 
                         alt="${nombreUsuario}" 
                         class="w-10 h-10 rounded-full object-cover mr-3 border border-gray-200 dark:border-gray-600">
                `;
            } else {
                // OPCIÓN B: No tiene foto -> Ponemos Iniciales con degradado
                headerWrapper.innerHTML = `
                    <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold mr-3">
                        <span>${getInitials(nombreUsuario)}</span>
                    </div>
                `;
            }
        }
        
        // 6. Cargar mensajes y actualizar estilo de la lista
        await loadChatMessages(conversationId);
        
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('bg-primary-50', 'dark:bg-primary-900/20');
        });
        document.querySelector(`[data-conversation-id="${conversationId}"]`)?.classList.add('bg-primary-50', 'dark:bg-primary-900/20');
        
    } catch (error) {
        console.error('Error opening conversation:', error);
    }
};

async function loadChatMessages(conversationId) {
    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/conversaciones/${conversationId}/mensajes`);
        const data = await response.json();
        const container = document.getElementById('chat-messages');
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = data.items.map(msg => renderChatMessage(msg)).join('');
            scrollChatToBottom();
        } else {
            container.innerHTML = `
                <div class="flex items-center justify-center h-full">
                    <p class="text-gray-600 dark:text-gray-400">No hay mensajes aún. ¡Inicia la conversación!</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading chat messages:', error);
    }
}

function renderChatMessage(msg) {
    const isMine = (msg.es_mio !== undefined) ? msg.es_mio : (msg.emisor_id === currentUserId);
    
    return `
        <div class="flex ${isMine ? 'justify-end' : 'justify-start'} mb-4">
            <div class="max-w-xs lg:max-w-md">
                ${!isMine ? `<p class="text-xs text-gray-600 dark:text-gray-400 mb-1 ml-1">${msg.emisor_nombre || ''}</p>` : ''}
                <div class="px-4 py-2 rounded-2xl ${isMine ? 'bg-primary-600 text-white rounded-br-none' : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-bl-none shadow-sm'}">
                    <p class="text-sm whitespace-pre-wrap">${escapeHtml(msg.contenido)}</p>
                </div>
                <div class="flex items-center ${isMine ? 'justify-end' : 'justify-start'} mt-1 space-x-1 px-1">
                    <span class="text-[10px] text-gray-400">${formatTime(msg.fecha_envio)}</span>
                    ${isMine && msg.leido ? '<i class="fas fa-check-double text-[10px] text-blue-400"></i>' : ''}
                    ${isMine && !msg.leido ? '<i class="fas fa-check text-[10px] text-gray-400"></i>' : ''}
                </div>
            </div>
        </div>
    `;
}

function appendMessageToChat(msg) {
    const container = document.getElementById('chat-messages');
    const emptyState = container.querySelector('.flex.items-center.justify-center');
    if (emptyState) container.innerHTML = '';
    
    const messageElement = document.createElement('div');
    messageElement.innerHTML = renderChatMessage(msg);
    container.appendChild(messageElement.firstElementChild);
}

function scrollChatToBottom() {
    const container = document.getElementById('chat-messages');
    if(container) container.scrollTop = container.scrollHeight;
}

async function handleSendMessage(e) {
    e.preventDefault();
    if (!currentConversationId) {
        showToast('Selecciona una conversación primero', 'warning');
        return;
    }
    
    const textarea = document.getElementById('message-input');
    const contenido = textarea.value.trim();
    if (!contenido) return;
    
    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/conversaciones/${currentConversationId}/mensajes`, {
            method: 'POST',
            body: JSON.stringify({ contenido })
        });
        
        if (response.ok) {
            textarea.value = '';
            textarea.style.height = 'auto';
        } else {
            throw new Error('Error al enviar mensaje');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('Error al enviar mensaje', 'error');
    }
}

async function markMessageAsRead(messageId) {
    try {
        await fetchAPI(`${API_BASE}/comunicaciones/mensajes/${messageId}/leer`, { method: 'PATCH' });
    } catch (error) { console.error('Error marking message as read:', error); }
}

function updateMessageReadStatus(messageId) {
    // Implementar si se desea feedback visual en tiempo real de lectura
}

window.markConversationAsRead = async function() {
    if (!currentConversationId) return;
    try {
        await fetchAPI(`${API_BASE}/comunicaciones/conversaciones/${currentConversationId}/marcar-leido`, { method: 'PATCH' });
        showToast('Marcado como leído', 'success');
        loadConversations();
    } catch (error) { console.error('Error marking as read:', error); }
}

window.archiveConversation = async function() {
    if (!currentConversationId) return;
    const result = await showConfirm('¿Archivar conversación?', 'La conversación será archivada', 'Archivar');
    if (!result.isConfirmed) return;
    
    try {
        await fetchAPI(`${API_BASE}/comunicaciones/conversaciones/${currentConversationId}/archivar`, { method: 'PATCH' });
        showToast('Conversación archivada', 'success');
        currentConversationId = null;
        loadConversations();
        document.getElementById('chat-header').classList.add('hidden');
        document.getElementById('chat-input-container').classList.add('hidden');
        document.getElementById('chat-messages').innerHTML = `<div class="flex items-center justify-center h-full"><p class="text-gray-600 dark:text-gray-400">Selecciona una conversación</p></div>`;
    } catch (error) { console.error('Error archiving conversation:', error); showToast('Error al archivar', 'error'); }
}

/* ============================================================
   MENSAJES (TAB BANDEJA DE ENTRADA)
   ============================================================ */
async function loadMensajes(filter = 'all', page = 1) {
    currentFilter = filter;
    currentMensajesPage = page;
    // 1. VALIDACIÓN DE SEGURIDAD (AGREGAR ESTO)
    const container = document.getElementById('mensajes-list');
    if (!container) return; // Si no existe el div, detenemos la función aquí.

    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/mensajes?filter=${filter}&page=${page}&per_page=20`);
        const data = await response.json();
        // const container = document.getElementById('mensajes-list'); // <-- BORRA O COMENTA ESTA LÍNEA ANTIGUA
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = data.items.map(msg => `
                `).join('');
            renderMensajesPagination(data.pagination);
        } else {
            container.innerHTML = `<div class="p-8 text-center"><p class="text-gray-600 dark:text-gray-400">No hay mensajes</p></div>`;
        }
    } catch (error) {
        console.error('Error loading mensajes:', error);
    }
    
    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/mensajes?filter=${filter}&page=${page}&per_page=20`);
        const data = await response.json();
        const container = document.getElementById('mensajes-list');
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = data.items.map(msg => `
                <div class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer ${!msg.leido ? 'bg-blue-50 dark:bg-blue-900/20' : ''}" 
                     onclick="openMensajeDetail(${msg.id})">
                    <div class="flex items-start justify-between">
                        <div class="flex items-start flex-1">
                            <div class="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold mr-3 flex-shrink-0">
                                ${getInitials(msg.emisor_nombre)}
                            </div>
                            <div class="flex-1 min-w-0">
                                <div class="flex items-center mb-1">
                                    <h4 class="font-semibold text-gray-900 dark:text-white mr-2">${msg.emisor_nombre}</h4>
                                    ${msg.prioridad === 'URGENTE' ? '<span class="px-2 py-0.5 text-xs bg-red-100 text-red-800 rounded-full">Urgente</span>' : ''}
                                </div>
                                <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">${msg.asunto}</p>
                                <p class="text-sm text-gray-600 dark:text-gray-400 truncate">${msg.mensaje}</p>
                            </div>
                        </div>
                        <div class="ml-4 flex items-center space-x-3">
                            <span class="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">${formatDateTime(msg.fecha_envio)}</span>
                            ${!msg.leido ? '<div class="w-2 h-2 bg-blue-500 rounded-full"></div>' : ''}
                        </div>
                    </div>
                </div>
            `).join('');
            renderMensajesPagination(data.pagination);
        } else {
            container.innerHTML = `<div class="p-8 text-center"><p class="text-gray-600 dark:text-gray-400">No hay mensajes</p></div>`;
        }
    } catch (error) {
        console.error('Error loading mensajes:', error);
    }
}

function renderMensajesPagination(pagination) {
    const container = document.getElementById('mensajes-pagination');
    if (!pagination || pagination.total_pages <= 1) {
        container.innerHTML = '';
        return;
    }
    const { current_page, total_pages } = pagination;
    container.innerHTML = `
        <div class="flex items-center justify-between">
            <p class="text-sm text-gray-700 dark:text-gray-300">Página ${current_page} de ${total_pages}</p>
            <div class="flex space-x-2">
                <button onclick="loadMensajes('${currentFilter}', ${current_page - 1})" ${current_page === 1 ? 'disabled' : ''} class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"><i class="fas fa-chevron-left"></i></button>
                <button onclick="loadMensajes('${currentFilter}', ${current_page + 1})" ${current_page === total_pages ? 'disabled' : ''} class="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"><i class="fas fa-chevron-right"></i></button>
            </div>
        </div>
    `;
}

window.openMensajeDetail = async function(mensajeId) {
    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/mensajes/${mensajeId}`);
        const data = await response.json();
        
        await fetchAPI(`${API_BASE}/comunicaciones/mensajes/${mensajeId}/leer`, { method: 'PATCH' });
        
        Swal.fire({
            title: data.asunto,
            html: `
                <div class="text-left">
                    <div class="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            <strong>De:</strong> ${data.emisor_nombre}<br>
                            <strong>Fecha:</strong> ${formatDateTime(data.fecha_envio)}
                        </p>
                    </div>
                    <div class="text-gray-700 dark:text-gray-300">${data.mensaje.replace(/\n/g, '<br>')}</div>
                </div>
            `,
            width: '600px',
            confirmButtonText: 'Cerrar',
            confirmButtonColor: '#DD8E0A',
            showCancelButton: true,
            cancelButtonText: '<i class="fas fa-reply mr-2"></i>Responder',
            cancelButtonColor: '#6b7280',
            reverseButtons: true
        }).then((result) => {
            if (result.dismiss === Swal.DismissReason.cancel) openReplyModal(data);
        });
        loadMensajes(currentFilter, currentMensajesPage);
    } catch (error) {
        console.error('Error loading mensaje detail:', error);
        showToast('Error al cargar mensaje', 'error');
    }
}

function openReplyModal(originalMessage) {
    showToast('Funcionalidad de respuesta en desarrollo', 'info');
}

/* ============================================================
   COMUNICADOS (TAB)
   ============================================================ */
async function loadComunicados() {
    // 1. VALIDACIÓN DE SEGURIDAD (AGREGAR ESTO)
    const container = document.getElementById('mensajes-list');
    if (!container) return; // Si no existe el div, detenemos la función aquí.

    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/mensajes?filter=${filter}&page=${page}&per_page=20`);
        const data = await response.json();
        // const container = document.getElementById('mensajes-list'); // <-- BORRA O COMENTA ESTA LÍNEA ANTIGUA
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = data.items.map(msg => `
                `).join('');
            renderMensajesPagination(data.pagination);
        } else {
            container.innerHTML = `<div class="p-8 text-center"><p class="text-gray-600 dark:text-gray-400">No hay mensajes</p></div>`;
        }
    } catch (error) {
        console.error('Error loading mensajes:', error);
    }
    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/comunicados`);
        const data = await response.json();
        const container = document.getElementById('comunicados-list');
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = data.items.map(com => `
                <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-shadow">
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex items-center">
                            <div class="w-12 h-12 ${getTipoComunicadoColor(com.tipo)} rounded-lg flex items-center justify-center mr-3">
                                <i class="${getTipoComunicadoIcon(com.tipo)} text-2xl text-white"></i>
                            </div>
                            <div>
                                <span class="px-3 py-1 text-xs font-semibold rounded-full ${getTipoComunicadoBadge(com.tipo)}">${com.tipo}</span>
                            </div>
                        </div>
                        <span class="text-xs text-gray-500 dark:text-gray-400">${formatDate(com.fecha_publicacion)}</span>
                    </div>
                    <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">${com.titulo}</h3>
                    <p class="text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">${com.contenido}</p>
                    <div class="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                        <div class="text-sm text-gray-600 dark:text-gray-400"><i class="fas fa-user mr-1"></i>${com.autor_nombre}</div>
                        <button onclick="openComunicadoDetail(${com.id})" class="text-primary-600 hover:text-primary-700 dark:text-primary-500 text-sm font-medium">Leer más <i class="fas fa-arrow-right ml-1"></i></button>
                    </div>
                </div>
            `).join('');
        } else {
            container.innerHTML = `<div class="col-span-full p-8 text-center"><i class="fas fa-bullhorn text-6xl text-gray-300 mb-4"></i><p class="text-gray-600">No hay comunicados</p></div>`;
        }
    } catch (error) { console.error('Error loading comunicados:', error); }
}

window.openComunicadoDetail = async function(comunicadoId) {
    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/comunicados/${comunicadoId}`);
        const data = await response.json();
        Swal.fire({
            title: data.titulo,
            html: `
                <div class="text-left">
                    <div class="mb-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            <strong>Tipo:</strong> ${data.tipo}<br>
                            <strong>Publicado por:</strong> ${data.autor_nombre}<br>
                            <strong>Fecha:</strong> ${formatDateTime(data.fecha_publicacion)}
                        </p>
                    </div>
                    <div class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">${data.contenido}</div>
                </div>
            `,
            width: '700px',
            confirmButtonText: 'Cerrar',
            confirmButtonColor: '#DD8E0A'
        });
    } catch (error) { console.error('Error loading comunicado:', error); }
}

function getTipoComunicadoColor(tipo) {
    const colors = { 'INFORMATIVO': 'bg-blue-500', 'URGENTE': 'bg-red-500', 'ACTIVIDAD': 'bg-green-500', 'RECORDATORIO': 'bg-yellow-500' };
    return colors[tipo] || 'bg-gray-500';
}
function getTipoComunicadoIcon(tipo) {
    const icons = { 'INFORMATIVO': 'fas fa-info', 'URGENTE': 'fas fa-exclamation-triangle', 'ACTIVIDAD': 'fas fa-calendar-star', 'RECORDATORIO': 'fas fa-bell' };
    return icons[tipo] || 'fas fa-bullhorn';
}
function getTipoComunicadoBadge(tipo) {
    const badges = { 'INFORMATIVO': 'bg-blue-100 text-blue-800', 'URGENTE': 'bg-red-100 text-red-800', 'ACTIVIDAD': 'bg-green-100 text-green-800', 'RECORDATORIO': 'bg-yellow-100 text-yellow-800' };
    return badges[tipo] || 'bg-gray-100 text-gray-800';
}

/* ============================================================
   HISTORIAL (TAB)
   ============================================================ */
window.loadHistorial = async function() {
    const desde = document.getElementById('historial-fecha-desde').value;
    const hasta = document.getElementById('historial-fecha-hasta').value;
    const tipo = document.getElementById('historial-tipo').value;
    
    try {
        const params = new URLSearchParams();
        if (desde) params.append('fecha_desde', desde);
        if (hasta) params.append('fecha_hasta', hasta);
        if (tipo !== 'all') params.append('tipo', tipo);
        
        const response = await fetchAPI(`${API_BASE}/comunicaciones/historial?${params.toString()}`);
        const data = await response.json();
        const container = document.getElementById('historial-results');
        
        if (data.items && data.items.length > 0) {
            container.innerHTML = `<div class="divide-y divide-gray-200 dark:divide-gray-700">${data.items.map(item => `
                <div class="py-4">
                    <div class="flex items-start">
                        <div class="w-10 h-10 ${getHistorialIcon(item.tipo)} rounded-lg flex items-center justify-center mr-3 flex-shrink-0">
                            <i class="${getHistorialIconClass(item.tipo)} text-white"></i>
                        </div>
                        <div class="flex-1">
                            <div class="flex items-center justify-between mb-1">
                                <h4 class="font-semibold text-gray-900 dark:text-white">${item.titulo || item.asunto}</h4>
                                <span class="text-xs text-gray-500 dark:text-gray-400">${formatDateTime(item.fecha)}</span>
                            </div>
                            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">${item.descripcion || item.contenido}</p>
                            <div class="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                                <span><i class="fas fa-user mr-1"></i>${item.usuario_nombre}</span>
                                <span class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">${item.tipo}</span>
                            </div>
                        </div>
                    </div>
                </div>`).join('')}</div>`;
        } else {
            container.innerHTML = `<div class="text-center py-12"><p class="text-gray-600 dark:text-gray-400">No se encontraron resultados</p></div>`;
        }
    } catch (error) { console.error('Error loading historial:', error); }
}

function getHistorialIcon(tipo) { return { 'chat': 'bg-blue-500', 'mensaje': 'bg-green-500', 'comunicado': 'bg-purple-500' }[tipo] || 'bg-gray-500'; }
function getHistorialIconClass(tipo) { return { 'chat': 'fas fa-comments', 'mensaje': 'fas fa-envelope', 'comunicado': 'fas fa-bullhorn' }[tipo] || 'fas fa-circle'; }




/* ============================================================
   MODALES Y SELECCIÓN DE USUARIOS (LOGICA NUEVA)
   ============================================================ */

function initModals() {
    // Modal: Nuevo Mensaje
    const newMessageForm = document.getElementById('new-message-form');
    if(newMessageForm) newMessageForm.addEventListener('submit', handleNewMessage);
    
    // Modal: Nueva Notificación (NUEVO)
    const notifForm = document.getElementById('new-notificacion-form');
    if(notifForm) notifForm.addEventListener('submit', handleNewNotificacion);
}

window.openNewMessageModal = function() {
    document.getElementById('new-message-modal').classList.remove('hidden');
    // Actualizar llamada:
    renderRecipientsList(usersCache, 'recipients-list', 'recipient-checkbox'); 
    
    const search = document.getElementById('recipient-search');
    // Actualizar llamada:
    if(search) search.oninput = (e) => filterRecipients(e.target.value, 'recipients-list', 'recipient-checkbox');
}

window.closeNewMessageModal = function() {
    document.getElementById('new-message-modal').classList.add('hidden');
    document.getElementById('new-message-form').reset();
    // Limpiar selección visual
    const count = document.getElementById('selected-count');
    if (count) count.textContent = '0';
    const list = document.getElementById('recipients-list');
    if (list) list.innerHTML = '';
}

// --- MODAL NOTIFICACIÓN (NUEVO) ---
window.openNewNotificaacionModal = function() {
    document.getElementById('new-notificacion-modal').classList.remove('hidden');
    // Usamos la función genérica indicando los IDs específicos de este modal
    renderRecipientsList(usersCache, 'notif-recipients-list', 'notif-checkbox'); 
    
    // Configurar buscador local
    const search = document.getElementById('notif-recipient-search');
    if(search) search.oninput = (e) => filterRecipients(e.target.value, 'notif-recipients-list', 'notif-checkbox');
    
    // Configurar select all
    const btnAll = document.getElementById('btn-notif-select-all');
    if(btnAll) btnAll.onclick = () => toggleSelectAll('notif-checkbox', 'notif-selected-count', 'btn-notif-select-all');
}

window.closeNewNotificacionModal = function() {
    document.getElementById('new-notificacion-modal').classList.add('hidden');
    document.getElementById('new-notificacion-form').reset();
    document.getElementById('notif-selected-count').textContent = '0';
}
/* --- FUNCIÓN CLAVE: CARGAR USUARIOS EN EL DIV --- */
async function loadRecipients() {
    const listContainer = document.getElementById('recipients-list');
    if (!listContainer) return;

    listContainer.innerHTML = '<div class="text-center py-8 text-gray-400"><i class="fas fa-circle-notch fa-spin mr-2"></i>Cargando directorio...</div>';

    try {
        // Pedimos 1000 usuarios activos para tenerlos en cache
        const response = await fetchAPI(`${API_BASE}/usuarios?per_page=1000&activo=1`);
        
        if (!response.ok) throw new Error("Error al cargar usuarios");
        
        const data = await response.json();
        usersCache = data.items || [];
        
        renderRecipientsList(usersCache);
        
        // Activar el buscador
        const searchInput = document.getElementById('recipient-search');
        if(searchInput) {
            searchInput.oninput = (e) => filterRecipients(e.target.value);
        }

        // Activar botón "Seleccionar Todos"
        const btnSelectAll = document.getElementById('btn-select-all');
        if(btnSelectAll) {
            btnSelectAll.onclick = () => toggleSelectAll();
        }

    } catch (error) {
        console.error('Error cargando destinatarios:', error);
        listContainer.innerHTML = '<div class="text-center py-4 text-red-500 text-sm">Error al cargar usuarios</div>';
    }
}

function renderRecipientsList(users, containerId, checkboxClass) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (users.length === 0) {
        container.innerHTML = '<div class="text-center py-6 text-gray-400">No hay usuarios</div>';
        return;
    }

    container.innerHTML = users.map(user => {
        const initials = getInitials(user.nombre_completo || user.nombres);
        const fotoUrl = user.foto_perfil_url;

        // LÓGICA DE AVATAR (Igual que en la tabla de usuarios)
        let avatarHTML;
        
        // Verificamos si hay URL válida (evitamos "CP" o textos cortos)
        if (fotoUrl && fotoUrl.length > 4 && fotoUrl.includes('/')) {
            // CASO 1: Tiene Foto
            avatarHTML = `<img src="${fotoUrl}" 
                               alt="${user.username}" 
                               class="w-8 h-8 rounded-full object-cover mr-3 border border-gray-200 dark:border-gray-600">`;
        } else {
            // CASO 2: No tiene Foto -> Iniciales con fondo Naranja suave
            avatarHTML = `<div class="w-8 h-8 rounded-full bg-[#DD8E0A]/10 text-[#DD8E0A] flex items-center justify-center text-xs font-bold mr-3 border border-transparent">
                            ${initials}
                          </div>`;
        }

        return `
        <label class="recipient-item flex items-center p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer border-b dark:border-gray-700 transition-colors">
            <input type="checkbox" value="${user.id}" class="${checkboxClass} mr-3 text-[#DD8E0A] rounded focus:ring-[#DD8E0A]" 
                onchange="updateCount('${checkboxClass}', '${containerId === 'recipients-list' ? 'selected-count' : 'notif-selected-count'}')">
            
            ${avatarHTML}
            
            <div class="flex-1">
                <div class="flex justify-between items-center">
                    <span class="text-sm font-semibold dark:text-white truncate pr-2">${user.nombre_completo}</span>
                    <span class="text-[10px] bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600">${user.rol_nombre || 'Usuario'}</span>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400">@${user.username}</p>
            </div>
        </label>
        `;
    }).join('');
}

function filterRecipients(query, containerId, checkboxClass) {
    const lower = query.toLowerCase();
    const filtered = usersCache.filter(u => 
        (u.nombre_completo || "").toLowerCase().includes(lower) || 
        (u.rol_nombre || "").toLowerCase().includes(lower)
    );
    renderRecipientsList(filtered, containerId, checkboxClass);
}

// Función global para actualizar el contador UI
window.updateCount = function(checkboxClass, counterId) {
    const checked = document.querySelectorAll(`.${checkboxClass}:checked`).length;
    const el = document.getElementById(counterId);
    if(el) el.textContent = checked;
}

function toggleSelectAll(checkboxClass, counterId, btnId) {
    const cbs = document.querySelectorAll(`.${checkboxClass}`);
    const allChecked = Array.from(cbs).every(c => c.checked);
    cbs.forEach(c => c.checked = !allChecked);
    window.updateCount(checkboxClass, counterId);
}

/* --- FUNCIÓN CLAVE: ENVIAR MENSAJE --- */
async function handleNewMessage(e) {
    e.preventDefault();
    
    // CAMBIO IMPORTANTE: Leer los checkboxes, NO el select
    const recipients = Array.from(document.querySelectorAll('.recipient-checkbox:checked'))
                            .map(cb => parseInt(cb.value));
    
    const asunto = document.getElementById('message-subject').value.trim();
    const mensaje = document.getElementById('message-body').value.trim();
    const prioridad = document.getElementById('message-priority').value;
    
    if (recipients.length === 0) {
        showToast('Selecciona al menos un destinatario', 'warning');
        return;
    }
    
    try {
        const response = await fetchAPI(`${API_BASE}/comunicaciones/mensajes`, {
            method: 'POST',
            body: JSON.stringify({
                destinatarios: recipients,
                asunto,
                mensaje,
                prioridad
            })
        });
        
        if (response.ok) {
            showToast('Mensaje enviado exitosamente', 'success');
            closeNewMessageModal();
            loadMensajes();
        } else {
            const err = await response.json();
            throw new Error(err.detail || 'Error al enviar mensaje');
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        showToast(error.message, 'error');
    }
}

async function handleNewNotificacion(e) {
    e.preventDefault();
    // Obtener destinatarios del modal notificación usando la clase específica
    const recipients = Array.from(document.querySelectorAll('.notif-checkbox:checked')).map(c => parseInt(c.value));
    const titulo = document.getElementById('notif-titulo').value;
    const mensaje = document.getElementById('notif-mensaje').value;
    const tipo = document.getElementById('notif-tipo').value;
    const prioridad = document.getElementById('notif-prioridad').value;
    
    if (recipients.length === 0) return showToast('Selecciona destinatarios', 'warning');
    
    try {
        const res = await fetchAPI(`${API_BASE}/notificaciones/enviar`, {
            method: 'POST', 
            body: JSON.stringify({ destinatarios: recipients, titulo, mensaje, tipo, prioridad })
        });
        
        if (res.ok) {
            showToast('Notificación enviada', 'success');
            closeNewNotificacionModal();
        } else {
            showToast('Error al enviar', 'error');
        }
    } catch(err) { console.error(err); }
}
/* ============================================================
   FILTROS Y BÚSQUEDA
   ============================================================ */
function initSearchFilters() {
    const searchConversations = document.getElementById('search-conversations');
    if(searchConversations) {
        searchConversations.addEventListener('input', debounce((e) => { filterConversations(e.target.value); }, 300));
    }
    
    const searchMensajes = document.getElementById('search-mensajes');
    if(searchMensajes) {
        searchMensajes.addEventListener('input', debounce((e) => { console.log('Searching:', e.target.value); }, 300));
    }
    
    document.querySelectorAll('.mensaje-filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.mensaje-filter-btn').forEach(b => {
                b.classList.remove('active', 'bg-primary-100', 'dark:bg-primary-900', 'text-primary-700', 'dark:text-primary-300');
            });
            e.target.classList.add('active', 'bg-primary-100', 'dark:bg-primary-900', 'text-primary-700', 'dark:text-primary-300');
            loadMensajes(e.target.dataset.filter);
        });
    });
}

function filterConversations(query) {
    document.querySelectorAll('.conversation-item').forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query.toLowerCase()) ? '' : 'none';
    });
}

/* ============================================================
   HELPERS
   ============================================================ */
function getInitials(name) {
    if (!name) return '??';
    const parts = name.split(' ');
    if (parts.length >= 2) return parts[0][0] + parts[1][0];
    return name.substring(0, 2).toUpperCase();
}

function escapeHtml(text) {
    if (!text) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return text.replace(/[&<>"']/g, m => map[m]);
}

function formatTime(dateString) {
    if(!dateString) return '';
    const date = new Date(dateString);
    const diffMins = Math.floor((new Date() - date) / 60000);
    if (diffMins < 1) return 'Ahora';
    if (diffMins < 60) return `${diffMins}m`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d`;
    return date.toLocaleDateString('es-BO', { day: '2-digit', month: 'short' });
}

function formatDate(dateString) {
    if(!dateString) return '';
    return new Date(dateString).toLocaleDateString('es-BO', { day: '2-digit', month: 'long', year: 'numeric' });
}

function formatDateTime(dateString) {
    if(!dateString) return '';
    return new Date(dateString).toLocaleString('es-BO', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

function updateConversationBadge(conversationId) {
    const item = document.querySelector(`.conversation-item[data-conversation-id="${conversationId}"]`);
    if (item) {
        const list = document.getElementById('conversations-list');
        if (list && list.firstChild !== item) {
            item.style.transition = 'background-color 0.3s';
            item.classList.add('bg-gray-50', 'dark:bg-gray-700');
            setTimeout(() => item.classList.remove('bg-gray-50', 'dark:bg-gray-700'), 1000);
            list.prepend(item);
        }
        const textContainer = item.querySelector('.flex-1');
        if (textContainer) {
            let badge = textContainer.querySelector('.bg-red-500.rounded-full');
            if (badge) badge.textContent = (parseInt(badge.textContent) || 0) + 1;
            else {
                badge = document.createElement('span');
                badge.className = 'inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full mt-1';
                badge.textContent = '1';
                textContainer.appendChild(badge);
            }
            const timeLabel = item.querySelector('.flex.items-center.justify-between > span');
            if (timeLabel) timeLabel.textContent = 'Ahora';
        }
    }
}