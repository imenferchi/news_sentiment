// Main dashboard functionality and event management

// Dashboard initialization
document.addEventListener('DOMContentLoaded', function () {
    initializeDashboard();
});

async function initializeDashboard() {
    try {
        initializeCharts();
        await loadDashboardData();
        setupEventListeners();

        if (DASHBOARD_CONFIG.REFRESH_SETTINGS.AUTO_REFRESH) {
            startAutoRefresh();
        }

        if (DASHBOARD_CONFIG.REFRESH_SETTINGS.REFRESH_ON_FOCUS) {
            setupVisibilityHandler();
        }

        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        showErrorMessage('Failed to initialize dashboard. Please refresh the page.');
    }
}

// Data loading and updates
async function loadDashboardData() {
    try {
        showLoadingState(true);

        const [sentimentData, correlationData, newsData, performanceData] = await Promise.all([
            fetchSentimentSummary(DASHBOARD_STATE.currentDateRange, DASHBOARD_STATE.currentDataSource),
            fetchCorrelationData(DASHBOARD_STATE.currentDateRange),
            fetchRecentNews(10, DASHBOARD_STATE.currentDataSource),
            fetchPerformanceMetrics()
        ]);

        updateMetricCards(sentimentData, correlationData, performanceData);
        updateSentimentDistribution(sentimentData);
        updateCharts(sentimentData, correlationData);
        updateNewsFeed(newsData);

        DASHBOARD_STATE.lastUpdate = new Date();
        updateLastUpdateDisplay();
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        showErrorMessage('Failed to load data. Retrying...');
        setTimeout(loadDashboardData, DASHBOARD_CONFIG.REFRESH_SETTINGS.RETRY_DELAY);
    } finally {
        showLoadingState(false);
    }
}

// UI Update Functions
function updateMetricCards(sentimentData, correlationData, performanceData) {
    const currentSentimentEl = document.getElementById('currentSentiment');
    if (currentSentimentEl && sentimentData) {
        currentSentimentEl.textContent = formatSentimentScore(sentimentData.currentSentiment);
    }

    const fearIndexEl = document.getElementById('fearIndex');
    if (fearIndexEl && correlationData) {
        fearIndexEl.textContent = correlationData.fearIndex;
        updateFearIndexLabel(correlationData.fearIndex);
    }

    const correlationValueEl = document.getElementById('correlationValue');
    if (correlationValueEl && correlationData) {
        correlationValueEl.textContent = `${correlationData.correlationPercentage}%`;
    }

    if (performanceData) {
        updatePerformanceMetrics(performanceData);
    }
}

function updateSentimentDistribution(sentimentData) {
    if (!sentimentData || !sentimentData.sentimentCounts) return;

    const counts = sentimentData.sentimentCounts;
    document.getElementById('positiveCount').textContent = counts.positive;
    document.getElementById('neutralCount').textContent = counts.neutral;
    document.getElementById('negativeCount').textContent = counts.negative;
}

function updateCharts(sentimentData, correlationData) {
    if (sentimentData?.timeline) {
        updateSentimentChart(sentimentData.timeline);
        updateCorrelationChart(sentimentData.timeline);
    }
}

function updateNewsFeed(newsData) {
    const newsFeed = document.getElementById('newsFeed');
    if (!newsFeed || !newsData) return;

    newsFeed.innerHTML = '';
    newsData.forEach(news => {
        const newsItem = createNewsItem(news);
        newsFeed.appendChild(newsItem);
    });
}

function createNewsItem(news) {
    const newsItem = document.createElement('div');
    newsItem.className = 'news-item';

    newsItem.innerHTML = `
        <div class="news-title">${news.title}</div>
        <div class="news-meta">
            <span>${news.source} • ${news.time}</span>
            <span class="sentiment-badge ${news.sentiment}">${news.sentiment.toUpperCase()}</span>
        </div>
    `;

    newsItem.addEventListener('click', () => {
        if (news.url) {
            window.open(news.url, '_blank');
        }
    });

    return newsItem;
}

function updatePerformanceMetrics(performanceData) {
    const metrics = {
        'articlesAnalyzed': performanceData.articlesAnalyzed,
        'processingSpeed': performanceData.processingSpeed,
        'activeSources': performanceData.activeSources,
        'lastUpdate': performanceData.lastUpdate
    };

    Object.entries(metrics).forEach(([key, value]) => {
        const element = document.getElementById(key);
        if (element) {
            element.textContent = value;
        }
    });
}

function updateFearIndexLabel(fearIndex) {
    const labelEl = document.querySelector('.fear-index .metric-label');
    if (!labelEl) return;

    let label = 'Moderate Fear';
    if (fearIndex < 20) label = 'Extreme Greed';
    else if (fearIndex < 40) label = 'Greed';
    else if (fearIndex < 60) label = 'Moderate Fear';
    else if (fearIndex < 80) label = 'Fear';
    else label = 'Extreme Fear';

    labelEl.textContent = label;
}

