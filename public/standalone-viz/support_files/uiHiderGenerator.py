def generate_precise_hide_js():
    """
    Generate JavaScript code to hide unwanted Emperor UI tabs while preserving 
    Color and Visibility tabs, and hiding the settings button and axes control.
    
    Returns:
        str: JavaScript code for hiding UI elements
    """
    precise_hide_js = """
// Precise tab hiding that preserves Color and Visibility only, hides Axes and settings
function preciseHideUnwantedTabs() {
    console.log("Starting precise tab hiding (preserving Color and Visibility only, hiding Axes and settings)...");
    
    // Exact text matches to hide (case-sensitive) - ADDED 'Axes' to this list
    const exactTextsToHide = ['Opacity', 'Scale', 'Animations', 'Axes'];
    
    // Exact text matches to preserve (case-insensitive) - REMOVED 'axes' from preserve list
    const exactTextsToKeep = ['color', 'visibility'];
    
    let hiddenCount = 0;
    let keptCount = 0;
    
    // Method 1: Find tabs by exact text content and hide only unwanted ones
    const allClickableElements = document.querySelectorAll('a, button, [role="tab"], .nav-link');
    
    allClickableElements.forEach(element => {
        const elementText = element.textContent.trim();
        const elementTextLower = elementText.toLowerCase();
        
        // Check if this is a tab we want to keep
        const shouldKeep = exactTextsToKeep.some(keepText => 
            elementTextLower.includes(keepText)
        );
        
        if (shouldKeep) {
            // Force show this element
            element.style.display = '';
            element.style.visibility = 'visible';
            keptCount++;
            console.log(`KEEPING tab: "${elementText}"`);
            return; // Skip to next element
        }
        
        // Check if this is a tab we want to hide
        const shouldHide = exactTextsToHide.some(hideText => 
            elementText === hideText
        );
        
        if (shouldHide) {
            element.style.display = 'none';
            hiddenCount++;
            console.log(`HIDDEN tab: "${elementText}"`);
            
            // Hide associated content panel
            const target = element.getAttribute('href') || 
                         element.getAttribute('data-target') ||
                         element.getAttribute('aria-controls');
            
            if (target) {
                const targetElement = document.querySelector(target) || 
                                   document.getElementById(target.replace('#', ''));
                if (targetElement) {
                    targetElement.style.display = 'none';
                    console.log(`Hidden content panel: ${target}`);
                }
            }
        }
    });
    
    // Method 2: Hide specific content panels by ID, including axes
    const contentIdsToHide = [
        '#opacity-tab', '#scale-tab', '#animations-tab', '#axes-tab', '#tab-axes',
        '#opacity', '#scale', '#animations', '#axes'
    ];
    
    contentIdsToHide.forEach(id => {
        const element = document.querySelector(id);
        if (element) {
            element.style.display = 'none';
            hiddenCount++;
            console.log(`Hidden content by ID: ${id}`);
        }
    });
    
    // Method 3: Force show Color and Visibility elements only - REMOVED axes selectors
    const forceShowSelectors = [
        'a[href*="color"]', 'a[href*="visibility"]',
        'button[data-target*="color"]', 'button[data-target*="visibility"]',
        '[id*="color"]:not([id*="axes"])', '[id*="visibility"]:not([id*="axes"])',
        '[aria-controls*="color"]', '[aria-controls*="visibility"]'
    ];
    
    forceShowSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
            // Double check we're not showing axes-related elements
            const elementText = element.textContent.toLowerCase();
            const elementId = (element.id || '').toLowerCase();
            const elementHref = (element.getAttribute('href') || '').toLowerCase();
            
            if (!elementText.includes('axes') && !elementId.includes('axes') && !elementHref.includes('axes')) {
                element.style.display = '';
                element.style.visibility = 'visible';
                console.log(`Force showing element:`, element);
            }
        });
    });
    
    // Method 4: Specifically hide axes controls
    console.log("Hiding axes controls...");
    
    const axesSelectors = [
        'a[href*="axes"]', 'a[href="#tab-axes"]', 'a[href="#axes"]',
        'button[data-target*="axes"]', '[id*="axes"]', '[class*="axes"]',
        '[aria-controls*="axes"]', '.axes-tab', '#axes-tab', '#tab-axes'
    ];
    
    axesSelectors.forEach(selector => {
        try {
            document.querySelectorAll(selector).forEach(element => {
                element.style.display = 'none';
                console.log(`Hidden axes element by selector "${selector}":`, element);
                hiddenCount++;
                
                // Hide parent list item if it exists
                if (element.parentElement && element.parentElement.tagName === 'LI') {
                    element.parentElement.style.display = 'none';
                }
            });
        } catch (e) {
            // Some selectors might not work in all browsers, ignore errors
        }
    });
    
    // Method 5: Hide the settings button (gear icon)
    console.log("Hiding settings button...");
    
    // Common selectors for settings buttons
    const settingsSelectors = [
        '.settings-btn', '.gear-icon', '.fa-gear', '.fa-cog', '.fa-settings',
        'button[title*="setting"]', 'button[title*="Setting"]',
        'button[aria-label*="setting"]', 'button[aria-label*="Setting"]',
        '[data-toggle="modal"]', '.btn[data-target*="setting"]',
        '.btn[data-target*="Setting"]', '.navbar-btn', '.btn-toolbar button'
    ];
    
    settingsSelectors.forEach(selector => {
        try {
            document.querySelectorAll(selector).forEach(element => {
                // Don't hide if it's related to color or visibility
                const elementText = element.textContent.toLowerCase();
                if (!elementText.includes('color') && !elementText.includes('visibility')) {
                    element.style.display = 'none';
                    console.log(`Hidden settings element by selector "${selector}":`, element);
                    hiddenCount++;
                }
            });
        } catch (e) {
            // Some selectors might not work in all browsers, ignore errors
        }
    });
    
    // Hide by checking button content for gear/settings icons
    const allButtons = document.querySelectorAll('button, a, .btn');
    allButtons.forEach(button => {
        const innerHTML = button.innerHTML.toLowerCase();
        const title = (button.getAttribute('title') || '').toLowerCase();
        const ariaLabel = (button.getAttribute('aria-label') || '').toLowerCase();
        const textContent = button.textContent.toLowerCase();
        
        // Don't hide if it's related to color or visibility (but DO hide if axes-related)
        if ((textContent.includes('color') || textContent.includes('visibility')) && 
            !textContent.includes('axes')) {
            return;
        }
        
        // Check if it contains gear/settings related content OR axes content
        const hasSettingsIndicators = [
            innerHTML.includes('fa-gear'),
            innerHTML.includes('fa-cog'),
            innerHTML.includes('fa-setting'),
            innerHTML.includes('gear'),
            innerHTML.includes('setting'),
            title.includes('setting'),
            ariaLabel.includes('setting'),
            innerHTML.includes('⚙'), // gear Unicode symbol
            innerHTML.includes('🔧'), // wrench Unicode symbol
            textContent.includes('axes') // Also hide axes-related buttons
        ];
        
        if (hasSettingsIndicators.some(indicator => indicator)) {
            button.style.display = 'none';
            console.log('Hidden settings/axes button by content:', button);
            hiddenCount++;
        }
    });
    
    console.log(`Precise hiding completed. Hidden: ${hiddenCount}, Kept: ${keptCount}`);
    return hiddenCount;
}

// Run the precise hiding function
setTimeout(preciseHideUnwantedTabs, 1000);
setTimeout(preciseHideUnwantedTabs, 3000);
setTimeout(preciseHideUnwantedTabs, 5000);

// Monitor for dynamic content changes
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver((mutations) => {
        let shouldRun = false;
        mutations.forEach(mutation => {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                shouldRun = true;
            }
        });
        
        if (shouldRun) {
            setTimeout(preciseHideUnwantedTabs, 100);
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
}
"""
    
    return precise_hide_js

