class EarthVisualization {
    constructor(containerId) {
        this.container = d3.select(`#${containerId}`);
        this.width = this.container.node().clientWidth;
        this.height = 500;
        this.projection = d3.geoOrthographic()
            .scale(this.height / 2.1)
            .translate([this.width / 2, this.height / 2]);
        
        this.path = d3.geoPath().projection(this.projection);
        this.satellites = [];
        
        this.initializeSvg();
        this.loadWorldData();
        this.setupRotation();
    }
    
    initializeSvg() {
        this.svg = this.container.append('svg')
            .attr('width', this.width)
            .attr('height', this.height);
            
        // Add water background
        this.svg.append('circle')
            .attr('cx', this.width / 2)
            .attr('cy', this.height / 2)
            .attr('r', this.projection.scale())
            .attr('class', 'ocean')
            .style('fill', '#a4d1e3');
            
        // Create groups for land and satellites
        this.landGroup = this.svg.append('g');
        this.satelliteGroup = this.svg.append('g');
    }
    
    async loadWorldData() {
        try {
            const response = await fetch('https://unpkg.com/world-atlas@2.0.2/countries-110m.json');
            const worldData = await response.json();
            const land = topojson.feature(worldData, worldData.objects.land);
            
            this.landGroup.selectAll('path')
                .data([land])
                .enter()
                .append('path')
                .attr('d', this.path)
                .style('fill', '#c6dabf')
                .style('stroke', '#999')
                .style('stroke-width', '0.5px');
                
        } catch (error) {
            console.error('Error loading world data:', error);
        }
    }
    
    setupRotation() {
        let rotationSpeed = 0.2;
        let lastTime = d3.now();
        
        const rotate = () => {
            const now = d3.now();
            const diff = now - lastTime;
            lastTime = now;
            
            const rotation = this.projection.rotate();
            rotation[0] += rotationSpeed * diff / 50;
            
            this.projection.rotate(rotation);
            this.updateVisualization();
            
            requestAnimationFrame(rotate);
        };
        
        rotate();
    }
    
    updateSatellites(satellites) {
        this.satellites = satellites;
        this.updateVisualization();
    }
    
    updateVisualization() {
        // Update land
        this.landGroup.selectAll('path').attr('d', this.path);
        
        // Update satellites
        const satelliteMarkers = this.satelliteGroup.selectAll('circle')
            .data(this.satellites, d => d.norad_id);
            
        // Remove old satellites
        satelliteMarkers.exit().remove();
        
        // Add new satellites
        satelliteMarkers.enter()
            .append('circle')
            .merge(satelliteMarkers)
            .attr('r', 3)
            .style('fill', '#e74c3c')
            .attr('transform', d => {
                const coords = this.projection([d.lon, d.lat]);
                return coords ? `translate(${coords})` : null;
            })
            .style('display', d => {
                const coords = this.projection([d.lon, d.lat]);
                return this.isVisible(coords) ? null : 'none';
            });
    }
    
    isVisible(coords) {
        if (!coords) return false;
        const [x, y] = coords;
        return x >= 0 && x <= this.width && y >= 0 && y <= this.height;
    }
}

// Initialize visualization when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('earth-container');
    if (container) {
        window.earthVis = new EarthVisualization('earth-container');
    }
}); 