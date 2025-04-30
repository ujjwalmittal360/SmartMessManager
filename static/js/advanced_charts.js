/**
 * Advanced Chart Utilities for Smart Mess Management System Analytics Dashboard
 */

/**
 * Initialize a multi-line chart with multiple datasets
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Chart labels (x-axis)
 * @param {Array} datasets - Array of dataset objects with label, data, and optional color
 * @param {string} yAxisLabel - Label for Y-axis
 */
function createMultiLineChart(elementId, title, labels, datasets, yAxisLabel) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Define default colors if not provided
    const defaultColors = [
        { backgroundColor: 'rgba(7, 122, 125, 0.2)', borderColor: 'rgba(7, 122, 125, 1)' },
        { backgroundColor: 'rgba(255, 99, 132, 0.2)', borderColor: 'rgba(255, 99, 132, 1)' },
        { backgroundColor: 'rgba(54, 162, 235, 0.2)', borderColor: 'rgba(54, 162, 235, 1)' },
        { backgroundColor: 'rgba(255, 206, 86, 0.2)', borderColor: 'rgba(255, 206, 86, 1)' },
        { backgroundColor: 'rgba(75, 192, 192, 0.2)', borderColor: 'rgba(75, 192, 192, 1)' }
    ];
    
    // Format datasets with colors
    const chartDatasets = datasets.map((dataset, index) => {
        const colorIndex = index % defaultColors.length;
        return {
            label: dataset.label,
            data: dataset.data,
            backgroundColor: dataset.backgroundColor || defaultColors[colorIndex].backgroundColor,
            borderColor: dataset.borderColor || defaultColors[colorIndex].borderColor,
            fill: dataset.fill !== undefined ? dataset.fill : false,
            tension: 0.1
        };
    });
    
    // Create chart
    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: chartDatasets
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
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Initialize a stacked bar chart
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Chart labels (x-axis)
 * @param {Array} datasets - Array of dataset objects with label, data, and optional color
 * @param {string} yAxisLabel - Label for Y-axis
 */
function createStackedBarChart(elementId, title, labels, datasets, yAxisLabel) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Define default colors if not provided
    const defaultColors = [
        { backgroundColor: 'rgba(7, 122, 125, 0.7)', borderColor: 'rgba(7, 122, 125, 1)' },
        { backgroundColor: 'rgba(255, 99, 132, 0.7)', borderColor: 'rgba(255, 99, 132, 1)' },
        { backgroundColor: 'rgba(54, 162, 235, 0.7)', borderColor: 'rgba(54, 162, 235, 1)' },
        { backgroundColor: 'rgba(255, 206, 86, 0.7)', borderColor: 'rgba(255, 206, 86, 1)' },
        { backgroundColor: 'rgba(75, 192, 192, 0.7)', borderColor: 'rgba(75, 192, 192, 1)' }
    ];
    
    // Format datasets with colors
    const chartDatasets = datasets.map((dataset, index) => {
        const colorIndex = index % defaultColors.length;
        return {
            label: dataset.label,
            data: dataset.data,
            backgroundColor: dataset.backgroundColor || defaultColors[colorIndex].backgroundColor,
            borderColor: dataset.borderColor || defaultColors[colorIndex].borderColor,
            borderWidth: 1
        };
    });
    
    // Create chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: chartDatasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: yAxisLabel
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
                    position: 'top'
                }
            }
        }
    });
}

/**
 * Initialize a scatter plot
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} xData - X-axis data points
 * @param {Array} yData - Y-axis data points
 * @param {string} xAxisLabel - Label for X-axis
 * @param {string} yAxisLabel - Label for Y-axis
 */
