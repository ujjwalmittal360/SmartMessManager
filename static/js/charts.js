/**
 * Chart utilities for Smart Mess Management System
 */

/**
 * Initialize a bar chart with the given data
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Chart labels
 * @param {Array} data - Chart data
 * @param {string} yAxisLabel - Label for Y-axis
 */
function createBarChart(elementId, title, labels, data, yAxisLabel) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Create chart using Chart.js
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
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
                        text: yAxisLabel
                    }
                },
                x: {
                    title: {
                        display: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

/**
 * Initialize a pie chart with the given data
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Chart labels
 * @param {Array} data - Chart data
 */
function createPieChart(elementId, title, labels, data) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Create chart using Chart.js
    new Chart(canvas, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(7, 122, 125, 0.7)',
                    'rgba(122, 226, 207, 0.7)',
                    'rgba(245, 238, 221, 0.7)',
                    'rgba(51, 51, 51, 0.7)',
                    'rgba(153, 102, 255, 0.7)'
                ],
                borderColor: [
                    'rgba(7, 122, 125, 1)',
                    'rgba(122, 226, 207, 1)',
                    'rgba(245, 238, 221, 1)',
                    'rgba(51, 51, 51, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

/**
 * Initialize a line chart with the given data
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Chart labels
 * @param {Array} data - Chart data
 * @param {string} yAxisLabel - Label for Y-axis
 */
function createLineChart(elementId, title, labels, data, yAxisLabel) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Create chart using Chart.js
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                fill: false,
                backgroundColor: 'rgba(7, 122, 125, 0.7)',
                borderColor: 'rgba(7, 122, 125, 1)',
                tension: 0.1
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
                        text: yAxisLabel
                    }
                },
                x: {
                    title: {
                        display: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                }
            }
        }
    });
}

/**
 * Initialize student wastage bar chart
 * @param {Array} studentData - Array of student wastage data objects
 */
function initStudentWastageChart(studentData) {
    if (!studentData || studentData.length === 0) return;
    
    // Limit to top 10 students for readability
    const data = studentData.slice(0, 10);
    
    // Extract names and wastage values
    const names = data.map(student => student.name);
    const values = data.map(student => student.leftover_weight);
    
    createBarChart(
        'student-wastage-chart',
        'Students with Highest Cumulative Wastage',
        names,
        values,
        'Wastage (kg)'
    );
}

/**
 * Initialize meal type wastage pie chart
 * @param {Array} mealTypeData - Array of meal type wastage data objects
 */
function initMealTypeWastageChart(mealTypeData) {
    if (!mealTypeData || mealTypeData.length === 0) return;
    
    // Extract meal types and wastage values
    const mealTypes = mealTypeData.map(item => item.meal_type);
    const values = mealTypeData.map(item => item.leftover_weight);
    
    createPieChart(
        'meal-type-wastage-chart',
        'Wastage Distribution by Meal Type',
        mealTypes,
        values
    );
}

/**
 * Initialize historical wastage line chart
 * @param {Array} dates - Array of date strings
 * @param {Array} values - Array of wastage values
 */
function initHistoricalWastageChart(dates, values) {
    if (!dates || !values || dates.length === 0) return;
    
    // Format dates to be more readable
    const formattedDates = dates.map(date => {
        const parts = date.split('-');
        return `${parts[1]}/${parts[2]}`;
    });
    
    createLineChart(
        'historical-wastage-chart',
        'Food Wastage Trend',
        formattedDates,
        values,
        'Wastage (kg)'
    );
}

/**
 * Initialize daily student attendance chart
 * @param {Object} attendanceData - Object containing attendance data
 */
