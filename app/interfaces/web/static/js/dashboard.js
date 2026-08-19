import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';
let inscripcionesChart = null;
let ingresosChart = null;

async function loadDashboardData() {
    const dashboard = document.getElementById('dashboard-content');
    const periodSelector = document.getElementById('period-selector');
    const period = periodSelector?.value || 'month';

    try {
        dashboard?.setAttribute('aria-busy', 'true');
        periodSelector?.setAttribute('disabled', 'disabled');

        // Una llamada evita repetir autenticación y consultas por tarjeta/gráfico.
        const response = await fetchAPI(`${API_BASE}/reportes/dashboard/resumen?period=${period}`);
        if (!response.ok) throw new Error(`No se pudo cargar el panel (${response.status})`);
        const data = await response.json();

        renderMetrics(data.metricas);
        renderInscripcionesChart(data.inscripciones);
        renderIngresosChart(data.ingresos);

        const actualizado = document.getElementById('dashboard-updated-at');
        if (actualizado) actualizado.textContent = `Actualizado ${formatDateTime(data.actualizado_en)}`;
    } catch (error) {
        console.error('Error al cargar el dashboard:', error);
        showToast('No se pudieron cargar los datos del dashboard', 'error');
    } finally {
        dashboard?.setAttribute('aria-busy', 'false');
        periodSelector?.removeAttribute('disabled');
    }
}

function renderMetrics(data) {
    setText('total-inscritos', data.total_inscritos || 0);
    setText('ingresos-mes', formatCurrency(data.ingresos_total || 0));
    setText('ingresos-change', 'Registrados en el periodo');
    setText('pagos-pendientes', data.pagos_pendientes_cantidad || 0);
    setText('monto-pendiente', formatCurrency(data.pagos_pendientes_monto || 0));
    setText('nuevos-mes', data.nuevos_total || 0);

    const changeEl = document.getElementById('inscritos-change');
    if (changeEl) {
        const nuevos = data.nuevos_total || 0;
        changeEl.textContent = `${nuevos} ${nuevos === 1 ? 'registro reciente' : 'registros recientes'}`;
        changeEl.className = 'text-green-600 dark:text-green-400 font-bold';
    }
}

function renderInscripcionesChart(data) {
    const canvas = document.getElementById('inscripciones-chart');
    if (!canvas || typeof Chart === 'undefined') return;
    Chart.getChart(canvas)?.destroy();
    inscripcionesChart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Inscripciones',
                data: data.valores,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.12)',
                borderWidth: 3,
                tension: 0.35,
                fill: true,
                pointRadius: 4,
                pointBackgroundColor: '#f59e0b',
            }],
        },
        options: chartOptions(),
    });
}

function renderIngresosChart(data) {
    const canvas = document.getElementById('ingresos-chart');
    if (!canvas || typeof Chart === 'undefined') return;
    Chart.getChart(canvas)?.destroy();
    ingresosChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Ingresos',
                data: data.valores,
                backgroundColor: '#10b981',
                borderRadius: 6,
                barPercentage: 0.62,
            }],
        },
        options: chartOptions(true),
    });
}

function chartOptions(currency = false) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: currency ? {
                callbacks: { label: (context) => `Ingresos: ${formatCurrency(context.parsed.y)}` },
            } : {},
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: 'rgba(156, 163, 175, 0.12)' },
                ticks: currency ? {
                    callback: (value) => value >= 1000 ? `Bs ${value / 1000}k` : `Bs ${value}`,
                } : { precision: 0 },
            },
            x: { grid: { display: false }, ticks: { color: '#9ca3af' } },
        },
    };
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = String(value);
}

function formatCurrency(value) {
    return `Bs ${Number(value).toLocaleString('es-BO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    })}`;
}

function formatDateTime(value) {
    return new Intl.DateTimeFormat('es-BO', {
        hour: '2-digit',
        minute: '2-digit',
    }).format(new Date(value));
}

document.getElementById('period-selector')?.addEventListener('change', loadDashboardData);
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    window.setInterval(loadDashboardData, 300000);
});
