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
            
        // Create groups for land, graticule, and satellites
        this.graticuleGroup = this.svg.append('g');
        this.landGroup = this.svg.append('g');
        this.satelliteGroup = this.svg.append('g');
        
        // Add graticule
        const graticule = d3.geoGraticule();
        this.graticuleGroup.append('path')
            .datum(graticule)
            .attr('class', 'graticule')
            .attr('d', this.path)
            .style('fill', 'none')
            .style('stroke', '#ccc')
            .style('stroke-width', '0.2px');
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
        let isDragging = false;
        let dragStart = null;
        
        // Add drag behavior
        const drag = d3.drag()
            .on('start', (event) => {
                isDragging = true;
                dragStart = [event.x, event.y];
            })
            .on('drag', (event) => {
                if (dragStart) {
                    const rotation = this.projection.rotate();
                    const dx = event.x - dragStart[0];
                    const dy = event.y - dragStart[1];
                    rotation[0] += dx * 0.5;
                    rotation[1] -= dy * 0.5;
                    rotation[1] = Math.max(-90, Math.min(90, rotation[1]));
                    this.projection.rotate(rotation);
                    this.updateVisualization();
                    dragStart = [event.x, event.y];
                }
            })
            .on('end', () => {
                isDragging = false;
                dragStart = null;
            });
            
        this.svg.call(drag);
        
        const rotate = () => {
            if (!isDragging) {
                const now = d3.now();
                const diff = now - lastTime;
                lastTime = now;
                
                const rotation = this.projection.rotate();
                rotation[0] += rotationSpeed * diff / 50;
                
                this.projection.rotate(rotation);
                this.updateVisualization();
            }
            
            requestAnimationFrame(rotate);
        };
        
        rotate();
    }
    
    updateSatellites(satellites) {
        this.satellites = satellites;
        this.updateVisualization();
    }
    
    updateVisualization() {
        // Update land and graticule
        this.landGroup.selectAll('path').attr('d', this.path);
        this.graticuleGroup.selectAll('path').attr('d', this.path);
        
        // Update satellites
        const satelliteMarkers = this.satelliteGroup.selectAll('g')
            .data(this.satellites, d => d.norad_id);
            
        // Remove old satellites
        satelliteMarkers.exit().remove();
        
        // Add new satellites
        const newSatellites = satelliteMarkers.enter()
            .append('g')
            .attr('class', 'satellite');
            
        // Add satellite dots
        newSatellites.append('circle')
            .attr('r', 3)
            .style('fill', '#e74c3c')
            .style('stroke', '#fff')
            .style('stroke-width', '0.5px');
            
        // Add altitude rings
        newSatellites.append('circle')
            .attr('class', 'altitude-ring')
            .style('fill', 'none')
            .style('stroke', '#e74c3c')
            .style('stroke-width', '0.5px')
            .style('stroke-opacity', '0.3');
            
        // Update all satellites (new and existing)
        this.satelliteGroup.selectAll('g.satellite')
            .attr('transform', d => {
                const coords = this.projection([d.lon, d.lat]);
                return coords ? `translate(${coords})` : null;
            })
            .style('display', d => {
                const coords = this.projection([d.lon, d.lat]);
                return this.isVisible(coords) ? null : 'none';
            })
            .each((d, i, nodes) => {
                // Update altitude ring size based on altitude
                const altitudeScale = d.alt_km / 1000; // Scale factor for visualization
                d3.select(nodes[i])
                    .select('.altitude-ring')
                    .attr('r', 3 + altitudeScale);
            });
    }
    
    isVisible(coords) {
        if (!coords) return false;
        
        // Get the current rotation
        const rotation = this.projection.rotate();
        const [lon, lat] = [-rotation[0], -rotation[1]];
        
        // Calculate the great circle distance between the point and the center of the visible hemisphere
        const distance = d3.geoDistance([lon, lat], [coords[0], coords[1]]);
        
        // Point is visible if it's less than 90 degrees from the center of the visible hemisphere
        return distance <= Math.PI / 2;
    }
}

// Initialize visualization when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('earth-container');
    if (container) {
        window.earthVis = new EarthVisualization('earth-container');
    }
}); 