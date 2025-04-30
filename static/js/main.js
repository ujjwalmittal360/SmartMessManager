/**
 * Smart Mess Management System
 * Main JavaScript File
 */

// Execute when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize popovers if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Popover) {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Add fade-out effect to alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade-out');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 500);
        }, 5000);
    });

    // Add confirmation to delete buttons
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Date picker initialization
    const datePickers = document.querySelectorAll('.date-picker');
    datePickers.forEach(input => {
        if (typeof flatpickr !== 'undefined') {
            flatpickr(input, {
                dateFormat: "Y-m-d",
                altInput: true,
                altFormat: "F j, Y",
            });
        }
    });

    // Initialize select2 dropdowns if available
    if (typeof $ !== 'undefined' && $.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap4',
            width: '100%'
        });
    }

    // Setup loading indicators for forms
    const forms = document.querySelectorAll('form:not(.no-loading)');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            // Find submit button
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                // Store original text and disable button
                submitBtn.dataset.originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                submitBtn.disabled = true;
            }
        });
    });

    // Toggle password visibility
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordInput = document.querySelector(this.dataset.target);
            if (passwordInput) {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    this.innerHTML = '<i class="fas fa-eye-slash"></i>';
                } else {
                    passwordInput.type = 'password';
                    this.innerHTML = '<i class="fas fa-eye"></i>';
                }
            }
        });
    });

    // Handle mobile navigation
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            const navbarNav = document.querySelector('.navbar-nav');
            if (navbarNav) {
                navbarNav.classList.toggle('show');
            }
        });
    }

    // Initialize food waste charts if present
    initFoodWasteChart();
    initTodaysWasteAnalysis();
});

/**
 * Initialize the food waste chart for the last 7 days
 */
function initFoodWasteChart() {
    const chartContainer = document.getElementById('food-waste-chart');
    if (!chartContainer) return;

    // Fetch data from the API
    fetch('/api/food_waste_data')
        .then(response => response.json())
        .then(data => {
            if (!data.dates || !data.values || data.dates.length === 0) {
                chartContainer.innerHTML = '<div class="alert alert-info">No waste data available for the last 7 days.</div>';
                return;
            }

            // Use formatted dates from API if available, otherwise format them ourselves
            const formattedDates = data.formatted_dates || data.dates.map(date => {
                const parts = date.split('-');
                return `${parts[1]}/${parts[2]}`; // MM/DD format
            });

            // Create chart using Chart.js
            const ctx = document.createElement('canvas');
            chartContainer.innerHTML = '';
            chartContainer.appendChild(ctx);

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: formattedDates,
                    datasets: [{
                        label: 'Food Waste (kg)',
                        data: data.values,
                        backgroundColor: 'rgba(7, 122, 125, 0.7)',
                        borderColor: 'rgba(7, 122, 125, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Weight (kg)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Date'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error fetching food waste data:', error);
            chartContainer.innerHTML = '<div class="alert alert-danger">Error parsing chart data. Please try refreshing the page.</div>';
        });
}

/**
 * Initialize today's waste analysis chart
 */
function initTodaysWasteAnalysis() {
    const chartContainer = document.getElementById('todays-waste-analysis');
    if (!chartContainer) return;

    // Fetch data from the API
    fetch('/api/todays_waste_analysis')
        .then(response => response.json())
        .then(data => {
            if (!data.available) {
                chartContainer.innerHTML = `<div class="alert alert-info">${data.message || 'No waste data available for today.'}</div>`;
                chartContainer.innerHTML += '<p>Add waste data to see analytics and recommendations.</p>';
                return;
            }

            // Create HTML to display the data
            let html = '<h4>Today\'s Waste Summary</h4>';
            html += `<p>Total waste recorded: <strong>${data.total_waste.toFixed(2)} kg</strong></p>`;
            
            html += '<table class="table table-striped">';
            html += '<thead><tr><th>Meal</th><th>Waste (kg)</th><th>Prepared (kg)</th><th>Waste %</th></tr></thead>';
            html += '<tbody>';
            
            data.waste_by_meal.forEach(meal => {
                html += '<tr>';
                html += `<td>${meal.meal_type}</td>`;
                html += `<td>${meal.leftover_weight.toFixed(2)}</td>`;
                html += `<td>${meal.quantity_prepared ? meal.quantity_prepared.toFixed(2) : 'N/A'}</td>`;
                html += `<td>${meal.wastage_percentage ? meal.wastage_percentage.toFixed(2) + '%' : 'N/A'}</td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            
            chartContainer.innerHTML = html;
            
            // Add a pie chart if we have enough meal types
            if (data.waste_by_meal.length >= 2) {
                const canvas = document.createElement('canvas');
                canvas.id = 'waste-by-meal-chart';
                chartContainer.appendChild(canvas);
                
                const labels = data.waste_by_meal.map(meal => meal.meal_type);
                const values = data.waste_by_meal.map(meal => meal.leftover_weight);
                
                new Chart(canvas, {
                    type: 'pie',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: values,
                            backgroundColor: [
                                'rgba(7, 122, 125, 0.7)',
                                'rgba(122, 226, 207, 0.7)',
                                'rgba(245, 238, 221, 0.7)'
                            ],
                            borderColor: [
                                'rgba(7, 122, 125, 1)',
                                'rgba(122, 226, 207, 1)',
                                'rgba(245, 238, 221, 1)'
                            ],
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'right',
                            },
                            title: {
                                display: true,
                                text: 'Waste Distribution by Meal Type'
                            }
                        }
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error fetching today\'s waste analysis:', error);
            chartContainer.innerHTML = '<div class="alert alert-danger">Error parsing chart data. Please try refreshing the page.</div>';
        });
}

/**
 * Logout confirmation
 */
function confirmLogout() {
    if (confirm('Are you sure you want to log out?')) {
        window.location.href = '/logout';
    }
}
