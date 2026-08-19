/* Datilera Copilot: respuestas verificables, gráficas y acciones controladas. */
const aiConfig = {
    isOpen: false,
    isLoading: false,
    apiEndpoint: '/api/v1/ia/chat',
    actionEndpoint: '/api/v1/ia/acciones/confirmar',
    history: [],
    charts: []
};

function toggleAIChat() {
    const windowEl = document.getElementById('ai-chat-window');
    if (!windowEl) return;
    aiConfig.isOpen = !aiConfig.isOpen;
    windowEl.classList.toggle('translate-y-10', !aiConfig.isOpen);
    windowEl.classList.toggle('opacity-0', !aiConfig.isOpen);
    windowEl.classList.toggle('pointer-events-none', !aiConfig.isOpen);
    if (aiConfig.isOpen) setTimeout(() => document.getElementById('ai-input')?.focus(), 100);
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('ai-chat-form')?.addEventListener('submit', async (event) => {
        event.preventDefault();
        await handleAISubmit();
    });
});

async function handleAISubmit(forcedMessage = '') {
    if (aiConfig.isLoading) return;
    const input = document.getElementById('ai-input');
    const message = (forcedMessage || input?.value || '').trim();
    if (!message) return;
    if (input) input.value = '';
    appendAIMessage(message, 'user');
    const historyForRequest = aiConfig.history.slice(-8);
    aiConfig.history.push({ role: 'user', content: message });
    showAILoading(true);

    try {
        const response = await fetch(aiConfig.apiEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, history: historyForRequest })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'No se pudo procesar la consulta');
        appendAIMessage(data.reply, 'ai', false, data);
        aiConfig.history.push({ role: 'assistant', content: data.reply });
        aiConfig.history = aiConfig.history.slice(-10);
    } catch (error) {
        console.error('Error de Datilera Copilot:', error);
        appendAIMessage(error.message || 'Error de conexión. Intenta nuevamente.', 'ai', true);
    } finally {
        showAILoading(false);
    }
}

function escapeHTML(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (character) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    })[character]);
}

