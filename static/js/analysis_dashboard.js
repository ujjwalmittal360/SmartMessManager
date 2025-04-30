// Analysis Dashboard Chart Initialization
document.addEventListener('DOMContentLoaded', function() {
    // Get data from hidden script elements
    const attendanceData = JSON.parse(document.getElementById('attendance-data').textContent || '{}');
    const consumptionData = JSON.parse(document.getElementById('consumption-data').textContent || '{}');
    const predictionData = JSON.parse(document.getElementById('prediction-data').textContent || '{}');

    // Initialize Overview Charts
    initOverviewCharts(attendanceData, consumptionData);
    
    // Initialize Attendance Analysis Charts
    initAttendanceCharts(attendanceData);
    
    // Initialize Consumption Analysis Charts
    initConsumptionCharts(consumptionData);
    
    // Initialize Prediction Charts
    initPredictionCharts(predictionData);
});

function initOverviewCharts(attendanceData, consumptionData) {
    // Daily Attendance Chart
    if (attendanceData.dates && attendanceData.breakfast && attendanceData.lunch && attendanceData.dinner) {
        const ctx = document.getElementById('daily-attendance-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: attendanceData.dates,
                datasets: [
                    {
                        label: 'Breakfast',
                        data: attendanceData.breakfast,
                        borderColor: 'rgba(7, 122, 125, 1)',
                        backgroundColor: 'rgba(7, 122, 125, 0.2)',
                        tension: 0.1
                    },
                    {
                        label: 'Lunch',
                        data: attendanceData.lunch,
                        borderColor: 'rgba(122, 226, 207, 1)',
                        backgroundColor: 'rgba(122, 226, 207, 0.2)',
                        tension: 0.1
                    },
                    {
                        label: 'Dinner',
                        data: attendanceData.dinner,
                        borderColor: 'rgba(245, 238, 221, 1)',
                        backgroundColor: 'rgba(245, 238, 221, 0.2)',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Students'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Daily Student Attendance',
                        font: { size: 16 }
                    }
                }
            }
        });
    }

    // Food Consumption Chart
    if (consumptionData.dates && consumptionData.prepared && consumptionData.consumed) {
        const ctx = document.getElementById('food-consumption-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: consumptionData.dates,
                datasets: [
                    {
                        label: 'Prepared',
                        data: consumptionData.prepared,
                        borderColor: 'rgba(7, 122, 125, 1)',
                        backgroundColor: 'rgba(7, 122, 125, 0.2)',
                        tension: 0.1
                    },
                    {
                        label: 'Consumed',
                        data: consumptionData.consumed,
                        borderColor: 'rgba(122, 226, 207, 1)',
                        backgroundColor: 'rgba(122, 226, 207, 0.2)',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantity (kg)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Food Prepared vs Consumed',
                        font: { size: 16 }
                    }
                }
            }
        });
    }
}

function initAttendanceCharts(attendanceData) {
    // Daily Attendance by Meal Chart
    if (attendanceData.dates && attendanceData.breakfast && attendanceData.lunch && attendanceData.dinner) {
        const ctx = document.getElementById('daily-attendance-by-meal-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: attendanceData.dates,
                datasets: [
                    {
                        label: 'Breakfast',
                        data: attendanceData.breakfast,
                        borderColor: 'rgba(7, 122, 125, 1)',
                        backgroundColor: 'rgba(7, 122, 125, 0.2)',
                        tension: 0.1
                    },
                    {
                        label: 'Lunch',
                        data: attendanceData.lunch,
                        borderColor: 'rgba(122, 226, 207, 1)',
                        backgroundColor: 'rgba(122, 226, 207, 0.2)',
                        tension: 0.1
                    },
                    {
                        label: 'Dinner',
                        data: attendanceData.dinner,
                        borderColor: 'rgba(245, 238, 221, 1)',
                        backgroundColor: 'rgba(245, 238, 221, 0.2)',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Students'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Daily Attendance by Meal Type',
                        font: { size: 16 }
                    }
                }
            }
        });
    }

    // Average Attendance by Day of Week Chart
    if (attendanceData.days && attendanceData.avg_breakfast && attendanceData.avg_lunch && attendanceData.avg_dinner) {
        const ctx = document.getElementById('day-of-week-attendance-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: attendanceData.days,
                datasets: [
                    {
                        label: 'Breakfast',
                        data: attendanceData.avg_breakfast,
                        backgroundColor: 'rgba(7, 122, 125, 0.7)',
                        borderColor: 'rgba(7, 122, 125, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Lunch',
                        data: attendanceData.avg_lunch,
                        backgroundColor: 'rgba(122, 226, 207, 0.7)',
                        borderColor: 'rgba(122, 226, 207, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Dinner',
                        data: attendanceData.avg_dinner,
                        backgroundColor: 'rgba(245, 238, 221, 0.7)',
                        borderColor: 'rgba(245, 238, 221, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Average Attendance'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Average Attendance by Day of Week',
                        font: { size: 16 }
                    }
                }
            }
        });
    }
}

