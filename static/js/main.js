/**
 * ExpenseWise - Interactive Client-Side Logic
 * Features:
 * 1. Chart.js Category Breakdown Rendering via Fetch API
 * 2. Instant Table Search & Filtering (DOM Manipulation)
 * 3. Alert Auto-dismiss
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss Alert Messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 400);
        }, 4000);
    });

    // 2. Load Chart.js Doughnut Chart if Canvas exists
    const chartCanvas = document.getElementById('expenseChart');
    if (chartCanvas) {
        loadCategoryChart(chartCanvas);
    }

    // 3. Instant Client-Side Live Search on Tables
    const searchInput = document.getElementById('tableSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const tableRows = document.querySelectorAll('.expense-row');
            
            tableRows.forEach(row => {
                const title = row.querySelector('.expense-title')?.innerText.toLowerCase() || '';
                const category = row.querySelector('.expense-category')?.innerText.toLowerCase() || '';
                const payment = row.querySelector('.expense-payment')?.innerText.toLowerCase() || '';
                
                if (title.includes(query) || category.includes(query) || payment.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
});

/**
 * Fetch category distribution from Django API endpoint and render Chart.js
 */
async function loadCategoryChart(canvas) {
    try {
        const response = await fetch('/api/chart-data/');
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        const placeholder = document.getElementById('chartPlaceholder');

        if (!data.has_data) {
            canvas.style.display = 'none';
            if (placeholder) placeholder.style.display = 'block';
            return;
        }

        if (placeholder) placeholder.style.display = 'none';
        canvas.style.display = 'block';

        const ctx = canvas.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.colors,
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 12,
                            font: {
                                family: "'Inter', sans-serif",
                                size: 12
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` ${context.label}: ₹${context.raw.toLocaleString('en-IN')}`;
                            }
                        }
                    }
                },
                cutout: '65%'
            }
        });
    } catch (error) {
        console.error('Error loading chart:', error);
    }
}