function formatSafeText(text) {
    return escapeHTML(text)
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

function appendAIMessage(text, sender, isError = false, metadata = {}) {
    const container = document.getElementById('ai-messages-container');
    if (!container) return;
    const wrapper = document.createElement('div');
    const isUser = sender === 'user';
    wrapper.className = `flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in-up`;
    const bubble = document.createElement('div');
    bubble.className = `px-4 py-3 rounded-2xl shadow-sm text-sm ${isUser
        ? 'max-w-[88%] bg-indigo-600 text-white rounded-br-none'
        : isError
            ? 'max-w-[94%] bg-red-100 text-red-700 border border-red-200'
            : 'w-full max-w-[96%] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 rounded-tl-none'}`;
    bubble.innerHTML = formatSafeText(text);

    if (!isUser && Array.isArray(metadata.visualizations)) {
        metadata.visualizations.slice(0, 3).forEach((visualization) => {
            bubble.appendChild(createVisualization(visualization));
        });
    }
    if (!isUser && Array.isArray(metadata.sources) && metadata.sources.length) {
        const source = document.createElement('div');
        source.className = 'mt-3 pt-2 border-t border-gray-200 dark:border-gray-700 text-[10px] text-gray-500';
        source.textContent = `Fuentes: ${metadata.sources.map((item) => item.label).join(', ')}`;
        bubble.appendChild(source);
    }
    if (!isUser && Array.isArray(metadata.actions) && metadata.actions.length) {
        const actions = document.createElement('div');
        actions.className = 'mt-3 flex flex-wrap gap-2';
        metadata.actions.forEach((action) => actions.appendChild(createActionButton(action)));
        bubble.appendChild(actions);
    }
    if (!isUser && Array.isArray(metadata.suggestions) && metadata.suggestions.length) {
        bubble.appendChild(createSuggestions(metadata.suggestions));
    }
    wrapper.appendChild(bubble);
    container.appendChild(wrapper);
    scrollToBottomAI();
}

function safeChartPayload(visualization) {
    const allowedTypes = new Set(['line', 'bar', 'doughnut', 'pie']);
    if (!visualization || !allowedTypes.has(visualization.type)) return null;
    const labels = Array.isArray(visualization.labels)
        ? visualization.labels.slice(0, 36).map((item) => String(item).slice(0, 40))
        : [];
    const datasets = Array.isArray(visualization.datasets)
        ? visualization.datasets.slice(0, 4).map((dataset) => ({
            label: String(dataset.label || 'Valor').slice(0, 50),
            data: Array.isArray(dataset.data)
                ? dataset.data.slice(0, labels.length).map((value) => Number.isFinite(Number(value)) ? Number(value) : 0)
                : [],
            borderColor: dataset.borderColor,
            backgroundColor: dataset.backgroundColor,
            fill: Boolean(dataset.fill),
            tension: visualization.type === 'line' ? 0.25 : undefined
        }))
        : [];
    if (!labels.length || !datasets.length) return null;
    return { type: visualization.type, title: String(visualization.title || 'Visualización').slice(0, 80), labels, datasets };
}

function createVisualization(visualization) {
    const payload = safeChartPayload(visualization);
    const card = document.createElement('section');
    card.className = 'mt-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 p-3';
    if (!payload) {
        card.textContent = 'La visualización recibida no tiene un formato válido.';
        return card;
    }
    const title = document.createElement('h4');
    title.className = 'font-semibold text-xs text-gray-700 dark:text-gray-200 mb-2';
    title.textContent = payload.title;
    card.appendChild(title);

    if (typeof window.Chart !== 'function') {
        card.appendChild(createChartFallback(payload));
        return card;
    }
    const chartArea = document.createElement('div');
    chartArea.className = 'relative w-full h-56';
    const canvas = document.createElement('canvas');
    canvas.setAttribute('role', 'img');
    canvas.setAttribute('aria-label', payload.title);
    chartArea.appendChild(canvas);
    card.appendChild(chartArea);
    requestAnimationFrame(() => {
        const chart = new window.Chart(canvas, {
            type: payload.type,
            data: { labels: payload.labels, datasets: payload.datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 350 },
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.dataset.label || 'Monto'}: Bs ${Number(context.raw || 0).toLocaleString('es-BO', { minimumFractionDigits: 2 })}`
                        }
                    }
                },
                scales: ['line', 'bar'].includes(payload.type) ? {
                    y: { beginAtZero: true, ticks: { callback: (value) => `Bs ${Number(value).toLocaleString('es-BO')}` } },
                    x: { ticks: { maxRotation: 45, minRotation: 0 } }
                } : undefined
            }
        });
        aiConfig.charts.push(chart);
    });
    return card;
}

function createChartFallback(payload) {
    const table = document.createElement('table');
    table.className = 'w-full text-[10px] text-left';
    const head = document.createElement('thead');
    head.innerHTML = `<tr><th class="py-1">Período</th>${payload.datasets.map((dataset) => `<th class="py-1">${escapeHTML(dataset.label)}</th>`).join('')}</tr>`;
    table.appendChild(head);
    const body = document.createElement('tbody');
    payload.labels.forEach((label, index) => {
        const row = document.createElement('tr');
        row.className = 'border-t border-gray-200 dark:border-gray-700';
        row.innerHTML = `<td class="py-1">${escapeHTML(label)}</td>${payload.datasets.map((dataset) => `<td>Bs ${Number(dataset.data[index] || 0).toLocaleString('es-BO', { minimumFractionDigits: 2 })}</td>`).join('')}`;
        body.appendChild(row);
    });
    table.appendChild(body);
    return table;
}

function createSuggestions(suggestions) {
    const container = document.createElement('div');
    container.className = 'mt-3 flex gap-2 overflow-x-auto pb-1';
    suggestions.slice(0, 4).forEach((suggestion) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'shrink-0 px-2.5 py-1.5 rounded-full border border-indigo-200 dark:border-indigo-700 text-indigo-700 dark:text-indigo-300 text-[10px] hover:bg-indigo-50 dark:hover:bg-indigo-900/30';
        button.textContent = String(suggestion).slice(0, 90);
        button.addEventListener('click', () => handleAISubmit(button.textContent));
        container.appendChild(button);
    });
    return container;
}

function createActionButton(action) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium disabled:opacity-50';
    button.textContent = action.label || 'Continuar';
    if (action.type === 'navigate' || action.type === 'download') {
        button.addEventListener('click', () => {
            if (typeof action.url === 'string' && action.url.startsWith('/')) window.location.assign(action.url);
        });
    } else if (action.type === 'confirm_reminder') {
        button.addEventListener('click', async () => {
            button.disabled = true;
            try {
                const response = await fetch(aiConfig.actionEndpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ token: action.token })
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.detail || 'No se pudo confirmar');
                appendAIMessage(data.reply, 'ai', false, data);
                button.textContent = 'Confirmado';
            } catch (error) {
                appendAIMessage(error.message || 'No se pudo confirmar la acción.', 'ai', true);
                button.disabled = false;
            }
        });
    } else {
        button.disabled = true;
    }
    return button;
}

function showAILoading(show) {
    aiConfig.isLoading = show;
    document.getElementById('ai-typing-indicator')?.classList.toggle('hidden', !show);
    const button = document.querySelector('#ai-chat-form button');
    const input = document.getElementById('ai-input');
    if (button) button.disabled = show;
    if (input) input.disabled = show;
    if (!show) setTimeout(() => input?.focus(), 100);
    scrollToBottomAI();
}

function scrollToBottomAI() {
    const container = document.getElementById('ai-messages-container');
    if (container) container.scrollTop = container.scrollHeight;
}
