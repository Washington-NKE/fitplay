// Dashboard JavaScript for FitPlay
class FitPlayDashboard {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        this.setupCharts();
        this.updateStats();
        this.setupAutoRefresh();
    }

    setupCharts() {
        this.createWeeklyChart();
    }

    async createWeeklyChart() {
        try {
            const response = await fetch('/dashboard/weekly_progress');
            const data = await response.json();
            
            const ctx = document.getElementById('weeklyChart').getContext('2d');
            
            this.charts.weekly = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => d.day),
                    datasets: [
                        {
                            label: 'Calories Burned',
                            data: data.map(d => d.calories),
                            borderColor: 'rgb(220, 53, 69)',
                            backgroundColor: 'rgba(220, 53, 69, 0.1)',
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Workouts',
                            data: data.map(d => d.workouts),
                            borderColor: 'rgb(40, 167, 69)',
                            backgroundColor: 'rgba(40, 167, 69, 0.1)',
                            fill: true,
                            tension: 0.4,
                            yAxisID: 'y1'
                        },
                        {
                            label: 'Time Active (min)',
                            data: data.map(d => d.time_active),
                            borderColor: 'rgb(23, 162, 184)',
                            backgroundColor: 'rgba(23, 162, 184, 0.1)',
                            fill: true,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Weekly Fitness Progress'
                        },
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: {
                                display: true,
                                text: 'Calories / Time (min)'
                            }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: {
                                display: true,
                                text: 'Workouts'
                            },
                            grid: {
                                drawOnChartArea: false,
                            },
                        }
                    },
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
        } catch (error) {
            console.error('Error creating weekly chart:', error);
        }
    }

    async updateStats() {
        try {
            const response = await fetch('/dashboard/stats');
            const stats = await response.json();
            
            // Update stat displays with animation
            this.animateCounter('total-points', stats.points);
            this.animateCounter('total-workouts', stats.workouts_completed);
            this.animateCounter('total-calories', stats.calories_burned);
            
            // Update time display
            const timeElement = document.getElementById('total-time');
            if (timeElement) {
                timeElement.textContent = `${stats.time_active.toFixed(1)}min`;
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    animateCounter(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000; // 1 second
        const startTime = Date.now();
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutQuart);
            element.textContent = currentValue;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = targetValue;
            }
        };
        
        animate();
    }

    async updateAchievementProgress() {
        try {
            const response = await fetch('/dashboard/achievement_progress');
            const progress = await response.json();
            
            // Update achievement progress bars
            Object.keys(progress).forEach(key => {
                const achievement = progress[key];
                const progressBar = document.querySelector(`[data-achievement="${key}"] .progress-bar`);
                if (progressBar) {
                    progressBar.style.width = `${achievement.progress}%`;
                    progressBar.setAttribute('aria-valuenow', achievement.current);
                }
            });
        } catch (error) {
            console.error('Error updating achievement progress:', error);
        }
    }

    setupAutoRefresh() {
        // Refresh stats every 30 seconds
        setInterval(() => {
            this.updateStats();
            this.updateAchievementProgress();
        }, 30000);
    }

    // Method to refresh charts when window resizes
    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.resize();
            }
        });
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.fitPlayDashboard = new FitPlayDashboard();
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.fitPlayDashboard) {
        window.fitPlayDashboard.resizeCharts();
    }
});

// Add some interactive elements
document.addEventListener('DOMContentLoaded', () => {
    // Add hover effects to stat cards
    const statCards = document.querySelectorAll('.stats-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
        });
    });
    
    // Add click-to-refresh functionality
    const refreshBtn = document.createElement('button');
    refreshBtn.className = 'btn btn-outline-primary btn-sm';
    refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i>Refresh';
    refreshBtn.onclick = () => {
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Refreshing...';
        window.fitPlayDashboard.updateStats().then(() => {
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt me-1"></i>Refresh';
        });
    };
    
    // Add refresh button to dashboard header
    const dashboardHeader = document.querySelector('h2');
    if (dashboardHeader) {
        dashboardHeader.parentNode.insertBefore(refreshBtn, dashboardHeader.nextSibling);
    }
});

// Add smooth scrolling for dashboard navigation
document.addEventListener('DOMContentLoaded', () => {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