function initDailyAttendanceChart(attendanceData) {
    if (!attendanceData || !attendanceData.dates) return;
    
    const canvas = document.getElementById('overview-attendance-chart');
    if (!canvas) return;
    
    // Format dates to be more readable
    const formattedDates = attendanceData.dates.map(date => {
        const parts = date.split('-');
        return `${parts[1]}/${parts[2]}`;
    });
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: formattedDates,
            datasets: [
                {
                    label: 'Breakfast',
                    data: attendanceData.breakfast || [],
                    fill: false,
                    borderColor: 'rgba(7, 122, 125, 1)',
                    backgroundColor: 'rgba(7, 122, 125, 0.7)',
                    tension: 0.1
                },
                {
                    label: 'Lunch',
                    data: attendanceData.lunch || [],
                    fill: false,
                    borderColor: 'rgba(122, 226, 207, 1)',
                    backgroundColor: 'rgba(122, 226, 207, 0.7)',
                    tension: 0.1
                },
                {
                    label: 'Dinner',
                    data: attendanceData.dinner || [],
                    fill: false,
                    borderColor: 'rgba(245, 238, 221, 1)',
                    backgroundColor: 'rgba(245, 238, 221, 0.7)',
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

/**
 * Initialize food prepared vs consumed chart
 * @param {Object} consumptionData - Object containing consumption data
 */
function initFoodConsumptionChart(consumptionData) {
    if (!consumptionData || !consumptionData.dates) return;
    
    const canvas = document.getElementById('overview-consumption-chart');
    if (!canvas) return;
    
    // Format dates to be more readable
    const formattedDates = consumptionData.dates.map(date => {
        const parts = date.split('-');
        return `${parts[1]}/${parts[2]}`;
    });
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: formattedDates,
            datasets: [
                {
                    label: 'Prepared',
                    data: consumptionData.prepared || [],
                    fill: false,
                    borderColor: 'rgba(7, 122, 125, 1)',
                    backgroundColor: 'rgba(7, 122, 125, 0.7)',
                    tension: 0.1
                },
                {
                    label: 'Consumed',
                    data: consumptionData.consumed || [],
                    fill: false,
                    borderColor: 'rgba(122, 226, 207, 1)',
                    backgroundColor: 'rgba(122, 226, 207, 0.7)',
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

/**
 * Initialize meal type efficiency chart
 * @param {Object} consumptionData - Object containing consumption data
 */
function initMealEfficiencyChart(consumptionData) {
    if (!consumptionData || !consumptionData.meal_types) return;
    
    const canvas = document.getElementById('overview-efficiency-chart');
    if (!canvas) return;
    
    // Calculate efficiency for each meal type
    const efficiencyData = consumptionData.meal_types.map((mealType, index) => {
        const prepared = consumptionData.meal_prepared[index] || 0;
        const consumed = consumptionData.meal_consumed[index] || 0;
        return (consumed / prepared * 100) || 0;
    });
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: consumptionData.meal_types,
            datasets: [{
                label: 'Consumption Efficiency',
                data: efficiencyData,
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
                    max: 100,
                    title: {
                        display: true,
                        text: 'Efficiency (%)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Meal Type Efficiency',
                    font: { size: 16 }
                }
            }
        }
    });
}

/**
 * Initialize consumption efficiency heatmap
 * @param {Object} consumptionData - Object containing consumption data
 */
function initConsumptionHeatmap(consumptionData) {
    if (!consumptionData || !consumptionData.heatmap_days) return;
    
    const canvas = document.getElementById('overview-heatmap-chart');
    if (!canvas) return;
    
    new Chart(canvas, {
        type: 'matrix',
        data: {
            datasets: [{
                label: 'Consumption Efficiency',
                data: consumptionData.heatmap_data.flat().map((value, index) => ({
                    x: index % 3,
                    y: Math.floor(index / 3),
                    v: value
                })),
                backgroundColor(context) {
                    const value = context.dataset.data[context.dataIndex].v;
                    const alpha = Math.min(Math.max(value / 100, 0), 1);
                    return `rgba(7, 122, 125, ${alpha})`;
                },
                width: ({ chart }) => (chart.chartArea || {}).width / 3 - 1,
                height: ({ chart }) => (chart.chartArea || {}).height / 7 - 1
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
                    ticks: {
                        display: true
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'category',
                    labels: consumptionData.heatmap_days,
                    offset: true,
                    ticks: {
                        display: true
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Consumption Efficiency Heatmap',
                    font: { size: 16 }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const value = context.dataset.data[context.dataIndex].v;
                            return `Efficiency: ${value.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize daily attendance by meal type chart
 * @param {Object} attendanceData - Object containing attendance data
 */
function initDailyAttendanceByMealChart(attendanceData) {
    if (!attendanceData || !attendanceData.dates) {
        console.error('Missing attendance data for daily attendance chart');
        return;
    }
    
    const canvas = document.getElementById('daily-attendance-chart');
    if (!canvas) {
        console.error('Canvas element not found for daily attendance chart');
        return;
    }
    
    // Format dates to be more readable
    const formattedDates = attendanceData.dates.map(date => {
        const parts = date.split('-');
        return `${parts[1]}/${parts[2]}`;
    });
    
    // Ensure all meal type arrays have the same length
    const maxLength = Math.max(
        attendanceData.breakfast?.length || 0,
        attendanceData.lunch?.length || 0,
        attendanceData.dinner?.length || 0
    );
    
    // Pad arrays with zeros if needed
    const breakfast = (attendanceData.breakfast || []).concat(Array(maxLength - (attendanceData.breakfast?.length || 0)).fill(0));
    const lunch = (attendanceData.lunch || []).concat(Array(maxLength - (attendanceData.lunch?.length || 0)).fill(0));
    const dinner = (attendanceData.dinner || []).concat(Array(maxLength - (attendanceData.dinner?.length || 0)).fill(0));
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: formattedDates,
            datasets: [
                {
                    label: 'Breakfast',
                    data: breakfast,
                    fill: false,
                    borderColor: 'rgba(7, 122, 125, 1)',
                    backgroundColor: 'rgba(7, 122, 125, 0.7)',
                    tension: 0.1
                },
                {
                    label: 'Lunch',
                    data: lunch,
                    fill: false,
                    borderColor: 'rgba(122, 226, 207, 1)',
                    backgroundColor: 'rgba(122, 226, 207, 0.7)',
                    tension: 0.1
                },
                {
                    label: 'Dinner',
                    data: dinner,
                    fill: false,
                    borderColor: 'rgba(245, 238, 221, 1)',
                    backgroundColor: 'rgba(245, 238, 221, 0.7)',
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
                    text: 'Daily Student Attendance by Meal Type',
                    font: { size: 16 }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

/**
 * Initialize average attendance by day of week chart
 * @param {Object} attendanceData - Object containing attendance data
 */
function initDayOfWeekAttendanceChart(attendanceData) {
    if (!attendanceData || !attendanceData.days) {
        console.error('Missing attendance data for day of week chart');
        return;
    }
    
    const canvas = document.getElementById('day-attendance-chart');
    if (!canvas) {
        console.error('Canvas element not found for day of week chart');
        return;
    }
    
    // Ensure all arrays have the same length
    const maxLength = Math.max(
        attendanceData.days?.length || 0,
        attendanceData.avg_breakfast?.length || 0,
        attendanceData.avg_lunch?.length || 0,
        attendanceData.avg_dinner?.length || 0
    );
    
    // Pad arrays with zeros if needed
    const days = (attendanceData.days || []).concat(Array(maxLength - (attendanceData.days?.length || 0)).fill(''));
    const avgBreakfast = (attendanceData.avg_breakfast || []).concat(Array(maxLength - (attendanceData.avg_breakfast?.length || 0)).fill(0));
    const avgLunch = (attendanceData.avg_lunch || []).concat(Array(maxLength - (attendanceData.avg_lunch?.length || 0)).fill(0));
    const avgDinner = (attendanceData.avg_dinner || []).concat(Array(maxLength - (attendanceData.avg_dinner?.length || 0)).fill(0));
    
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: days,
            datasets: [
                {
                    label: 'Breakfast',
                    data: avgBreakfast,
                    backgroundColor: 'rgba(7, 122, 125, 0.7)',
                    borderColor: 'rgba(7, 122, 125, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Lunch',
                    data: avgLunch,
                    backgroundColor: 'rgba(122, 226, 207, 0.7)',
                    borderColor: 'rgba(122, 226, 207, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Dinner',
                    data: avgDinner,
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
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

/**
 * Initialize attendance trend analysis chart
 * @param {Object} attendanceData - Object containing attendance data
 */
function initAttendanceTrendChart(attendanceData) {
    if (!attendanceData || !attendanceData.dates) {
        console.error('Missing attendance data for trend chart');
        return;
    }
    
    const canvas = document.getElementById('attendance-trend-chart');
    if (!canvas) {
        console.error('Canvas element not found for trend chart');
        return;
    }
    
    // Calculate total daily attendance
    const totalDailyAttendance = attendanceData.dates.map((date, index) => {
        const breakfast = attendanceData.breakfast?.[index] || 0;
        const lunch = attendanceData.lunch?.[index] || 0;
        const dinner = attendanceData.dinner?.[index] || 0;
        return breakfast + lunch + dinner;
    });
    
    // Format dates to be more readable
    const formattedDates = attendanceData.dates.map(date => {
        const parts = date.split('-');
        return `${parts[1]}/${parts[2]}`;
    });
    
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: formattedDates,
            datasets: [{
                label: 'Total Daily Attendance',
                data: totalDailyAttendance,
                fill: false,
                borderColor: 'rgba(7, 122, 125, 1)',
                backgroundColor: 'rgba(7, 122, 125, 0.7)',
                tension: 0.1
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
                        text: 'Total Attendance'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Attendance Trend Analysis',
                    font: { size: 16 }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

// Initialize all charts when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get data from template
    const attendanceData = JSON.parse(document.getElementById('attendance-data').textContent || '{}');
    const consumptionData = JSON.parse(document.getElementById('consumption-data').textContent || '{}');
    
    // Initialize overview charts
    initDailyAttendanceChart(attendanceData);
    initFoodConsumptionChart(consumptionData);
    initMealEfficiencyChart(consumptionData);
    initConsumptionHeatmap(consumptionData);
    
    // Initialize attendance analysis charts
    initDailyAttendanceByMealChart(attendanceData);
    initDayOfWeekAttendanceChart(attendanceData);
    initAttendanceTrendChart(attendanceData);
});