function updateLastUpdateDisplay() {
    const lastUpdateEl = document.getElementById('lastUpdate');
    if (lastUpdateEl && DASHBOARD_STATE.lastUpdate) {
        lastUpdateEl.textContent = formatTimeAgo(DASHBOARD_STATE.lastUpdate);
    }
}

// Event Listeners
function setupEventListeners() {
    const dateRangeSelect = document.getElementById('dateRange');
    if (dateRangeSelect) {
        dateRangeSelect.addEventListener('change', handleDateRangeChange);
    }

    const dataSourceSelect = document.getElementById('dataSource');
    if (dataSourceSelect) {
        dataSourceSelect.addEventListener('change', handleDataSourceChange);
    }

    document.querySelectorAll('.metric-card').forEach(card => {
        card.addEventListener('click', handleMetricCardClick);
    });

    window.addEventListener('resize', resizeCharts);
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Event Handlers
async function handleDateRangeChange(event) {
    DASHBOARD_STATE.currentDateRange = parseInt(event.target.value);
    console.log(`Date range changed to: ${DASHBOARD_STATE.currentDateRange} days`);
    await loadDashboardData();
}

async function handleDataSourceChange(event) {
    DASHBOARD_STATE.currentDataSource = event.target.value;
    console.log(`Data source changed to: ${DASHBOARD_STATE.currentDataSource}`);
    await loadDashboardData();
}

function handleMetricCardClick(event) {
    const cardTitle = event.currentTarget.querySelector('h3').textContent;
    console.log(`Metric card clicked: ${cardTitle}`);
}

function handleKeyboardShortcuts(event) {
    if (event.key === 'r' && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        refreshData();
    }

    if (event.key === 'f' && event.altKey) {
        event.preventDefault();
        console.log('Fullscreen chart view (not implemented yet)');
    }
}

// Refresh functionality
async function refreshData() {
    console.log('Refreshing data...');
    const refreshBtn = document.querySelector('.btn');
    if (refreshBtn) {
        const originalText = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '🔄 Refreshing...';
        refreshBtn.disabled = true;

        try {
            await loadDashboardData();
        } finally {
            setTimeout(() => {
                refreshBtn.innerHTML = originalText;
                refreshBtn.disabled = false;
            }, 1000);
        }
    } else {
        await loadDashboardData();
    }
}

// Auto-refresh functionality
function startAutoRefresh() {
    setInterval(async () => {
        if (!DASHBOARD_STATE.isLoading && document.visibilityState === 'visible') {
            try {
                const performanceData = await fetchPerformanceMetrics();
                if (performanceData) {
                    updatePerformanceMetrics(performanceData);
                    updateLastUpdateDisplay();
                }
            } catch (error) {
                console.error('Auto-refresh failed:', error);
            }
        }
    }, DASHBOARD_CONFIG.UPDATE_INTERVALS.REAL_TIME);

    setInterval(async () => {
        if (!DASHBOARD_STATE.isLoading && document.visibilityState === 'visible') {
            await loadDashboardData();
        }
    }, DASHBOARD_CONFIG.UPDATE_INTERVALS.METRICS);
}

// Visibility change handler
function setupVisibilityHandler() {
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && DASHBOARD_STATE.lastUpdate) {
            const timeSinceUpdate = Date.now() - DASHBOARD_STATE.lastUpdate.getTime();
            if (timeSinceUpdate > 5 * 60 * 1000) {
                loadDashboardData();
            }
        }
    });
}

// Utility functions
function showLoadingState(isLoading) {
    const statusIndicator = document.querySelector('.status-indicator');
    if (statusIndicator) {
        statusIndicator.className = `status-indicator ${isLoading ? 'status-loading' : 'status-connected'}`;
    }
}

function showErrorMessage(message) {
    console.error(message);
    const statusIndicator = document.querySelector('.status-indicator');
    if (statusIndicator) {
        statusIndicator.className = 'status-indicator status-disconnected';
    }
}

function updateConnectionStatus(status) {
    DASHBOARD_STATE.connectionStatus = status;

    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = statusIndicator?.nextElementSibling;

    if (statusIndicator && statusText) {
        statusIndicator.className = `status-indicator status-${status}`;
        statusText.textContent = status === 'connected' ? 'Connected to MongoDB' : 'Connection Issues';
    }
}

// Export main functions
window.dashboardAPI = {
    refreshData,
    loadDashboardData,
    updateConnectionStatus,
    DASHBOARD_STATE,
    DASHBOARD_CONFIG
};