function initConsumptionCharts(consumptionData) {
    // Meal Type Consumption Chart
    if (consumptionData.meal_types && consumptionData.meal_prepared && consumptionData.meal_consumed) {
        const ctx = document.getElementById('meal-type-consumption-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: consumptionData.meal_types,
                datasets: [
                    {
                        label: 'Prepared',
                        data: consumptionData.meal_prepared,
                        backgroundColor: 'rgba(7, 122, 125, 0.7)',
                        borderColor: 'rgba(7, 122, 125, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Consumed',
                        data: consumptionData.meal_consumed,
                        backgroundColor: 'rgba(122, 226, 207, 0.7)',
                        borderColor: 'rgba(122, 226, 207, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Quantity (kg)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Food Quantities by Meal Type',
                        font: { size: 16 }
                    }
                }
            }
        });
    }

    // Consumption Heatmap
    if (consumptionData.heatmap_days && consumptionData.heatmap_data) {
        const ctx = document.getElementById('consumption-heatmap').getContext('2d');
        new Chart(ctx, {
            type: 'matrix',
            data: {
                datasets: [{
                    data: consumptionData.heatmap_data.map((row, i) => 
                        row.map((value, j) => ({
                            x: j,
                            y: i,
                            v: value
                        }))
                    ).flat(),
                    backgroundColor: function(context) {
                        const value = context.dataset.data[context.dataIndex].v;
                        const alpha = value / 100;
                        return `rgba(7, 122, 125, ${alpha})`;
                    },
                    width: ({chart}) => (chart.chartArea || {}).width / 3 - 1,
                    height: ({chart}) => (chart.chartArea || {}).height / 7 - 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'category',
                        labels: ['Breakfast', 'Lunch', 'Dinner'],
                        offset: true,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        type: 'category',
                        labels: consumptionData.heatmap_days,
                        offset: true,
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Consumption Efficiency by Day and Meal',
                        font: { size: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            title: function(context) {
                                return `${consumptionData.heatmap_days[context[0].y]}, ${['Breakfast', 'Lunch', 'Dinner'][context[0].x]}`;
                            },
                            label: function(context) {
                                return `Efficiency: ${context.dataset.data[context.dataIndex].v}%`;
                            }
                        }
                    }
                }
            }
        });
    }
}

function initPredictionCharts(predictionData) {
    // Actual vs Predicted Consumption Chart
    if (predictionData.actual && predictionData.predicted) {
        const ctx = document.getElementById('prediction-accuracy-chart').getContext('2d');
        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Actual vs Predicted',
                    data: predictionData.actual.map((value, index) => ({
                        x: value,
                        y: predictionData.predicted[index]
                    })),
                    backgroundColor: 'rgba(7, 122, 125, 0.7)',
                    borderColor: 'rgba(7, 122, 125, 1)',
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Actual Consumption (kg)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Predicted Consumption (kg)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Prediction Accuracy Analysis',
                        font: { size: 16 }
                    }
                }
            }
        });
    }

    // Consumption Rate Distribution Chart
    if (predictionData.consumption_rate_bins && predictionData.consumption_rate_counts) {
        const ctx = document.getElementById('consumption-rate-distribution-chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: predictionData.consumption_rate_bins,
                datasets: [{
                    label: 'Frequency',
                    data: predictionData.consumption_rate_counts,
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
                            text: 'Frequency'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Consumption Rate (kg per student)'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribution of Food Consumption Rates',
                        font: { size: 16 }
                    }
                }
            }
        });
    }
} 