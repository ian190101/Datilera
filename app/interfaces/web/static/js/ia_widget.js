/* ============================================================
   🤖 LOGICA DEL WIDGET DE IA (DATILERA COPILOT)
   ============================================================ */

const aiConfig = {
    isOpen: false,
    apiEndpoint: '/api/v1/ia/chat'
};

// Toggle Abrir/Cerrar
function toggleAIChat() {
    const windowEl = document.getElementById('ai-chat-window');
    aiConfig.isOpen = !aiConfig.isOpen;

    if (aiConfig.isOpen) {
        windowEl.classList.remove('translate-y-10', 'opacity-0', 'pointer-events-none');
        setTimeout(() => document.getElementById('ai-input').focus(), 100);
    } else {
        windowEl.classList.add('translate-y-10', 'opacity-0', 'pointer-events-none');
    }
}

// Manejo del Formulario
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('ai-chat-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleAISubmit();
        });
    }
});

async function handleAISubmit() {
    const input = document.getElementById('ai-input');
    const message = input.value.trim();
    if (!message) return;

    // 1. Limpiar input y mostrar mensaje usuario
    input.value = '';
    appendAIMessage(message, 'user');
    
    // 2. Mostrar loading
    showAILoading(true);
    
    try {
        // 3. Llamada al Backend
        const response = await fetch(aiConfig.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Si usas tokens en headers, agrégalo aquí. 
                // Si usas cookies (como en tu routes.py), no hace falta nada extra.
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        if (response.ok) {
            appendAIMessage(data.reply, 'ai');
        } else {
            appendAIMessage("Lo siento, tuve un problema procesando tu solicitud.", 'ai', true);
            console.error("IA Error:", data);
        }

    } catch (error) {
        console.error("Network Error:", error);
        appendAIMessage("Error de conexión. Intenta nuevamente.", 'ai', true);
    } finally {
        showAILoading(false);
        scrollToBottomAI();
    }
}

// Renderizar Mensaje
function appendAIMessage(text, sender, isError = false) {
    const container = document.getElementById('ai-messages-container');
    const div = document.createElement('div');
    const isUser = sender === 'user';

    div.className = `flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in-up`;
    
    // Formato simple de Markdown (Negritas y Saltos de linea)
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Negritas
        .replace(/\n/g, '<br>'); // Saltos de línea

    const bubbleClass = isUser 
        ? 'bg-indigo-600 text-white rounded-br-none' 
        : (isError ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-tl-none');

    div.innerHTML = `
        <div class="px-4 py-2 rounded-2xl shadow-sm max-w-[85%] text-sm ${bubbleClass}">
            ${formattedText}
        </div>
    `;

    container.appendChild(div);
    scrollToBottomAI();
}

function showAILoading(show) {
    const loader = document.getElementById('ai-typing-indicator');
    const btn = document.querySelector('#ai-chat-form button');
    
    if (show) {
        loader.classList.remove('hidden');
        btn.disabled = true;
    } else {
        loader.classList.add('hidden');
        btn.disabled = false;
        setTimeout(() => document.getElementById('ai-input').focus(), 100);
    }
    scrollToBottomAI();
}

function scrollToBottomAI() {
    const container = document.getElementById('ai-messages-container');
    container.scrollTop = container.scrollHeight;
}