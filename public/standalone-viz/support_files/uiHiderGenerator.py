def generate_precise_hide_js():
    """
    Generate JavaScript code to hide unwanted Emperor UI tabs while preserving 
    Color, Shape, and Visibility tabs, and hiding the settings button.
    
    Returns:
        str: JavaScript code for hiding UI elements
    """
    precise_hide_js = """
// Precise tab hiding that preserves Color, Shape, and Visibility + hides settings
function preciseHideUnwantedTabs() {
    console.log("Starting precise tab hiding (preserving Color, Shape, and Visibility, hiding settings)...");
    
    // Exact text matches to hide (case-sensitive) - REMOVED 'Visibility' from this list
    const exactTextsToHide = ['Opacity', 'Scale', 'Axes', 'Animations'];
    
    // Exact text matches to preserve (case-insensitive) - ADDED 'visibility' to preserve list
    const exactTextsToKeep = ['color', 'shape', 'visibility'];
    
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
    
    // Method 2: Hide specific content panels by ID, but preserve color, shape, and visibility - REMOVED visibility IDs
    const contentIdsToHide = [
        '#opacity-tab', '#scale-tab', '#axes-tab', '#animations-tab',
        '#opacity', '#scale', '#axes', '#animations'
    ];
    
    contentIdsToHide.forEach(id => {
        const element = document.querySelector(id);
        if (element) {
            element.style.display = 'none';
            hiddenCount++;
            console.log(`Hidden content by ID: ${id}`);
        }
    });
    
    // Method 3: Force show Color, Shape, and Visibility elements - ADDED visibility selectors
    const forceShowSelectors = [
        'a[href*="color"]', 'a[href*="shape"]', 'a[href*="visibility"]',
        'button[data-target*="color"]', 'button[data-target*="shape"]', 'button[data-target*="visibility"]',
        '[id*="color"]', '[id*="shape"]', '[id*="visibility"]',
        '[aria-controls*="color"]', '[aria-controls*="shape"]', '[aria-controls*="visibility"]'
    ];
    
    forceShowSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(element => {
            element.style.display = '';
            element.style.visibility = 'visible';
            console.log(`Force showing element:`, element);
        });
    });
    
    // Method 4: Hide the settings button (gear icon)
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
                // Don't hide if it's related to color, shape, or visibility
                const elementText = element.textContent.toLowerCase();
                if (!elementText.includes('color') && !elementText.includes('shape') && !elementText.includes('visibility')) {
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
        
        // Don't hide if it's related to color, shape, or visibility
        if (textContent.includes('color') || textContent.includes('shape') || textContent.includes('visibility')) {
            return;
        }
        
        // Check if it contains gear/settings related content
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
        ];
        
        if (hasSettingsIndicators.some(indicator => indicator)) {
            button.style.display = 'none';
            console.log('Hidden settings button by content:', button);
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
    Color, Shape, and Visibility controls.
    
    Returns:
        str: CSS code for hiding UI elements
    """
    precise_hide_css = """
<style>
/* Hide specific tab links by href patterns - but preserve color, shape, and visibility */
a[href*="opacity"]:not([href*="color"]):not([href*="shape"]):not([href*="visibility"]),
a[href*="scale"]:not([href*="color"]):not([href*="shape"]):not([href*="visibility"]),
a[href*="axes"]:not([href*="color"]):not([href*="shape"]):not([href*="visibility"]),
a[href*="animation"]:not([href*="color"]):not([href*="shape"]):not([href*="visibility"]) {
    display: none !important;
}

/* Hide specific content panels by ID - but preserve color, shape, and visibility */
[id="opacity-tab"], [id="scale-tab"],
[id="axes-tab"], [id="animations-tab"],
[id="opacity"], [id="scale"],
[id="axes"], [id="animations"] {
    display: none !important;
}

/* Hide by data-target attributes - but preserve color, shape, and visibility */
button[data-target*="opacity"]:not([data-target*="color"]):not([data-target*="shape"]):not([data-target*="visibility"]),
button[data-target*="scale"]:not([data-target*="color"]):not([data-target*="shape"]):not([data-target*="visibility"]),
button[data-target*="axes"]:not([data-target*="color"]):not([data-target*="shape"]):not([data-target*="visibility"]),
button[data-target*="animation"]:not([data-target*="color"]):not([data-target*="shape"]):not([data-target*="visibility"]) {
    display: none !important;
}

/* Hide settings button by common patterns */
.settings-btn, .gear-icon, .fa-gear, .fa-cog, .fa-settings,
button[title*="setting" i]:not([class*="color"]):not([class*="shape"]):not([class*="visibility"]),
button[aria-label*="setting" i]:not([class*="color"]):not([class*="shape"]):not([class*="visibility"]),
[data-toggle="modal"]:not([class*="color"]):not([class*="shape"]):not([class*="visibility"]),
.btn[data-target*="setting" i]:not([class*="color"]):not([class*="shape"]):not([class*="visibility"]) {
    display: none !important;
}

/* Hide toolbar buttons except essential ones */
.btn-toolbar button:not([class*="color"]):not([class*="shape"]):not([class*="visibility"]):not(.btn-primary) {
    display: none !important;
}

/* Force show Color, Shape, and Visibility elements */
a[href*="color"], a[href*="shape"], a[href*="visibility"],
button[data-target*="color"], button[data-target*="shape"], button[data-target*="visibility"],
[id*="color"], [id*="shape"], [id*="visibility"],
[aria-controls*="color"], [aria-controls*="shape"], [aria-controls*="visibility"] {
    display: block !important;
    visibility: visible !important;
}

/* Alternative: Hide by aria-controls but preserve color, shape, and visibility */
[aria-controls="opacity"],
[aria-controls="scale"], [aria-controls="axes"],
[aria-controls="animations"] {
    display: none !important;
}

/* Don't hide color, shape, and visibility controls */
[aria-controls*="color"], [aria-controls*="shape"], [aria-controls*="visibility"] {
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