// Configuration settings for the dashboard
const DASHBOARD_CONFIG = {
    // API endpoints - update these to match your backend
    API_BASE_URL: 'http://localhost:5000/api',
    ENDPOINTS: {
        SENTIMENT_SUMMARY: '/sentiment/summary',
        CORRELATION_DATA: '/correlation/data',
        NEWS_FEED: '/news/recent',
        SP500_DATA: '/sp500/returns',
        PERFORMANCE_METRICS: '/metrics/performance'
    },
    
    // MongoDB collection names (matching your phase1-3 setup)
    COLLECTIONS: {
        FINANCIAL_NEWS: 'financial_news',
        DAILY_SENTIMENT: 'daily_sentiment_summary',
        CORRELATION_INDEX: 'correlation_index',
        SP500_RETURNS: 'sp500_daily_returns',
        RETURN_SENTIMENT_MATCH: 'return_sentiment_match'
    },
    
    // Chart configuration
    CHART_COLORS: {
        PRIMARY: '#3b82f6',
        SECONDARY: '#dc2626',
        SUCCESS: '#10b981',
        WARNING: '#f59e0b',
        BACKGROUND: 'rgba(59, 130, 246, 0.1)'
    },
    
    // Update intervals (in milliseconds)
    UPDATE_INTERVALS: {
        REAL_TIME: 30000,    // 30 seconds
        METRICS: 60000,      // 1 minute
        NEWS_FEED: 120000    // 2 minutes
    },
    
    // Data refresh settings
    REFRESH_SETTINGS: {
        AUTO_REFRESH: true,
        REFRESH_ON_FOCUS: true,
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY: 5000
    },
    
    // Financial sources mapping (from your phase1 config)
    FINANCIAL_SOURCES: {
        'bloomberg.com': 'Bloomberg',
        'cnbc.com': 'CNBC',
        'reuters.com': 'Reuters',
        'marketwatch.com': 'MarketWatch',
        'wsj.com': 'Wall Street Journal',
        'ft.com': 'Financial Times',
        'forbes.com': 'Forbes',
        'investopedia.com': 'Investopedia',
        'financialpost.com': 'Financial Post'
    },
    
    // Sentiment scoring (matching your phase2 setup)
    SENTIMENT_SCORES: {
        'positive': 1,
        'neutral': 0,
        'negative': -1
    }
};

// Global variables for chart instances
let sentimentChart = null;
let correlationChart = null;

// Global state management
const DASHBOARD_STATE = {
    currentDateRange: 30,
    currentDataSource: 'all',
    isLoading: false,
    lastUpdate: null,
    connectionStatus: 'connected'
};