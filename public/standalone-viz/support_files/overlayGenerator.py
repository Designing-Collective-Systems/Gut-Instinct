from .jsUtils import escape_for_js, dict_to_js_object
from .variableDescriptions import VARIABLE_DESCRIPTIONS

def generate_overlay_js(variable1, variable2, dependentvar):
    """
    Generate JavaScript code to create information overlays for variables and study info.
    
    Args:
        variable1 (str): The name of the first variable (for coloring)
        variable2 (str): The name of the second variable (for shapes)
        dependentvar (str): The name of the dependent variable
    
    Returns:
        str: JavaScript code for creating information overlays
    """
    
    overlay_js = f"""
// Create information overlays
function createInfoOverlays() {{
  console.log("=== CREATING INFO OVERLAYS ===");
  
  // Get variable descriptions
  const variableDescriptions = {dict_to_js_object(VARIABLE_DESCRIPTIONS)};
  const sheetDescriptions = {dict_to_js_object({'Dataset S1.2': 'Primary demographic and clinical characteristics dataset containing patient baseline information, medical history, and socioeconomic factors collected at study enrollment'})};
  
  console.log("variableDescriptions loaded:", Object.keys(variableDescriptions).length);
  console.log("sheetDescriptions loaded:", Object.keys(sheetDescriptions).length);
  
  // Remove existing overlays
  const existingOverlays = document.querySelectorAll('.info-overlay');
  console.log("Removing existing overlays:", existingOverlays.length);
  existingOverlays.forEach(overlay => overlay.remove());
  
  try {{
    // Create overlay 1 - Variable 1 info
    console.log("Creating overlay 1 for variable:", {escape_for_js(variable1)});
    const overlay1 = document.createElement('div');
    overlay1.id = 'overlay1';
    overlay1.className = 'info-overlay';
    overlay1.style.cssText = `
      position: fixed !important;
      top: 340px !important;
      right: 20px !important;
      width: 300px !important;
      background: rgba(255, 255, 255, 0.95) !important;
      border: 2px solid #333 !important;
      border-radius: 8px !important;
      padding: 15px !important;
      z-index: 99999 !important;
      font-family: Arial, sans-serif !important;
      font-size: 14px !important;
    `;
    
    const var1Description = variableDescriptions[{escape_for_js(variable1)}] || 'No description available for this variable.';
    console.log("Variable1 description found:", var1Description);
    
    overlay1.innerHTML = `
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
        <span>Color Variable</span>
        <button onclick="toggleOverlay('overlay1')" style="background: none; border: 1px solid #ccc; border-radius: 3px; cursor: pointer; padding: 2px 6px; font-size: 12px; min-width: 20px;">−</button>
      </div>
      <div class="overlay-content">
        <div style="font-weight: bold; color: #0066cc; margin-bottom: 5px;">{escape_for_js(variable1)}</div>
        <div style="color: #555; margin-bottom: 15px;">${{var1Description}}</div>
      </div>
    `;
    
    // Create overlay 2 - Variable 2 info  
    console.log("Creating overlay 2 for variable:", {escape_for_js(variable2)});
    const overlay2 = document.createElement('div');
    overlay2.id = 'overlay2';
    overlay2.className = 'info-overlay';
    overlay2.style.cssText = `
      position: fixed !important;
      top: 500px !important;
      right: 20px !important;
      width: 300px !important;
      background: rgba(255, 255, 255, 0.95) !important;
      border: 2px solid #333 !important;
      border-radius: 8px !important;
      padding: 15px !important;
      z-index: 99999 !important;
      font-family: Arial, sans-serif !important;
      font-size: 14px !important;
    `;
    
    const var2Description = variableDescriptions[{escape_for_js(variable2)}] || 'No description available for this variable.';
    console.log("Variable2 description found:", var2Description);
    
    overlay2.innerHTML = `
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
        <span>Shape Variable</span>
        <button onclick="toggleOverlay('overlay2')" style="background: none; border: 1px solid #ccc; border-radius: 3px; cursor: pointer; padding: 2px 6px; font-size: 12px; min-width: 20px;">−</button>
      </div>
      <div class="overlay-content">
        <div style="font-weight: bold; color: #0066cc; margin-bottom: 5px;">{escape_for_js(variable2)}</div>
        <div style="color: #555; margin-bottom: 15px;">${{var2Description}}</div>
      </div>
    `;
    
    // Create overlay 3 - Sheet info
    const overlay3 = document.createElement('div');
    overlay3.id = 'overlay3';
    overlay3.className = 'info-overlay';
    overlay3.style.cssText = `
      position: fixed !important;
      top: 760px !important;
      right: 20px !important;
      width: 300px !important;
      background: rgba(255, 255, 255, 0.95) !important;
      border: 2px solid #333 !important;
      border-radius: 8px !important;
      padding: 15px !important;
      z-index: 99999 !important;
      font-family: Arial, sans-serif !important;
      font-size: 14px !important;
    `;
    
    const sheetDescription = 'Taxa level: this is the dependent variable';
    console.log("Sheet description found:", sheetDescription);
    
    overlay3.innerHTML = `
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
        <span>Taxa</span>
        <button onclick="toggleOverlay('overlay3')" style="background: none; border: 1px solid #ccc; border-radius: 3px; cursor: pointer; padding: 2px 6px; font-size: 12px; min-width: 20px;">−</button>
      </div>
      <div class="overlay-content">
        <div style="font-weight: bold; color: #0066cc; margin-bottom: 5px;">{escape_for_js(dependentvar)}</div>
        <div style="color: #555; margin-bottom: 15px;">${{sheetDescription}}</div>
      </div>
    `;

    // Create overlay 4 - Study info
    const overlay4 = document.createElement('div');
    overlay4.id = 'overlay4';
    overlay4.className = 'info-overlay';
    overlay4.style.cssText = `
      position: fixed !important;
      top: 960px !important;
      right: 20px !important;
      width: 300px !important;
      background: rgba(255, 255, 255, 0.95) !important;
      border: 2px solid #333 !important;
      border-radius: 8px !important;
      padding: 15px !important;
      z-index: 99999 !important;
      font-family: Arial, sans-serif !important;
      font-size: 14px !important;
    `;
    
    const overlay4Description = 'This was a cross-sectional observational study conducted from September 2015 to January 2019 across 7 international sites (San Francisco, Boston, New York, Pittsburgh, Buenos Aires, Edinburgh, and San Sebastián). 576 MS patients paired with 576 genetically unrelated household healthy controls. Participants had to cohabitate for at least 6 months. MS patients on treatments had to be stable on therapy for ≥3 months. Single time point data collection per participant. Basically, no experiments were done during the study and all the data collected serves as a guide to give context to the microbial composition of people.';
    console.log("Sheet description found:", overlay4Description);
    
    overlay4.innerHTML = `
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
        <span>Study Information</span>
        <button onclick="toggleOverlay('overlay4')" style="background: none; border: 1px solid #ccc; border-radius: 3px; cursor: pointer; padding: 2px 6px; font-size: 12px; min-width: 20px;">−</button>
      </div>
      <div class="overlay-content">
        <div style="color: #555; margin-bottom: 15px;">${{overlay4Description}}</div>
      </div>
    `;

    // Create overlay 5 - HEI2015 info
    const overlay5 = document.createElement('div');
    overlay5.id = 'overlay5';
    overlay5.className = 'info-overlay';
    overlay5.style.cssText = `
      position: fixed !important;
      top: 960px !important;
      right: 420px !important;
      width: 300px !important;
      background: rgba(255, 255, 255, 0.95) !important;
      border: 2px solid #333 !important;
      border-radius: 8px !important;
      padding: 15px !important;
      z-index: 99999 !important;
      font-family: Arial, sans-serif !important;
      font-size: 14px !important;
    `;
    
    const overlay5Description = 'The HEI2015 is the latest iteration of the Healthy Eating Index, a tool designed to measure diet quality—that is, how closely an eating pattern or mix of foods matches the Dietary Guidelines for Americans recommendations. HEI2015 is a total value of ADDSUG, FATTYACID, GREEN_AND_BEAN, TOTALDAIRY, TOTALFRUIT, TOTALVEG, TOTPROT, REFINEDGRAIN, WHOLEFRUIT, WHOLEGRAIN, SFA, SEAPLANT_PROT, SODIUM. https://www.nccor.org/wp-content/uploads/2023/05/HEI-2015-Factsheet.pdf';
    console.log("Sheet description found:", overlay5Description);
    
    overlay5.innerHTML = `
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
        <span>HEI2015 Information</span>
        <button onclick="toggleOverlay('overlay5')" style="background: none; border: 1px solid #ccc; border-radius: 3px; cursor: pointer; padding: 2px 6px; font-size: 12px; min-width: 20px;">−</button>
      </div>
      <div class="overlay-content">
        <div style="color: #555; margin-bottom: 15px;">${{overlay5Description}}</div>
      </div>
    `;

    // Create overlay 6 - FFQ info
    const overlay6 = document.createElement('div');
    overlay6.id = 'overlay6';
    overlay6.className = 'info-overlay';
    overlay6.style.cssText = `
      position: fixed !important;
      top: 360px !important;
      right: 420px !important;
      width: 300px !important;
      background: rgba(255, 255, 255, 0.95) !important;
      border: 2px solid #333 !important;
      border-radius: 8px !important;
      padding: 15px !important;
      z-index: 99999 !important;
      font-family: Arial, sans-serif !important;
      font-size: 14px !important;
    `;
    
    const overlay6Description = 'An FFQ, or Food Frequency Questionnaire, is a dietary assessment tool used to estimate an individuals usual food and beverage consumption patterns over a specific period, typically a few months to a year. It involves participants reporting how frequently they eat or drink various food items from a list provided on the questionnaire. https://biolincc.nhlbi.nih.gov/media/studies/framoffspring/Forms/Exam%203%20Food%20Frequency%20Questionnaire.pdf?link_time=2018-08-11_23:58:42.966309';
    console.log("Sheet description found:", overlay6Description);
    
    overlay6.innerHTML = `
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
        <span>FFQ Information</span>
        <button onclick="toggleOverlay('overlay6')" style="background: none; border: 1px solid #ccc; border-radius: 3px; cursor: pointer; padding: 2px 6px; font-size: 12px; min-width: 20px;">−</button>
      </div>
      <div class="overlay-content">
        <div style="color: #555; margin-bottom: 15px;">${{overlay6Description}}</div>
      </div>
    `;
    
    // Add overlays to document
    console.log("Adding overlays to document body");
    document.body.appendChild(overlay1);
    document.body.appendChild(overlay2);
    document.body.appendChild(overlay3);
    document.body.appendChild(overlay4);
    document.body.appendChild(overlay5);
    document.body.appendChild(overlay6);
    
    // Verify they were added
    const addedOverlays = document.querySelectorAll('.info-overlay');
    console.log("Overlays successfully added:", addedOverlays.length);
    
    console.log('Information overlays created successfully');
    
  }} catch (error) {{
    console.error("Error creating overlays:", error);
  }}
}}

// Add toggle functionality
window.toggleOverlay = function(overlayId) {{
  const overlay = document.getElementById(overlayId);
  const content = overlay.querySelector('.overlay-content');
  const button = overlay.querySelector('button');
  
  if (content.style.display === 'none') {{
    content.style.display = 'block';
    button.textContent = '−';
  }} else {{
    content.style.display = 'none';
    button.textContent = '+';
  }}
}};

// Create overlays when page loads
setTimeout(createInfoOverlays, 2000);

// Recreate overlays if they get removed by dynamic content
setInterval(function() {{
  if (document.querySelectorAll('.info-overlay').length < 6) {{
    createInfoOverlays();
  }}
}}, 5000);
"""
    
    return overlay_js