// assets/script.js

// This script adds additional interactivity to the Electra.AI dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Function to toggle the sidebar on mobile devices
    function setupMobileToggle() {
        // Check if we're on mobile
        if (window.innerWidth < 992) {
            // Create toggle button if it doesn't exist
            if (!document.getElementById('sidebar-toggle')) {
                const toggleBtn = document.createElement('button');
                toggleBtn.id = 'sidebar-toggle';
                toggleBtn.innerHTML = '☰ Controls';
                toggleBtn.className = 'sidebar-toggle-btn';
                
                // Add button to DOM
                const header = document.querySelector('.header');
                header.appendChild(toggleBtn);
                
                // Add event listener
                toggleBtn.addEventListener('click', function() {
                    const sidebar = document.querySelector('.sidebar');
                    sidebar.classList.toggle('sidebar-visible');
                });
            }
        }
    }
    
    // Function to enhance interactive elements
    function enhanceInteractivity() {
        // Add hover effects for buttons
        const buttons = document.querySelectorAll('.button');
        buttons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.05)';
                this.style.transition = 'transform 0.3s';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
            });
        });
        
        // Smooth scrolling for file list
        const fileLists = document.querySelectorAll('.file-list');
        fileLists.forEach(list => {
            list.style.scrollBehavior = 'smooth';
        });
    }
    
    // Function to handle theme changes
    function handleThemeChange() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('change', function() {
                const value = this.querySelector('input:checked').value;
                const mainContainer = document.getElementById('main-container');
                
                // Apply animation for smooth transition
                mainContainer.style.transition = 'background-color 0.5s, color 0.5s';
                
                // Remove any existing theme classes
                mainContainer.classList.remove('theme-dark', 'theme-light');
                
                // Add the selected theme class
                mainContainer.classList.add(`theme-${value}`);
            });
        }
    }
    
    // Function to enhance the visualization
    function enhanceVisualization() {
        // Find the graph container
        const graphContainer = document.getElementById('main-graph');
        if (graphContainer) {
            // Add fullscreen support
            graphContainer.addEventListener('dblclick', function() {
                if (!document.fullscreenElement) {
                    this.requestFullscreen().catch(err => {
                        console.error(`Error attempting to enable fullscreen: ${err.message}`);
                    });
                } else {
                    document.exitFullscreen();
                }
            });
            
            // Add tooltip informing about fullscreen
            const tooltip = document.createElement('div');
            tooltip.className = 'graph-tooltip';
            tooltip.innerHTML = 'Double-click to enter fullscreen';
            tooltip.style.position = 'absolute';
            tooltip.style.top = '10px';
            tooltip.style.right = '10px';
            tooltip.style.padding = '5px 10px';
            tooltip.style.borderRadius = '4px';
            tooltip.style.fontSize = '12px';
            tooltip.style.opacity = '0';
            tooltip.style.transition = 'opacity 0.3s';
            
            // Container needs position relative for absolute positioning of tooltip
            graphContainer.style.position = 'relative';
            graphContainer.appendChild(tooltip);
            
            // Show tooltip on hover
            graphContainer.addEventListener('mouseenter', function() {
                tooltip.style.opacity = '0.8';
            });
            
            graphContainer.addEventListener('mouseleave', function() {
                tooltip.style.opacity = '0';
            });
        }
    }
    
    // Initialize all enhancement functions
    setupMobileToggle();
    enhanceInteractivity();
    handleThemeChange();
    
    // Enhancement functions that need to wait for elements to be rendered
    // Use MutationObserver to detect when elements are added to the DOM
    const observer = new MutationObserver(function(mutations) {
        enhanceVisualization();
    });
    
    // Start observing the main container for changes
    const mainContainer = document.getElementById('main-container');
    if (mainContainer) {
        observer.observe(mainContainer, { childList: true, subtree: true });
    }
    
    // Handle window resize for responsive design
    window.addEventListener('resize', function() {
        setupMobileToggle();
    });
});