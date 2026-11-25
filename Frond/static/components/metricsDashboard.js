/**
 * Metrics Dashboard Component
 * Panel de métricas con gráficos interactivos
 */

class MetricsDashboardComponent {
    constructor() {
        this.metricsContainer = null;
        this.charts = {};
        this.metricsData = null;
        this.init();
    }

    init() {
        this.metricsContainer = document.getElementById('metrics-container');
        this.loadMetrics();
        this.initCharts();
    }

    async loadMetrics() {
        try {
            const response = await fetch(`${window.API_BASE_URL}/metrics`);
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            this.metricsData = await response.json();
            this.updateMetricsDisplay();
            
        } catch (error) {
            console.error('Error cargando métricas:', error);
            this.showErrorState();
        }
    }

    updateMetricsDisplay() {
        if (!this.metricsData) return;

        // Actualizar valores principales
        this.updateMetricValue('accuracy-value', `${(this.metricsData.precision * 100).toFixed(1)}%`);
        this.updateMetricValue('satisfaction-value', `${this.metricsData.satisfaccion.toFixed(1)}/5`);
        this.updateMetricValue('improvement-value', `${(this.metricsData.tasa_mejora * 100).toFixed(1)}%`);

        // Actualizar gráficos
        this.updateCharts();
    }

    updateMetricValue(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
        }
    }

    initCharts() {
        // Esperar a que Chart.js esté disponible
        if (typeof Chart === 'undefined') {
            setTimeout(() => this.initCharts(), 100);
            return;
        }

        this.createAccuracyChart();
        this.createSatisfactionChart();
        this.createImprovementChart();
    }

    createAccuracyChart() {
        const ctx = document.getElementById('accuracy-chart');
        if (!ctx) return;

        this.charts.accuracy = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4', 'Semana 5'],
                datasets: [{
                    label: 'Precisión',
                    data: this.metricsData?.tendencias?.precision || [85, 87, 89, 91, 92],
                    borderColor: '#4ecdc4',
                    backgroundColor: 'rgba(78, 205, 196, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    createSatisfactionChart() {
        const ctx = document.getElementById('satisfaction-chart');
        if (!ctx) return;

        this.charts.satisfaction = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May'],
                datasets: [{
                    label: 'Satisfacción',
                    data: this.metricsData?.tendencias?.satisfaccion || [4.0, 4.1, 4.2, 4.2, 4.3],
                    backgroundColor: '#4ecdc4',
                    borderColor: '#45b7aa',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 5,
                        ticks: {
                            callback: function(value) {
                                return value + '/5';
                            }
                        }
                    }
                }
            }
        });
    }

    createImprovementChart() {
        const ctx = document.getElementById('improvement-chart');
        if (!ctx) return;

        this.charts.improvement = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Mejorado', 'Sin cambios', 'Empeorado'],
                datasets: [{
                    data: [65, 30, 5],
                    backgroundColor: ['#27ae60', '#f39c12', '#e74c3c'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 10,
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }

    updateCharts() {
        if (!this.metricsData) return;

        // Actualizar gráfico de precisión
        if (this.charts.accuracy && this.metricsData.tendencias?.precision) {
            this.charts.accuracy.data.datasets[0].data = this.metricsData.tendencias.precision;
            this.charts.accuracy.update();
        }

        // Actualizar gráfico de satisfacción
        if (this.charts.satisfaction && this.metricsData.tendencias?.satisfaccion) {
            this.charts.satisfaction.data.datasets[0].data = this.metricsData.tendencias.satisfaccion;
            this.charts.satisfaction.update();
        }
    }

    showErrorState() {
        // Mostrar estado de error en los valores
        this.updateMetricValue('accuracy-value', 'Error');
        this.updateMetricValue('satisfaction-value', 'Error');
        this.updateMetricValue('improvement-value', 'Error');
    }

    // Método para refrescar métricas
    async refreshMetrics() {
        await this.loadMetrics();
    }

    // Método para exportar métricas
    exportMetrics() {
        if (!this.metricsData) return;

        const dataStr = JSON.stringify(this.metricsData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `alimentor-metrics-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
    }

    // Método para mostrar métricas detalladas
    showDetailedMetrics() {
        if (!this.metricsData) return;

        const modal = document.createElement('div');
        modal.className = 'metrics-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Métricas Detalladas</h3>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="detailed-metrics">
                        <div class="metric-group">
                            <h4>Rendimiento del Sistema</h4>
                            <p><strong>Análisis Totales:</strong> ${this.metricsData.total_analisis || 0}</p>
                            <p><strong>Feedback Total:</strong> ${this.metricsData.total_feedback || 0}</p>
                            <p><strong>Tiempo de Respuesta:</strong> ${this.metricsData.tiempo_respuesta || 0}s</p>
                        </div>
                        <div class="metric-group">
                            <h4>Estadísticas Mensuales</h4>
                            <p><strong>Análisis este mes:</strong> ${this.metricsData.analisis_mes || 0}</p>
                            <p><strong>Feedback este mes:</strong> ${this.metricsData.feedback_mes || 0}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Event listeners para el modal
        modal.querySelector('.close-btn').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }

    // Método para obtener datos de métricas
    getMetricsData() {
        return this.metricsData;
    }
}

// Exportar para uso global
window.MetricsDashboardComponent = MetricsDashboardComponent;