def generate_precise_hide_css():
    """
    Generate CSS code to hide unwanted Emperor UI elements while preserving 
    Color and Visibility controls only (hiding Axes).
    
    Returns:
        str: CSS code for hiding UI elements
    """
    precise_hide_css = """
<style>
/* Hide specific tab links by href patterns - preserve color and visibility only */
a[href*="opacity"]:not([href*="color"]):not([href*="visibility"]),
a[href*="scale"]:not([href*="color"]):not([href*="visibility"]),
a[href*="animation"]:not([href*="color"]):not([href*="visibility"]),
a[href*="axes"]:not([href*="color"]):not([href*="visibility"]) {
    display: none !important;
}

/* Hide specific content panels by ID - including axes */
[id="opacity-tab"], [id="scale-tab"], [id="animations-tab"], [id="axes-tab"], [id="tab-axes"],
[id="opacity"], [id="scale"], [id="animations"], [id="axes"] {
    display: none !important;
}

/* Hide by data-target attributes - preserve color and visibility only */
button[data-target*="opacity"]:not([data-target*="color"]):not([data-target*="visibility"]),
button[data-target*="scale"]:not([data-target*="color"]):not([data-target*="visibility"]),
button[data-target*="animation"]:not([data-target*="color"]):not([data-target*="visibility"]),
button[data-target*="axes"]:not([data-target*="color"]):not([data-target*="visibility"]) {
    display: none !important;
}

/* Specifically hide axes controls */
a[href="#tab-axes"],
a[href="#axes"],
a[href*="axes"],
button[data-target*="axes"],
[id*="axes"]:not([id*="color"]):not([id*="visibility"]),
[class*="axes"]:not([class*="color"]):not([class*="visibility"]),
[aria-controls*="axes"],
.axes-tab,
#axes-tab,
#tab-axes,
.tab-pane#tab-axes {
    display: none !important;
}

/* Hide parent list items of axes tabs */
li:has(a[href*="axes"]),
li:has(button[data-target*="axes"]) {
    display: none !important;
}

/* Hide settings button by common patterns */
.settings-btn, .gear-icon, .fa-gear, .fa-cog, .fa-settings,
button[title*="setting" i]:not([class*="color"]):not([class*="visibility"]),
button[aria-label*="setting" i]:not([class*="color"]):not([class*="visibility"]),
[data-toggle="modal"]:not([class*="color"]):not([class*="visibility"]),
.btn[data-target*="setting" i]:not([class*="color"]):not([class*="visibility"]) {
    display: none !important;
}

/* Hide toolbar buttons except essential ones */
.btn-toolbar button:not([class*="color"]):not([class*="visibility"]):not(.btn-primary) {
    display: none !important;
}

/* Force show Color and Visibility elements only */
a[href*="color"]:not([href*="axes"]), a[href*="visibility"]:not([href*="axes"]),
button[data-target*="color"]:not([data-target*="axes"]), button[data-target*="visibility"]:not([data-target*="axes"]),
[id*="color"]:not([id*="axes"]), [id*="visibility"]:not([id*="axes"]),
[aria-controls*="color"]:not([aria-controls*="axes"]), [aria-controls*="visibility"]:not([aria-controls*="axes"]) {
    display: block !important;
    visibility: visible !important;
}

/* Hide by aria-controls including axes */
[aria-controls="opacity"], [aria-controls="scale"], [aria-controls="animations"], [aria-controls="axes"] {
    display: none !important;
}

/* Force show only color and visibility controls */
[aria-controls*="color"]:not([aria-controls*="axes"]), [aria-controls*="visibility"]:not([aria-controls*="axes"]) {
    display: block !important;
    visibility: visible !important;
}

/* Overlay styles */
.info-overlay {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 300px;
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #333;
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    font-family: Arial, sans-serif;
    font-size: 14px;
    line-height: 1.4;
    z-index: 10000;
    max-height: 400px;
    overflow-y: auto;
}

.overlay-title {
    font-weight: bold;
    font-size: 16px;
    margin-bottom: 10px;
    color: #333;
    border-bottom: 1px solid #ccc;
    padding-bottom: 5px;
}

.overlay-variable {
    font-weight: bold;
    color: #0066cc;
    margin-bottom: 5px;
}

.overlay-description {
    color: #555;
    margin-bottom: 15px;
}

#overlay1 { top: 20px; }
#overlay2 { top: 160px; }
#overlay3 { top: 300px; }
</style>
"""
    
    return precise_hide_css