function createScatterPlot(elementId, title, xData, yData, xAxisLabel, yAxisLabel) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Create data points array
    const data = xData.map((x, i) => ({
        x: x,
        y: yData[i]
    }));
    
    // Create chart
    new Chart(canvas, {
        type: 'scatter',
        data: {
            datasets: [{
                label: title,
                data: data,
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
                        text: xAxisLabel
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: yAxisLabel
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
 * Initialize a heatmap chart
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} xLabels - X-axis labels
 * @param {Array} yLabels - Y-axis labels
 * @param {Array} data - 2D array of values
 */
function createHeatmap(elementId, title, xLabels, yLabels, data) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Format data for Chart.js
    const datasets = yLabels.map((yLabel, i) => ({
        label: yLabel,
        data: data[i].map((value, j) => ({
            x: xLabels[j],
            y: yLabel,
            v: value
        }))
    }));
    
    // Create chart with custom plugin for heatmap
    new Chart(canvas, {
        type: 'matrix',
        data: {
            datasets: [{
                label: title,
                data: datasets.flatMap(dataset => 
                    dataset.data.map(point => ({
                        x: point.x,
                        y: point.y,
                        v: point.v
                    }))
                ),
                backgroundColor(context) {
                    const value = context.dataset.data[context.dataIndex].v;
                    // Color scale from red (0%) to green (100%)
                    if (value < 50) {
                        // Red to yellow (0-50%)
                        const r = 255;
                        const g = Math.round((value / 50) * 255);
                        return `rgba(${r}, ${g}, 0, 0.8)`;
                    } else {
                        // Yellow to green (50-100%)
                        const r = Math.round(255 - ((value - 50) / 50) * 255);
                        const g = 255;
                        return `rgba(${r}, ${g}, 0, 0.8)`;
                    }
                },
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1,
                width: ({ chart }) => (chart.chartArea || {}).width / xLabels.length - 2,
                height: ({ chart }) => (chart.chartArea || {}).height / yLabels.length - 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'category',
                    labels: xLabels,
                    offset: true,
                    ticks: {
                        align: 'center'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    type: 'category',
                    labels: yLabels,
                    offset: true,
                    ticks: {
                        align: 'center'
                    },
                    grid: {
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
                },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const data = context.dataset.data[context.dataIndex];
                            return `${data.y} - ${data.x}: ${data.v.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize a horizontal bar chart
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Chart labels (y-axis for horizontal bar)
 * @param {Array} data - Chart data
 * @param {string} xAxisLabel - Label for X-axis
 */
function createHorizontalBarChart(elementId, title, labels, data, xAxisLabel) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Create chart
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
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: xAxisLabel
                    }
                },
                y: {
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
 * Initialize a histogram
 * @param {string} elementId - ID of the canvas element
 * @param {string} title - Chart title
 * @param {Array} labels - Bin labels
 * @param {Array} counts - Frequency counts
 * @param {string} xAxisLabel - Label for X-axis
 * @param {string} yAxisLabel - Label for Y-axis
 */
function createHistogram(elementId, title, labels, counts, xAxisLabel, yAxisLabel) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return;
    
    // Create chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: counts,
                backgroundColor: 'rgba(7, 122, 125, 0.7)',
                borderColor: 'rgba(7, 122, 125, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: xAxisLabel
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: yAxisLabel
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

// Register matrix chart type
Chart.register({
    id: 'matrix',
    beforeInit(chart) {
        const originalFit = chart.legend.fit;
        chart.legend.fit = function fit() {
            originalFit.bind(chart.legend)();
            this.height += 10;
        };
    },
    defaults: {
        datasets: {
            matrix: {
                borderWidth: 1,
                borderColor: 'rgba(0, 0, 0, 0.1)',
                backgroundColor: 'rgba(0, 0, 0, 0.1)',
                width: 20,
                height: 20
            }
        }
    },
    controller: class MatrixController extends Chart.DatasetController {
        draw() {
            const meta = this._cachedMeta;
            const { data } = meta;
            const { ctx } = this.chart;
            
            data.forEach(element => {
                const { x, y, width, height } = element;
                ctx.save();
                ctx.fillStyle = element.options.backgroundColor;
                ctx.fillRect(x - width / 2, y - height / 2, width, height);
                
                ctx.strokeStyle = element.options.borderColor;
                ctx.lineWidth = element.options.borderWidth;
                ctx.strokeRect(x - width / 2, y - height / 2, width, height);
                
                // Optional: add value text in the center
                const value = element.$context.raw.v;
                if (value !== undefined) {
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
                    ctx.font = '12px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(value.toFixed(1), x, y);
                }
                
                ctx.restore();
            });
        }
        
        updateElement(element, index, properties, mode) {
            Object.assign(element, properties);
            
            const dataset = this.getDataset();
            const data = dataset.data[index];
            
            element.$context = {
                chart: this.chart,
                dataIndex: index,
                dataset,
                datasetIndex: this.index,
                raw: data
            };
            
            if (mode !== 'reset') {
                this.updateElementGeometry(element, index, properties, mode);
            }
        }
        
        updateElementGeometry(element, index, properties, mode) {
            const dataset = this.getDataset();
            const data = dataset.data[index];
            const xScale = this._getScaleForId('x');
            const yScale = this._getScaleForId('y');
            
            const width = dataset.width || 20;
            const height = dataset.height || 20;
            
            element.x = xScale.getPixelForValue(data.x);
            element.y = yScale.getPixelForValue(data.y);
            element.width = typeof width === 'function' ? width({ chart: this.chart }) : width;
            element.height = typeof height === 'function' ? height({ chart: this.chart }) : height;
        }
    },
    elements: {
        matrix: class MatrixElement extends Chart.Element {
            constructor() {
                super();
                this.x = undefined;
                this.y = undefined;
                this.width = undefined;
                this.height = undefined;
            }
            
            draw(ctx) {
                const { x, y, width, height, options } = this;
                
                ctx.save();
                
                ctx.fillStyle = options.backgroundColor;
                ctx.fillRect(x - width / 2, y - height / 2, width, height);
                
                ctx.strokeStyle = options.borderColor;
                ctx.lineWidth = options.borderWidth;
                ctx.strokeRect(x - width / 2, y - height / 2, width, height);
                
                ctx.restore();
            }
            
            inRange(mouseX, mouseY) {
                const { x, y, width, height } = this;
                return (
                    mouseX >= x - width / 2 &&
                    mouseX <= x + width / 2 &&
                    mouseY >= y - height / 2 &&
                    mouseY <= y + height / 2
                );
            }
            
            inXRange(mouseX) {
                return this.inRange(mouseX, this.y);
            }
            
            inYRange(mouseY) {
                return this.inRange(this.x, mouseY);
            }
        }
    }
});

/**
 * Initialize attendance charts for meal breakdown
 * @param {Object} attendanceData - Object containing attendance data
 */
function initAttendanceCharts(attendanceData) {
    if (!attendanceData || !attendanceData.dates || attendanceData.dates.length === 0) {
        console.error('No attendance data available');
        return;
    }
    
    // Line chart for daily attendance by meal type
    const dailyAttendanceDatasets = [
        {
            label: 'Breakfast',
            data: attendanceData.breakfast,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)'
        },
        {
            label: 'Lunch',
            data: attendanceData.lunch,
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)'
        },
        {
            label: 'Dinner',
            data: attendanceData.dinner,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)'
        }
    ];
    
    createMultiLineChart(
        'daily-attendance-chart',
        'Daily Student Attendance by Meal Type',
        attendanceData.dates,
        dailyAttendanceDatasets,
        'Number of Students'
    );
    
    // Bar chart for average attendance by day of week
    const dayAttendanceDatasets = [
        {
            label: 'Breakfast',
            data: attendanceData.avg_breakfast,
            backgroundColor: 'rgba(255, 99, 132, 0.7)',
            borderColor: 'rgba(255, 99, 132, 1)'
        },
        {
            label: 'Lunch',
            data: attendanceData.avg_lunch,
            backgroundColor: 'rgba(54, 162, 235, 0.7)',
            borderColor: 'rgba(54, 162, 235, 1)'
        },
        {
            label: 'Dinner',
            data: attendanceData.avg_dinner,
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
            borderColor: 'rgba(75, 192, 192, 1)'
        }
    ];
    
    createStackedBarChart(
        'day-attendance-chart',
        'Average Attendance by Day of Week',
        attendanceData.days,
        dayAttendanceDatasets,
        'Number of Students'
    );
}

/**
 * Initialize consumption charts
 * @param {Object} consumptionData - Object containing consumption data
 */
function initConsumptionCharts(consumptionData) {
    if (!consumptionData || !consumptionData.dates || consumptionData.dates.length === 0) {
        console.error('No consumption data available');
        return;
    }
    
    // Line chart for food prepared vs consumed
    const foodConsumptionDatasets = [
        {
            label: 'Food Prepared',
            data: consumptionData.prepared,
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)'
        },
        {
            label: 'Food Consumed',
            data: consumptionData.consumed,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)'
        },
        {
            label: 'Leftover Food',
            data: consumptionData.leftover,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)'
        }
    ];
    
    createMultiLineChart(
        'food-consumption-chart',
        'Food Prepared vs Consumed (Daily)',
        consumptionData.dates,
        foodConsumptionDatasets,
        'Quantity (kg)'
    );
    
    // Bar chart for leftover food by meal type
    const leftoverDatasets = [
        {
            label: 'Prepared',
            data: consumptionData.meal_prepared,
            backgroundColor: 'rgba(54, 162, 235, 0.7)',
            borderColor: 'rgba(54, 162, 235, 1)'
        },
        {
            label: 'Consumed',
            data: consumptionData.meal_consumed,
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
            borderColor: 'rgba(75, 192, 192, 1)'
        },
        {
            label: 'Leftover',
            data: consumptionData.meal_leftover,
            backgroundColor: 'rgba(255, 99, 132, 0.7)',
            borderColor: 'rgba(255, 99, 132, 1)'
        }
    ];
    
    createStackedBarChart(
        'meal-leftover-chart',
        'Food Quantities by Meal Type',
        consumptionData.meal_types,
        leftoverDatasets,
        'Quantity (kg)'
    );
    
    // Pie chart for total consumed vs leftover
    createPieChart(
        'total-consumption-chart',
        'Total Food Consumption vs Leftover',
        ['Consumed', 'Leftover'],
        [consumptionData.total_consumed, consumptionData.total_leftover]
    );
    
    // Heatmap for consumption efficiency
    if (consumptionData.heatmap_days && consumptionData.heatmap_data) {
        createHeatmap(
            'consumption-heatmap',
            'Consumption Efficiency by Day & Meal Type (%)',
            MEAL_TYPES,
            consumptionData.heatmap_days,
            consumptionData.heatmap_data
        );
    }
    
    // Horizontal bar charts for highest consumption and waste
    if (consumptionData.highest_consumed_meal) {
        createHorizontalBarChart(
            'highest-consumption-chart',
            'Meal with Highest Consumption',
            [consumptionData.highest_consumed_meal],
            [consumptionData.highest_consumed_value],
            'Quantity Consumed (kg)'
        );
    }
    
    if (consumptionData.highest_waste_meal) {
        createHorizontalBarChart(
            'highest-wastage-chart',
            'Meal with Highest Wastage',
            [consumptionData.highest_waste_meal],
            [consumptionData.highest_waste_value],
            'Quantity Wasted (kg)'
        );
    }
}

/**
 * Initialize prediction charts
 * @param {Object} predictionData - Object containing prediction data
 */
function initPredictionCharts(predictionData) {
    if (!predictionData || Object.keys(predictionData).length === 0) {
        console.error('No prediction data available');
        return;
    }
    
    // Line chart for actual vs predicted food demand
    if (predictionData.dates && predictionData.actual_ts && predictionData.predicted_ts) {
        const predictionDatasets = [
            {
                label: 'Actual Consumption',
                data: predictionData.actual_ts,
                borderColor: 'rgba(54, 162, 235, 1)',
                backgroundColor: 'rgba(54, 162, 235, 0.2)'
            },
            {
                label: 'Predicted Consumption',
                data: predictionData.predicted_ts,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)'
            }
        ];
        
        createMultiLineChart(
            'prediction-accuracy-chart',
            'Actual vs Predicted Food Demand',
            predictionData.dates,
            predictionDatasets,
            'Quantity (kg)'
        );
    }
    
    // Scatter plot for predicted vs actual
    if (predictionData.actual && predictionData.predicted) {
        createScatterPlot(
            'prediction-scatter-chart',
            'Predicted vs Actual Food Consumption',
            predictionData.predicted,
            predictionData.actual,
            'Predicted Consumption (kg)',
            'Actual Consumption (kg)'
        );
    }
    
    // Histogram for consumption rates
    if (predictionData.consumption_rate_bins && predictionData.consumption_rate_counts) {
        createHistogram(
            'consumption-histogram',
            'Distribution of Food Consumption Rates',
            predictionData.consumption_rate_bins,
            predictionData.consumption_rate_counts,
            'Consumption Rate (kg per student)',
            'Frequency'
        );
    }
    
    // Line chart for weekly trend
    if (predictionData.weeks && predictionData.weekly_counts) {
        const weeklyDataset = [
            {
                label: 'Weekly Attendance',
                data: predictionData.weekly_counts,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)'
            }
        ];
        
        createMultiLineChart(
            'attendance-trend-chart',
            'Weekly Attendance Trend',
            predictionData.weeks.map(w => `Week ${w}`),
            weeklyDataset,
            'Number of Students'
        );
    }
}