// Chart management and visualization functions

let sentimentChart;
let correlationChart;

function initializeCharts() {
    createSentimentChart();
    createCorrelationChart();
}

function createSentimentChart() {
    const ctx = document.getElementById('sentimentChart');
    if (!ctx) return;

    if (sentimentChart) {
        sentimentChart.destroy();
    }

    sentimentChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: sampleData.sentimentTimeline.labels,
            datasets: [{
                label: 'Sentiment Score',
                data: sampleData.sentimentTimeline.sentiment,
                borderColor: DASHBOARD_CONFIG.CHART_COLORS.PRIMARY,
                backgroundColor: DASHBOARD_CONFIG.CHART_COLORS.BACKGROUND,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: DASHBOARD_CONFIG.CHART_COLORS.PRIMARY,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: DASHBOARD_CONFIG.CHART_COLORS.PRIMARY,
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return `Sentiment: ${formatSentimentScore(context.parsed.y)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0,0,0,0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280',
                        callback: function(value) {
                            return formatSentimentScore(value);
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function createCorrelationChart() {
    const ctx = document.getElementById('correlationChart');
    if (!ctx) return;

    if (correlationChart) {
        correlationChart.destroy();
    }

    correlationChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: sampleData.sentimentTimeline.labels,
            datasets: [
                {
                    label: 'Sentiment',
                    data: sampleData.sentimentTimeline.sentiment,
                    backgroundColor: DASHBOARD_CONFIG.CHART_COLORS.PRIMARY + 'CC',
                    borderColor: DASHBOARD_CONFIG.CHART_COLORS.PRIMARY,
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false,
                },
                {
                    label: 'S&P 500 Return (%)',
                    data: sampleData.sentimentTimeline.sp500,
                    backgroundColor: DASHBOARD_CONFIG.CHART_COLORS.SECONDARY + 'CC',
                    borderColor: DASHBOARD_CONFIG.CHART_COLORS.SECONDARY,
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        color: '#374151'
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: DASHBOARD_CONFIG.CHART_COLORS.PRIMARY,
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const datasetLabel = context.dataset.label;
                            const value = context.parsed.y;
                            if (datasetLabel === 'Sentiment') {
                                return `${datasetLabel}: ${formatSentimentScore(value)}`;
                            } else {
                                return `${datasetLabel}: ${value.toFixed(2)}%`;
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#6b7280'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function updateSentimentChart(data) {
    if (!sentimentChart) return;

    sentimentChart.data.labels = data.labels;
    sentimentChart.data.datasets[0].data = data.sentiment;
    sentimentChart.update('active');
}

function updateCorrelationChart(data) {
    if (!correlationChart) return;

    correlationChart.data.labels = data.labels;
    correlationChart.data.datasets[0].data = data.sentiment;
    correlationChart.data.datasets[1].data = data.sp500;
    correlationChart.update('active');
}

function destroyCharts() {
    if (sentimentChart) {
        sentimentChart.destroy();
        sentimentChart = null;
    }
    if (correlationChart) {
        correlationChart.destroy();
        correlationChart = null;
    }
}

function resizeCharts() {
    if (sentimentChart) sentimentChart.resize();
    if (correlationChart) correlationChart.resize();
}

function processSentimentTimelineData(rawData) {
    return {
        labels: rawData.map(item => new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' })),
        sentiment: rawData.map(item => item.average_score),
        dates: rawData.map(item => item.date)
    };
}

function processCorrelationData(sentimentData, sp500Data) {
    const combined = [];

    sentimentData.forEach(sentiment => {
        const sp500Match = sp500Data.find(sp => sp.Date === sentiment.date);
        if (sp500Match) {
            combined.push({
                date: sentiment.date,
                sentiment: sentiment.average_score,
                sp500Return: sp500Match.Return * 100
            });
        }
    });

    return {
        labels: combined.map(item => new Date(item.date).toLocaleDateString('en-US', { weekday: 'short' })),
        sentiment: combined.map(item => item.sentiment),
        sp500: combined.map(item => item.sp500Return)
    };
}

function animateChartUpdate(chart) {
    chart.update('active');

    const canvas = chart.canvas;
    canvas.style.transition = 'opacity 0.3s ease';
    canvas.style.opacity = '0.7';

    setTimeout(() => {
        canvas.style.opacity = '1';
    }, 150);
}

window.chartFunctions = {
    initializeCharts,
    updateSentimentChart,
    updateCorrelationChart,
    destroyCharts,
    resizeCharts,
    processSentimentTimelineData,
    processCorrelationData,
    animateChartUpdate
};
