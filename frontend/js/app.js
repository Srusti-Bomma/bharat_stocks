// Main Application JavaScript

// Theme Toggle
function initTheme() {
    const theme = localStorage.getItem('theme') || 'dark';
    document.body.className = theme === 'dark' ? 'dark-mode' : 'light-mode';
}

function toggleTheme() {
    const currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.body.className = newTheme === 'dark' ? 'dark-mode' : 'light-mode';
    localStorage.setItem('theme', newTheme);
}

// API Functions
function __getBase(){
    try {
        if (typeof window !== 'undefined' && window.API_URL) return window.API_URL;
    } catch(e) {}
    try {
        if (typeof API_URL !== 'undefined') return API_URL;
    } catch(e) {}
    try {
        const saved = (typeof localStorage !== 'undefined') ? localStorage.getItem('api_base_url') : null;
        if (saved) return saved;
    } catch(e) {}
    return 'http://localhost:8000';
}
async function fetchStockData(symbol) {
    try {
        const BASE = __getBase();
        const response = await fetch(`${BASE}/api/fetch-now?symbol=${symbol}`);
        if (!response.ok) throw new Error('Failed to fetch stock');
        return await response.json();
    } catch (error) {
        console.error('Error fetching stock:', error);
        return null;
    }
}

async function fetchMultipleStocks(symbols) {
    try {
        const symbolString = symbols.join(',');
        const BASE = __getBase();
        const response = await fetch(`${BASE}/api/live-data?symbols=${symbolString}`);
        if (!response.ok) throw new Error('Failed to fetch stocks');
        return await response.json();
    } catch (error) {
        console.error('Error fetching stocks:', error);
        return null;
    }
}

async function fetchTrendingStocks() {
    try {
        const BASE = __getBase();
        const response = await fetch(`${BASE}/api/trending`);
        if (!response.ok) throw new Error('Failed to fetch trending stocks');
        return await response.json();
    } catch (error) {
        console.error('Error fetching trending stocks:', error);
        return null;
    }
}

async function fetchMostActiveStocks() {
    try {
        const BASE = __getBase();
        const response = await fetch(`${BASE}/api/most-active`);
        if (!response.ok) throw new Error('Failed to fetch most active stocks');
        return await response.json();
    } catch (error) {
        console.error('Error fetching most active stocks:', error);
        return null;
    }
}

async function fetchNews() {
    try {
        const BASE = __getBase();
        const response = await fetch(`${BASE}/api/news`);
        if (!response.ok) throw new Error('Failed to fetch news');
        return await response.json();
    } catch (error) {
        console.error('Error fetching news:', error);
        return null;
    }
}

async function fetchIndianNews() {
    try {
        const BASE = __getBase();
        const response = await fetch(`${BASE}/api/news-indian`);
        if (!response.ok) throw new Error('Failed to fetch Indian news');
        return await response.json();
    } catch (error) {
        console.error('Error fetching Indian news:', error);
        return null;
    }
}

// Utility Functions
function formatPrice(price) {
    if (typeof price === 'string') price = parseFloat(price);
    return price ? `₹${price.toFixed(2)}` : 'N/A';
}

function formatPercent(percent) {
    if (typeof percent === 'string') percent = parseFloat(percent);
    return percent ? `${percent > 0 ? '+' : ''}${percent.toFixed(2)}%` : 'N/A';
}

function formatNumber(num) {
    if (typeof num === 'string') num = parseFloat(num);
    if (!num) return 'N/A';
    if (num >= 10000000) return `${(num / 10000000).toFixed(2)}Cr`;
    if (num >= 100000) return `${(num / 100000).toFixed(2)}L`;
    if (num >= 1000) return `${(num / 1000).toFixed(2)}K`;
    return num.toString();
}

function getChangeClass(value) {
    if (typeof value === 'string') value = parseFloat(value);
    return value > 0 ? 'text-green-500' : value < 0 ? 'text-red-500' : 'text-gray-400';
}

function getChangeIcon(value) {
    if (typeof value === 'string') value = parseFloat(value);
    if (value > 0) return '▲';
    if (value < 0) return '▼';
    return '━';
}

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="flex justify-center items-center py-12">
                <div class="spinner"></div>
            </div>
        `;
    }
}

// Show error message
function showErrorMessage(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="bg-red-500/20 border border-red-500 text-red-500 px-4 py-3 rounded-lg text-center">
                ${message}
            </div>
        `;
    }
}

// Show empty state
function showEmptyState(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center py-12 text-gray-400">
                <p class="text-xl mb-2">📊</p>
                <p>${message}</p>
            </div>
        `;
    }
}

// Time ago function
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    initTheme();
    try { if (typeof window.resolveApiBase === 'function') { await window.resolveApiBase(); } } catch(e) {}
});
