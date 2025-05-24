// Data management and API functions

// Sample data - replace with actual API calls to your MongoDB
const sampleData = {
    sentimentTimeline: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        sentiment: [0.15, -0.08, 0.23, 0.31, -0.12, 0.19, 0.23],
        sp500: [0.8, -0.5, 1.2, 1.8, -0.7, 0.9, 1.1]
    },
    recentNews: [
        {
            title: "Fed Signals Potential Rate Cut Amid Economic Concerns",
            sentiment: "negative",
            source: "Reuters",
            time: "2 hours ago"
        },
        {
            title: "Tech Stocks Rally on Strong Earnings Reports",
            sentiment: "positive",
            source: "Bloomberg",
            time: "4 hours ago"
        },
        {
            title: "Market Volatility Expected to Continue",
            sentiment: "neutral",
            source: "CNBC",
            time: "6 hours ago"
        },
        {
            title: "Consumer Confidence Index Shows Improvement",
            sentiment: "positive",
            source: "WSJ",
            time: "8 hours ago"
        }
    ]
};

// API Helper Functions
async function makeAPIRequest(endpoint, options = {}) {
    try {
        DASHBOARD_STATE.isLoading = true;

        const response = await fetch(`${DASHBOARD_CONFIG.API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        DASHBOARD_STATE.connectionStatus = 'connected';
        return data;

    } catch (error) {
        console.error('API request failed:', error);
        DASHBOARD_STATE.connectionStatus = 'disconnected';
        throw error;
    } finally {
        DASHBOARD_STATE.isLoading = false;
    }
}

// Data fetching functions
async function fetchSentimentSummary(dateRange = 30, source = 'all') {
    try {
        // const data = await makeAPIRequest(`${DASHBOARD_CONFIG.ENDPOINTS.SENTIMENT_SUMMARY}?days=${dateRange}&source=${source}`);
        return {
            currentSentiment: 0.23,
            sentimentCounts: {
                positive: 142,
                neutral: 89,
                negative: 76
            },
            timeline: sampleData.sentimentTimeline
        };
    } catch (error) {
        console.error('Failed to fetch sentiment summary:', error);
        return null;
    }
}

async function fetchCorrelationData(dateRange = 30) {
    try {
        // const data = await makeAPIRequest(`${DASHBOARD_CONFIG.ENDPOINTS.CORRELATION_DATA}?days=${dateRange}`);
        return {
            correlationPercentage: 68,
            fearIndex: 34,
            matches: sampleData.sentimentTimeline
        };
    } catch (error) {
        console.error('Failed to fetch correlation data:', error);
        return null;
    }
}

async function fetchRecentNews(limit = 10, source = 'all') {
    try {
        // const data = await makeAPIRequest(`${DASHBOARD_CONFIG.ENDPOINTS.NEWS_FEED}?limit=${limit}&source=${source}`);
        return sampleData.recentNews;
    } catch (error) {
        console.error('Failed to fetch recent news:', error);
        return [];
    }
}

async function fetchPerformanceMetrics() {
    try {
        // const data = await makeAPIRequest(DASHBOARD_CONFIG.ENDPOINTS.PERFORMANCE_METRICS);
        return {
            articlesAnalyzed: 234,
            processingSpeed: '1.2s avg',
            activeSources: '7/9',
            lastUpdate: new Date().toLocaleTimeString()
        };
    } catch (error) {
        console.error('Failed to fetch performance metrics:', error);
        return null;
    }
}

// Data transformation utilities
function calculateFearIndex(sentimentData) {
    const avgSentiment = sentimentData.reduce((sum, val) => sum + val, 0) / sentimentData.length;
    return Math.max(0, Math.min(100, Math.round((1 - avgSentiment) * 50)));
}

function formatSentimentScore(score) {
    return score >= 0 ? `+${score.toFixed(2)}` : score.toFixed(2);
}

function formatTimeAgo(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInSeconds = Math.floor((now - time) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} min ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    return `${Math.floor(diffInSeconds / 86400)} days ago`;
}

// Real API functions (example structure, commented out)
/*
async function fetchSentimentFromMongoDB(dateRange) {
    const query = {
        method: 'POST',
        body: JSON.stringify({
            collection: DASHBOARD_CONFIG.COLLECTIONS.DAILY_SENTIMENT,
            pipeline: [
                {
                    $match: {
                        date: {
                            $gte: new Date(Date.now() - dateRange * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                        }
                    }
                },
                {
                    $sort: { date: 1 }
                }
            ]
        })
    };

    return await makeAPIRequest('/mongodb/aggregate', query);
}

async function fetchCorrelationFromMongoDB(dateRange) {
    const query = {
        method: 'POST',
        body: JSON.stringify({
            collection: DASHBOARD_CONFIG.COLLECTIONS.RETURN_SENTIMENT_MATCH,
            pipeline: [
                {
                    $match: {
                        date: {
                            $gte: new Date(Date.now() - dateRange * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
                        }
                    }
                },
                {
                    $group: {
                        _id: null,
                        totalMatches: { $sum: "$match" },
                        totalDays: { $sum: 1 },
                        avgCorrelation: { $avg: "$correlation_with_market" }
                    }
                }
            ]
        })
    };

    return await makeAPIRequest('/mongodb/aggregate', query);
}

async function fetchNewsFromMongoDB(limit, source) {
    const matchStage = source === 'all' ? {} : { source };

    const query = {
        method: 'POST',
        body: JSON.stringify({
            collection: DASHBOARD_CONFIG.COLLECTIONS.FINANCIAL_NEWS,
            pipeline: [
                { $match: { ...matchStage, sentiment: { $exists: true } } },
                { $sort: { publishedAt: -1 } },
                { $limit: limit },
                {
                    $project: {
                        title: 1,
                        sentiment: 1,
                        source: 1,
                        publishedAt: 1,
                        url: 1
                    }
                }
            ]
        })
    };

    return await makeAPIRequest('/mongodb/aggregate', query);
}
*/
