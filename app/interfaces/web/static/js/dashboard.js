import { fetchAPI, showToast } from './main.js';

const API_BASE = '/api/v1';

/* ============================================================
   VARIABLES GLOBALES
   ============================================================ */
let inscripcionesChart = null;
let ingresosChart = null;

/* ============================================================
   CARGAR DATOS DEL DASHBOARD
   ============================================================ */
async function loadDashboardData() {
    try {
        // 1. Obtener el periodo seleccionado
        const periodSelector = document.getElementById('period-selector');
        const period = periodSelector ? periodSelector.value : 'month';

        console.log("Cargando dashboard para periodo:", period);

        // 2. Cargar métricas pasando el periodo como Query Param
        await Promise.all([
            loadMetrics(period),
            loadInscripcionesChart(period),
            loadIngresosChart(period)
            // loadRecentCodes() <--- ELIMINADO
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Error al cargar datos del dashboard', 'error');
    }
}

/* ============================================================
   MÉTRICAS (Cards)
   ============================================================ */
async function loadMetrics(period) {
    try {
        // Pasamos ?period=...
        const response = await fetchAPI(`${API_BASE}/reportes/dashboard/metricas?period=${period}`);
        const data = await response.json();

        // Total Inscritos
        document.getElementById('total-inscritos').textContent = data.total_inscritos || 0;
        
        // Cambio porcentual (visual)
        const changeEl = document.getElementById('inscritos-change');
        const changeVal = data.inscritos_cambio_porcentaje || 0;
        changeEl.textContent = `${changeVal > 0 ? '+' : ''}${changeVal}%`;
        changeEl.className = changeVal >= 0 ? "text-green-600 dark:text-green-400 font-bold" : "text-red-600 dark:text-red-400 font-bold";

        // Ingresos Mes/Periodo
        document.getElementById('ingresos-mes').textContent = formatCurrency(data.ingresos_total || 0);
        document.getElementById('ingresos-change').textContent = "En este periodo"; 

        // Pagos Pendientes (Mora)
        document.getElementById('pagos-pendientes').textContent = data.pagos_pendientes_cantidad || 0;
        document.getElementById('monto-pendiente').textContent = formatCurrency(data.pagos_pendientes_monto || 0);

        // Nuevos
        document.getElementById('nuevos-mes').textContent = data.nuevos_total || 0;
    } catch (error) {
        console.error('Error loading metrics:', error);
    }
}

/* ============================================================
   GRÁFICO: CRECIMIENTO DE INSCRIPCIONES
   ============================================================ */
async function loadInscripcionesChart(period) {
    try {
        const response = await fetchAPI(`${API_BASE}/reportes/dashboard/crecimiento-inscripciones?period=${period}`);
        const data = await response.json();

        const canvas = document.getElementById('inscripciones-chart');
        if (!canvas) return; 

        const existingChart = Chart.getChart(canvas);
        if (existingChart) existingChart.destroy();

        inscripcionesChart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: data.labels, // Ahora vendrán dinámicos desde el backend
                datasets: [{
                    label: 'Inscripciones',
                    data: data.valores,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#f59e0b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, 
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(156, 163, 175, 0.1)' } },
                    x: { grid: { display: false }, ticks: { color: '#9ca3af' } }
                }
            }
        });
    } catch (error) {
        console.error('Error loading inscripciones chart:', error);
    }
}

/* ============================================================
   GRÁFICO: FLUJO DE INGRESOS
   ============================================================ */
async function loadIngresosChart(period) {
    try {
        const response = await fetchAPI(`${API_BASE}/reportes/dashboard/flujo-ingresos?period=${period}`);
        const data = await response.json();

        const canvas = document.getElementById('ingresos-chart');
        if (!canvas) return;

        const existingChart = Chart.getChart(canvas);
        if (existingChart) existingChart.destroy();

        ingresosChart = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels, // Ahora son fechas legibles (ej: "28 Dic")
                datasets: [{
                    label: 'Ingresos',
                    data: data.valores,
                    backgroundColor: '#10b981',
                    borderRadius: 4,
                    barPercentage: 0.6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => 'Ingresos: ' + formatCurrency(context.parsed.y)
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(156, 163, 175, 0.1)' },
                        ticks: {
                            callback: (value) => value >= 1000 ? 'Bs ' + (value/1000) + 'k' : 'Bs ' + value
                        }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    } catch (error) {
        console.error('Error loading ingresos chart:', error);
    }
}

/* ============================================================
   EVENTOS
   ============================================================ */
const periodSelector = document.getElementById('period-selector');
if (periodSelector) {
    periodSelector.addEventListener('change', () => loadDashboardData());
}

function formatCurrency(value) {
    return `Bs ${value.toLocaleString('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    setInterval(() => loadDashboardData(), 300000); // 5 min
});