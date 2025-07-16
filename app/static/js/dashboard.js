class DashboardManager {
    constructor() {
        this.satellites = [];
        this.filteredSatellites = [];
        this.updateInterval = 300000; // 5 minutes for satellite list
        this.positionInterval = 30000; // 30 seconds for position updates
        
        this.initializeElements();
        this.setupEventListeners();
        this.startPeriodicUpdates();
    }
    
    initializeElements() {
        this.searchInput = document.getElementById('searchInput');
        this.sortSelect = document.getElementById('sortSelect');
        this.satelliteList = document.getElementById('satelliteList');
        this.activeCount = document.getElementById('activeCount');
        this.lastUpdate = document.getElementById('lastUpdate');
    }
    
    setupEventListeners() {
        this.searchInput.addEventListener('input', () => this.filterSatellites());
        this.sortSelect.addEventListener('change', () => this.sortSatellites());
    }
    
    startPeriodicUpdates() {
        // Initial fetch
        this.fetchSatellites();
        
        // Set up periodic updates
        setInterval(() => this.fetchSatellites(), this.updateInterval);
        setInterval(() => this.updatePositions(), this.positionInterval);
    }
    
    async fetchSatellites() {
        try {
            const response = await fetch(API.SATELLITES);
            const data = await response.json();
            
            this.satellites = data.satellites;
            this.lastUpdate.textContent = formatDate(data.updated);
            this.activeCount.textContent = data.count;
            
            this.filterSatellites();
            this.updatePositions();
            
        } catch (error) {
            handleApiError(error);
        }
    }
    
    async updatePositions() {
        try {
            // Get positions for visible satellites
            const visibleIds = this.filteredSatellites
                .slice(0, 100) // Limit to prevent overloading
                .map(sat => sat.norad_id)
                .join(',');
                
            if (!visibleIds) return;
            
            const response = await fetch(`${API.POSITIONS}?norad_ids=${visibleIds}`);
            const data = await response.json();
            
            // Update Earth visualization with smooth transition
            if (window.earthVis) {
                window.earthVis.updateSatellites(data.positions);
            }
            
        } catch (error) {
            handleApiError(error);
        }
    }
    
    filterSatellites() {
        const searchTerm = this.searchInput.value.toLowerCase();
        
        this.filteredSatellites = this.satellites.filter(sat => 
            sat.name.toLowerCase().includes(searchTerm) ||
            sat.norad_id.toString().includes(searchTerm)
        );
        
        this.sortSatellites();
        this.renderSatelliteList();
    }
    
    sortSatellites() {
        const sortBy = this.sortSelect.value;
        
        this.filteredSatellites.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'norad':
                    return a.norad_id - b.norad_id;
                case 'updated':
                    return new Date(b.last_updated) - new Date(a.last_updated);
                default:
                    return 0;
            }
        });
        
        this.renderSatelliteList();
    }
    
    renderSatelliteList() {
        this.satelliteList.innerHTML = this.filteredSatellites
            .map(sat => `
                <div class="satellite-item">
                    <a href="/satellite/${sat.norad_id}" class="satellite-link">
                        <h3>${sat.name}</h3>
                        <div class="satellite-meta">
                            <span>NORAD ID: ${sat.norad_id}</span>
                            <span>Updated: ${formatDate(sat.last_updated)}</span>
                        </div>
                    </a>
                </div>
            `)
            .join('');
    }
}

// Initialize dashboard when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new DashboardManager();
    
    // Handle refresh button clicks
    window.onDataRefresh = () => {
        if (window.dashboard) {
            window.dashboard.fetchSatellites();
        }
    };
}); 