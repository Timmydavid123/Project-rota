// app/static/js/dashboard.js
// Dashboard specific JavaScript

class DashboardManager {
    constructor() {
        this.charts = {};
        this.init();
    }
    
    init() {
        this.loadStats();
        this.loadCoverageChart();
        this.loadUtilizationChart();
        this.loadRecentActivity();
        this.setupAutoRefresh();
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            document.getElementById('total-staff').textContent = data.total_staff;
            document.getElementById('total-services').textContent = data.total_services;
            document.getElementById('active-shifts').textContent = data.active_shifts;
            
            const aiStatus = document.getElementById('ai-status');
            if (data.ai_enabled) {
                aiStatus.innerHTML = '<span class="badge bg-success">Active</span>';
            } else {
                aiStatus.innerHTML = '<span class="badge bg-warning">Not Trained</span>';
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }
    
    async loadCoverageChart() {
        try {
            const response = await fetch('/api/analytics/coverage');
            const data = await response.json();
            
            const ctx = document.getElementById('coverageChart').getContext('2d');
            
            if (this.charts.coverage) {
                this.charts.coverage.destroy();
            }
            
            this.charts.coverage = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(d => d.service_user),
                    datasets: [{
                        label: 'Coverage %',
                        data: data.map(d => d.coverage_percentage),
                        backgroundColor: data.map(d => 
                            d.coverage_percentage >= 90 ? '#1cc88a' : 
                            d.coverage_percentage >= 70 ? '#f6c23e' : '#e74a3b'
                        ),
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: '#eaecf4'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Failed to load coverage chart:', error);
        }
    }
    
    async loadUtilizationChart() {
        try {
            const response = await fetch('/api/analytics/utilization');
            const data = await response.json();
            
            const ctx = document.getElementById('utilizationChart').getContext('2d');
            
            if (this.charts.utilization) {
                this.charts.utilization.destroy();
            }
            
            this.charts.utilization = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Over-utilized', 'Well-utilized', 'Under-utilized', 'Idle'],
                    datasets: [{
                        data: [
                            data.filter(d => d.status === 'Over-utilized').length,
                            data.filter(d => d.status === 'Well-utilized').length,
                            data.filter(d => d.status === 'Under-utilized').length,
                            data.filter(d => d.status === 'Idle').length
                        ],
                        backgroundColor: ['#e74a3b', '#1cc88a', '#f6c23e', '#858796'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    cutout: '60%'
                }
            });
        } catch (error) {
            console.error('Failed to load utilization chart:', error);
        }
    }
    
    async loadRecentActivity() {
        try {
            const response = await fetch('/api/schedule?limit=10');
            const data = await response.json();
            
            const container = document.getElementById('recent-activity');
            
            if (data.length === 0) {
                container.innerHTML = '<p class="text-muted text-center">No recent activity</p>';
                return;
            }
            
            container.innerHTML = data.map(shift => `
                <div class="activity-item p-2 border-bottom">
                    <div class="d-flex justify-content-between">
                        <strong>${shift.service_user}</strong>
                        <small class="text-muted">${shift.date}</small>
                    </div>
                    <div class="d-flex justify-content-between">
                        <span>${shift.staff_assigned}</span>
                        <span class="badge bg-info">${shift.hours}h</span>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Failed to load recent activity:', error);
        }
    }
    
    setupAutoRefresh() {
        // Auto refresh every 5 minutes
        setInterval(() => {
            this.loadStats();
            this.loadRecentActivity();
        }, 300000);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new DashboardManager();
});