// app/static/js/schedule.js
// Schedule management JavaScript

class ScheduleManager {
    constructor() {
        this.currentDate = new Date();
        this.schedule = [];
        this.init();
    }
    
    init() {
        this.loadSchedule();
        this.setupEventListeners();
    }
    
    async loadSchedule(date = null) {
        const dateStr = date || this.formatDate(this.currentDate);
        
        try {
            showLoading('Loading schedule...');
            const response = await fetch(`/api/schedule?date=${dateStr}`);
            this.schedule = await response.json();
            this.renderSchedule();
            hideLoading();
        } catch (error) {
            console.error('Failed to load schedule:', error);
            hideLoading();
            showToast('Failed to load schedule', 'danger');
        }
    }
    
    renderSchedule() {
        const container = document.getElementById('schedule-container');
        
        if (this.schedule.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i>
                    No shifts scheduled for this date.
                    <a href="/schedule/generate">Generate a schedule</a>
                </div>
            `;
            return;
        }
        
        // Group by time
        const grouped = this.groupByTime(this.schedule);
        
        container.innerHTML = Object.entries(grouped).map(([time, shifts]) => `
            <div class="time-slot mb-4">
                <h6 class="time-slot-header">${time}</h6>
                <div class="row">
                    ${shifts.map(shift => this.renderShiftCard(shift)).join('')}
                </div>
            </div>
        `).join('');
    }
    
    renderShiftCard(shift) {
        const color = this.getShiftColor(shift.support_ratio);
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="card shift-card" style="border-left: 4px solid ${color}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <h6 class="card-title">${shift.service_user}</h6>
                            <span class="badge" style="background-color: ${color}">
                                ${shift.support_ratio}:1
                            </span>
                        </div>
                        <p class="card-text mb-1">
                            <i class="fas fa-user"></i> ${shift.staff_assigned}
                        </p>
                        <p class="card-text mb-1">
                            <i class="fas fa-clock"></i> ${shift.shift}
                        </p>
                        <p class="card-text mb-1">
                            <i class="fas fa-map-marker-alt"></i> ${shift.location || 'N/A'}
                        </p>
                        <p class="card-text">
                            <i class="fas fa-hourglass"></i> ${shift.hours} hours
                        </p>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="editShift('${shift.id}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteShift('${shift.id}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    groupByTime(schedule) {
        const grouped = {};
        
        schedule.sort((a, b) => {
            const timeA = a.shift.split('-')[0];
            const timeB = b.shift.split('-')[0];
            return timeA.localeCompare(timeB);
        });
        
        schedule.forEach(shift => {
            if (!grouped[shift.shift]) {
                grouped[shift.shift] = [];
            }
            grouped[shift.shift].push(shift);
        });
        
        return grouped;
    }
    
    getShiftColor(ratio) {
        const colors = {
            1: '#1cc88a',
            2: '#f6c23e',
            3: '#e74a3b',
            4: '#6f42c1'
        };
        return colors[ratio] || '#858796';
    }
    
    formatDate(date) {
        return date.toISOString().split('T')[0];
    }
    
    setupEventListeners() {
        const datePicker = document.getElementById('schedule-date');
        if (datePicker) {
            datePicker.addEventListener('change', (e) => {
                this.loadSchedule(e.target.value);
            });
        }
        
        const prevDay = document.getElementById('prev-day');
        if (prevDay) {
            prevDay.addEventListener('click', () => {
                this.currentDate.setDate(this.currentDate.getDate() - 1);
                this.loadSchedule();
                this.updateDateDisplay();
            });
        }
        
        const nextDay = document.getElementById('next-day');
        if (nextDay) {
            nextDay.addEventListener('click', () => {
                this.currentDate.setDate(this.currentDate.getDate() + 1);
                this.loadSchedule();
                this.updateDateDisplay();
            });
        }
    }
    
    updateDateDisplay() {
        const display = document.getElementById('current-date-display');
        if (display) {
            display.textContent = this.currentDate.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }
}

// Initialize schedule manager
document.addEventListener('DOMContentLoaded', () => {
    new ScheduleManager();
});

// Global functions for onclick handlers
function editShift(id) {
    console.log('Edit shift:', id);
    // Implement edit functionality
}

function deleteShift(id) {
    if (confirm('Are you sure you want to delete this shift?')) {
        fetch(`/api/shifts/${id}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(() => {
                location.reload();
            })
            .catch(error => {
                showToast('Failed to delete shift', 'danger');
            });
    }
}