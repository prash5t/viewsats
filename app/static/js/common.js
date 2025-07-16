// API endpoints
const API = {
    HEALTH: '/api/health',
    REFRESH: '/api/refresh',
    SATELLITES: '/api/satellites',
    POSITIONS: '/api/satellites/positions'
};

// Utility functions
function formatDate(isoString) {
    return new Date(isoString).toLocaleString();
}

function handleApiError(error) {
    console.error('API Error:', error);
    // You could add more sophisticated error handling here
}

// Initialize refresh button
document.addEventListener('DOMContentLoaded', () => {
    const refreshButton = document.getElementById('refreshButton');
    if (refreshButton) {
        refreshButton.addEventListener('click', async () => {
            try {
                refreshButton.disabled = true;
                const response = await fetch(API.REFRESH, { method: 'POST' });
                const data = await response.json();
                
                if (data.status === 'completed') {
                    // Trigger any page-specific refresh handlers
                    if (window.onDataRefresh) {
                        window.onDataRefresh();
                    }
                }
            } catch (error) {
                handleApiError(error);
            } finally {
                refreshButton.disabled = false;
            }
        });
    }
}); 