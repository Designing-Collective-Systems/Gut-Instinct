def generate_custom_color_js(safe_variable1):
    """
    Generate JavaScript code for Emperor color system compatibility and axis renaming.
    
    Args:
        safe_variable1 (str): The JavaScript-safe escaped variable1 name
    
    Returns:
        str: JavaScript code for Emperor customization
    """
    custom_js = f"""
setTimeout(function() {{
  console.log("Setting up color system compatibility...");
  
  // The key insight: Don't override Emperor's color system at all
  // Just make sure the UI interactions work properly
  
  // Ensure variable1 is selected initially
  if (ec.controllers && ec.controllers.color) {{
    var colorController = ec.controllers.color;
    var colorSelect = colorController.$select[0];
    
    for (var i = 0; i < colorSelect.options.length; i++) {{
      if (colorSelect.options[i].value === {safe_variable1}) {{
        if (colorSelect.selectedIndex !== i) {{
          colorSelect.selectedIndex = i;
          console.log('Auto-selected variable1 for coloring');
        }}
        break;
      }}
    }}
  }}
  
  // That's it! No overrides, no interference
  // Your custom colors from Python will show initially
  // And Emperor's UI will work normally for user changes
  
  console.log('Color system ready - your custom colors should be visible');
  console.log('Users can now change individual bin colors through the UI');
  
  // Axis renaming (unchanged)
  function renameAxisLabels() {{
    var allText = document.querySelectorAll('text');
    for (var i = 0; i < allText.length; i++) {{
      var text = allText[i].textContent || allText[i].innerText;
      if (text.match(/PC1/i)) allText[i].textContent = text.replace(/PC1/i, 'Axis 1');
      if (text.match(/PC2/i)) allText[i].textContent = text.replace(/PC2/i, 'Axis 2');
      if (text.match(/PC3/i)) allText[i].textContent = text.replace(/PC3/i, 'Axis 3');
    }}
  }}
  
  renameAxisLabels();
  var renameInterval = setInterval(renameAxisLabels, 500);
  setTimeout(function() {{ clearInterval(renameInterval); }}, 10000);
  
}}, 1000);
"""
    
    return custom_js