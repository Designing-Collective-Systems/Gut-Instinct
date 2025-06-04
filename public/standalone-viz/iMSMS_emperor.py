import pandas as pd
import numpy as np
from emperor import Emperor
from emperor.util import get_emperor_support_files_dir
from skbio.stats.ordination import pcoa
from scipy.spatial.distance import pdist, squareform
import os
import re
import sys

# Get command line arguments
if len(sys.argv) >= 3:
    variable1 = sys.argv[1]  # Will be used for coloring
    variable2 = sys.argv[2]  # Will be used for shapes
    print(f"Received variables: {variable1}, {variable2}")
else:
    # Default values if no arguments provided
    variable1 = "age"  # Default coloring variable
    variable2 = "height"  # Default shape variable
    print("No variables provided, using defaults")

# Define variable-specific bin counts
VARIABLE_BIN_COUNTS = {
    'ADDSUG':5,
    'administration':5,
    'age': 5,
    'Alcohol % of cals (%)': 4,
    'allergies':3,
    'allergy_specific': 286,
    'anxiety': 3,
    'asthma': 3,
    'B1, B2 (mg)': 5,
    'Beta-carotene (mcg)':5,
    'birth_method':3,
    'bmi': 4,
    'Bread, pasta, rice (1)':5,
    'breastfeeding': 3,
    'Calcium (mg)': 5,
    'Calories (Kcal)': 5,
    'Carbohydrate (g)': 5,
    'Carbohydrate (g) as % of cals': 5,
    'children_number': 5,
    'Cholestrol (mg)': 5,
    'csf_results': 4,
    'depression': 3,
    'diet_no_special_needs': 2,
    'diet_special_needs': 27,
    'Dietary Fiber(g)': 5,
    'disease': 2,
    'disease_course': 4,
    'disease_course_control': 4,
    'disease_duration': 6,
    'dmt': 3,
    'eating_disorder': 3,
    'eczema': 3,
    'edss': 5,
    'education': 6,
    'ethnicity': 4,
    'Fat (g)': 5,
    'Fat (g) as % of cals': 5,
    'FATTYACID': 5,
    'Folate (mcg)': 5,
    'Fruits, fruit juices (cups)': 4,
    'Good oils, in foods ("teaspoons")': 5,
    'GREEN_AND_BEAN': 5,
    'HEI2015_TOTAL_SCORE': 5,
    'height': 4,
    'household': 2,
    'Iron (mg)': 5,
    'Magnesium (mg)': 5,
    'manic_depression_bipolar': 3,
    'Meat, eggs, or beans (1)': 5,
    'Milk, cheese, yogurt (cups)': 5,
    'Monounsaturated fat (g)': 5,
    'ms_family': 3,
    'MSSS': 6,
    'Niacin (mg)': 5,
    'nsaids': 3,
    'nsaids_specifics': 264,
    'occupation': 623,
    'ocd': 3,
    'ocps_y_n': 3,
    'otc_meds': 3,
    'otc_number': 6,
    'pets': 3,
    'Polyunsaturated fat (g)': 5,
    'postpartum_depression': 3,
    'Potassium (mg)': 5,
    'probiotics': 3,
    'Protein (g)': 5,
    'Protein (g) as % of cals': 5,
    'recreational_drug': 3,
    'REFINEDGRAIN': 5,
    'relapse_number': 6,
    'roommates': 3,
    'rxmeds': 4,
    'rxmeds_number': 6,
    'Saturated fat (g)': 5,
    'Saturated fat (g) as % of cals': 5,
    'SEAPLANT_PROT': 5,
    'sex': 2,
    'SFA': 5,
    'site': 7,
    'smoke': 4,
    'SODIUM': 5,
    'Sodium (salt) (mg)': 5,
    'spms_year': 24,
    'Sweets % of cals (%)': 5,
    'TOTALDAIRY': 5,
    'TOTALFRUIT': 5,
    'TOTALVEG': 5,
    'TOTPROT': 5,
    'treated': 4,
    'treatment_status': 3,
    'treatments': 8,
    'treatments_control': 14,
    'type2diabetes': 3,
    'Vegetables group (cups)': 5,
    'Vitamdietpairsumin A (RAE)': 5,
    'Vitamin B6 (mg)': 5,
    'Vitamin C (mg)': 4,
    'vitamin D (IU)': 5,
    'Vitamin E (mg)': 5,
    'weight': 5,
    'weight_change': 3,
    'which_ocp': 45,
    'Whole grains (1)': 5,
    'WHOLEFRUIT': 5,
    'WHOLEGRAIN': 5,
    'without potatoes (cups)': 5,
    'year_of_onset': 53,
    'Zinc (mg)': 5
    # Add more variables and their desired bin counts as needed
}

# Get bin counts for our variables
variable1_bins = VARIABLE_BIN_COUNTS.get(variable1, 5)  # Default to 5 if not specified
variable2_bins = VARIABLE_BIN_COUNTS.get(variable2, 4)  # Default to 4 if not specified

# Example usage:
print(f"Processing with Variable 1 (coloring): {variable1} ({variable1_bins} bins)")
print(f"Processing with Variable 2 (shapes): {variable2} ({variable2_bins} bins)")

# Function to convert specified column to bins with specified number of bins
def convert_column_to_ranges(df, column_name, num_bins=4):
    if column_name not in df.columns:
        print(f"Warning: '{column_name}' column not found in data.")
        return df
    
    # Check if column is already converted to categories
    if df[column_name].dtype == 'object' or df[column_name].dtype.name.startswith('str'):
        print(f"Warning: '{column_name}' column is not numeric. Creating categorical bins.")
        
        # Get unique values and create artificial bins
        unique_values = df[column_name].dropna().unique()
        
        if len(unique_values) <= num_bins:
            # If we have fewer unique values than bins, use the values directly
            sorted_unique = sorted(unique_values)
            value_map = {val: str(val) for val in sorted_unique}  # Keep original values as strings
            df[column_name] = df[column_name].map(value_map)
        else:
            # Create artificial bins by splitting unique values into num_bins groups
            sorted_values = sorted(unique_values)
            splits = np.array_split(sorted_values, num_bins)
            
            # Create mapping from values to descriptive range labels
            value_map = {}
            for i, split in enumerate(splits):
                if len(split) == 1:
                    range_label = str(split[0])
                else:
                    range_label = f"{split[0]}-{split[-1]}"
                for val in split:
                    value_map[val] = range_label
            
            df[column_name] = df[column_name].map(value_map)
    else:
        # Original numeric processing - create actual value ranges
        min_val = df[column_name].min()
        max_val = df[column_name].max()
        range_steps = np.linspace(min_val, max_val, num_bins + 1)
        
        # Create descriptive range labels with actual values
        range_labels = []
        for i in range(len(range_steps) - 1):
            range_labels.append(f"{round(range_steps[i], 1)}-{round(range_steps[i + 1], 1)}")
        
        # Store original values for comparison
        original_values = df[column_name].copy()
        df[column_name] = np.nan
        
        for i in range(len(range_steps) - 1):
            mask = (original_values >= range_steps[i]) & (original_values < range_steps[i + 1])
            df.loc[mask, column_name] = range_labels[i]
        
        # Handle edge case for maximum value
        df.loc[original_values == max_val, column_name] = range_labels[-1]
    
    return df

# Function that converts integer columns to range values (for other columns)
def convert_to_ranges(df, num_bins=5, exclude_columns=None):
    if exclude_columns is None:
        exclude_columns = []
    
    def categorize_value(value, min_val, max_val, range_steps, range_labels):
        if pd.isna(value):
            return np.nan
        for i in range(len(range_steps) - 1):
            if range_steps[i] <= value < range_steps[i + 1]:
                return range_labels[i]
        return range_labels[-1]
    
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    # Exclude specified columns from automatic conversion
    numeric_columns = [col for col in numeric_columns if col not in exclude_columns]
    
    for col in numeric_columns:
        min_val = df[col].min()
        max_val = df[col].max()
        range_steps = np.linspace(min_val, max_val, num_bins + 1)
        range_labels = [f"{round(range_steps[i], 2)}-{round(range_steps[i + 1], 2)}" for i in range(len(range_steps) - 1)]
        df[col] = df[col].apply(categorize_value, args=(min_val, max_val, range_steps, range_labels))
    return df

# Load your data - Use absolute paths to find the dataset
# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Look for the dataset in the same directory as the script, or one level up
possible_dataset_locations = [
    os.path.join(script_dir, 'iMSMS_dataset'),
    os.path.join(script_dir, '..', 'iMSMS_dataset'),
    os.path.join(script_dir, '..', '..', 'iMSMS_dataset'),
    'iMSMS_dataset'  # Relative path (original)
]

dataset_dir = None
for location in possible_dataset_locations:
    test_file = os.path.join(location, 'Supplementary_Dataset_S1.xlsx')
    # print(f"Looking for dataset at: {test_file}")
    if os.path.exists(test_file):
        dataset_dir = location
        # print(f"Found dataset at: {dataset_dir}")
        break

if not dataset_dir:
    for location in possible_dataset_locations:
        print(f"  - {os.path.abspath(location)}")
    sys.exit(1)

S1_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S1.xlsx')
S2_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S2.xlsx')
S3_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S3.xlsx')
S6_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S6.xlsx')

sheet1_2 = pd.read_excel(S1_PATH, sheet_name='Dataset S1.2')
sheet2 = pd.read_excel(S2_PATH, sheet_name='Dataset S2')
sheet3 = pd.read_excel(S3_PATH, sheet_name='Dataset S3')
sheet6_class = pd.read_excel(S6_PATH, sheet_name='class')

# Merge the demographic data
demographic_data = (sheet1_2
                   .merge(sheet3, on='iMSMS_ID', how='inner')
                   .merge(sheet2, on='iMSMS_ID', how='inner')
                   )

# Convert variable1 (coloring variable) to its specified number of bins
demographic_data = convert_column_to_ranges(demographic_data, variable1, num_bins=variable1_bins)

# Convert variable2 (shape variable) to its specified number of bins
demographic_data = convert_column_to_ranges(demographic_data, variable2, num_bins=variable2_bins)

# Convert other numeric columns, excluding our target variables
demographic_data = convert_to_ranges(demographic_data, num_bins=5, exclude_columns=[variable1, variable2])

print(demographic_data)

sheet6_class = sheet6_class.merge(demographic_data[['iMSMS_ID']], on='iMSMS_ID', how='inner')
demographic_data = demographic_data.set_index('iMSMS_ID')
sheet6_class = sheet6_class.set_index('iMSMS_ID')

# Beta Diversity
bray_curtis = pdist(sheet6_class, metric='braycurtis')
bray_curtis_matrix = squareform(bray_curtis)
bray_curtis_df = pd.DataFrame(bray_curtis_matrix, index=sheet6_class.index, columns=sheet6_class.index)

# Prepare distance matrix
distance_matrix = bray_curtis_df.to_numpy()
distance_matrix = (distance_matrix + distance_matrix.T) / 2
np.fill_diagonal(distance_matrix, 0)

# Perform PCoA
pcoa_results = pcoa(distance_matrix)

# Fix sample IDs if needed
if isinstance(pcoa_results.samples, pd.DataFrame):
    pcoa_results.samples.index = demographic_data.index
else:
    pcoa_results.samples = pd.DataFrame(
        data=pcoa_results.samples,
        index=demographic_data.index
    )

# Define colors for variable1 (coloring variable) - ROBUST HANDLING
variable1_ranges = demographic_data[variable1].dropna().unique().tolist()
variable1_ranges.sort()  # Sort the ranges

# Define colors (expand color palette to handle more bins)
available_colors = [
    '#1f77b4',  # blue
    '#2ca02c',  # green
    '#ffff00',  # yellow
    '#ff7f0e',  # orange
    '#d62728',  # red
    '#9467bd',  # purple
    '#8c564b',  # brown
    '#e377c2',  # pink
    '#7f7f7f',  # gray
    '#bcbd22'   # olive
]

# Create custom color mapping based on actual number of ranges
custom_colors = {}
for i, range_val in enumerate(variable1_ranges):
    if i < len(available_colors):
        custom_colors[range_val] = available_colors[i]
    else:
        # If we have more ranges than colors, cycle through colors
        custom_colors[range_val] = available_colors[i % len(available_colors)]

print(f"Variable1 ({variable1}) ranges found: {variable1_ranges}")
print(f"Color mapping: {custom_colors}")

# Define shapes for variable2 (shape variable) - ROBUST HANDLING
variable2_ranges = demographic_data[variable2].dropna().unique().tolist()
variable2_ranges.sort()  # Sort the ranges

# Define shapes (expand shape palette to handle more bins)
available_shapes = [
    'Star',
    'Cylinder', 
    'Sphere',
    'Cone',
    'Diamond',        # Additional shapes if needed
    'Ring',
    'Icosahedron',
    'Square'
]

# Create custom shape mapping based on actual number of ranges
custom_shapes = {}
for i, range_val in enumerate(variable2_ranges):
    if i < len(available_shapes):
        custom_shapes[range_val] = available_shapes[i]
    else:
        # If we have more ranges than shapes, cycle through shapes
        custom_shapes[range_val] = available_shapes[i % len(available_shapes)]

print(f"Variable2 ({variable2}) ranges found: {variable2_ranges}")
print(f"Shape mapping: {custom_shapes}")

# Add a more aggressive approach to rename the axis labels
# First, attempt to rename in the decomposition data itself
if hasattr(pcoa_results, 'samples') and isinstance(pcoa_results.samples, pd.DataFrame):
    # Rename the column labels if they exist
    if pcoa_results.samples.columns.tolist():
        new_columns = []
        for col in pcoa_results.samples.columns:
            if 'PC1' in str(col) or 'pc1' in str(col).lower():
                new_columns.append('Axis 1')
            elif 'PC2' in str(col) or 'pc2' in str(col).lower():
                new_columns.append('Axis 2')
            elif 'PC3' in str(col) or 'pc3' in str(col).lower():
                new_columns.append('Axis 3')
            else:
                new_columns.append(col)
        pcoa_results.samples.columns = new_columns

# Create the Emperor visualization
viz = Emperor(pcoa_results, demographic_data, remote=get_emperor_support_files_dir())

# Use Emperor's color_by method to set the initial coloring (using variable1)
viz.color_by(variable1, custom_colors)

# Use Emperor's shape_by method to set the shapes by variable2
viz.shape_by(variable2, custom_shapes)

# Set other visualization options
viz.set_axes([0, 1, 2])  # Set axes to display (using indices 0, 1, 2 for pc1, pc2, pc3)

# Create dictionaries for scaling and opacity - ROBUST HANDLING
scale_dict = {var1_range: 1.0 for var1_range in variable1_ranges}
opacity_dict = {var1_range: 1.0 for var1_range in variable1_ranges}

# Set scaling and opacity
viz.scale_by(variable1, scale_dict)
viz.opacity_by(variable1, opacity_dict)

# Generate the base Emperor visualization HTML
emperor_html = viz.make_emperor(standalone=True)

# Create the direct shape override JavaScript (updated to use variable2)
# Convert the shape mapping to JavaScript format
js_shape_mapping = {}
for key, value in custom_shapes.items():
    js_shape_mapping[key] = value

shape_mapping_js = str(js_shape_mapping).replace("'", '"')

direct_shape_js = f"""// This script directly manipulates the THREE.js objects in Emperor
// Map of shape names to THREE.js geometry creation functions
const SHAPE_GEOMETRIES = {{
  'Cone': function() {{
    return new THREE.ConeGeometry(0.5, 1, 8);
  }},
  'Sphere': function() {{
    return new THREE.SphereGeometry(0.5, 16, 16);
  }},
  'Star': function() {{
    // Create a star shape
    const starShape = new THREE.Shape();
    const outerRadius = 0.5;
    const innerRadius = 0.2;
    const spikes = 5;
    
    for (let i = 0; i < spikes * 2; i++) {{
      const radius = i % 2 === 0 ? outerRadius : innerRadius;
      const angle = (Math.PI * 2 * i) / (spikes * 2);
      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;
      
      if (i === 0) {{
        starShape.moveTo(x, y);
      }} else {{
        starShape.lineTo(x, y);
      }}
    }}
    starShape.closePath();
    
    const extrudeSettings = {{
      depth: 0.2,
      bevelEnabled: false
    }};
    
    return new THREE.ExtrudeGeometry(starShape, extrudeSettings);
  }},
  'Cylinder': function() {{
    return new THREE.CylinderGeometry(0.4, 0.4, 0.8, 16);
  }},
  'Box': function() {{
    return new THREE.BoxGeometry(0.8, 0.8, 0.8);
  }},
  'Octahedron': function() {{
    return new THREE.OctahedronGeometry(0.5);
  }},
  'Tetrahedron': function() {{
    return new THREE.TetrahedronGeometry(0.6);
  }},
  'Torus': function() {{
    return new THREE.TorusGeometry(0.4, 0.2, 8, 16);
  }}
}};

// Function to directly replace geometries in THREE.js scene
function replaceGeometries() {{
  // Accessing Emperor's controller
  if (typeof empObj === 'undefined' || !empObj.sceneViews || !empObj.sceneViews[0]) {{
    console.log("Emperor or scene view not available yet");
    return false;
  }}
  
  const sceneView = empObj.sceneViews[0];
  const scene = sceneView.scene;
  const metadata = window.data.plot.metadata;
  const metadataHeaders = window.data.plot.metadata_headers;
  
  // Find {variable2} index in metadata
  let variable2Index = -1;
  for (let i = 0; i < metadataHeaders.length; i++) {{
    if (metadataHeaders[i] === '{variable2}') {{
      variable2Index = i;
      break;
    }}
  }}
  
  if (variable2Index === -1) {{
    console.log("{variable2} field not found in metadata");
    return false;
  }}
  
  // Create a map from sample ID to {variable2} value
  const sampleToVariable2 = {{}};
  for (const sampleId in metadata) {{
    if (metadata.hasOwnProperty(sampleId)) {{
      sampleToVariable2[sampleId] = metadata[sampleId][variable2Index];
    }}
  }}
  
  // Map {variable2} values to shape types - DYNAMIC MAPPING
  const variable2ToShape = {shape_mapping_js};
  
  // Go through all objects in the scene
  let pointsReplaced = false;
  
  try {{
    // First, try to replace THREE.Points with individual meshes
    for (let i = 0; i < scene.children.length; i++) {{
      const child = scene.children[i];
      
      if (child instanceof THREE.Points) {{
        console.log("Found points object:", child);
        
        // Get the positions from the points
        const positions = child.geometry.attributes.position.array;
        const colors = child.geometry.attributes.color.array;
        const count = child.geometry.attributes.position.count;
        
        // Create a parent object to hold our meshes
        const meshesParent = new THREE.Object3D();
        meshesParent.name = "CustomShapesContainer";
        
        // Get sample IDs if available
        let sampleIds = [];
        if (sceneView.decomp && sceneView.decomp.plottable && sceneView.decomp.plottable.sample_ids) {{
          sampleIds = sceneView.decomp.plottable.sample_ids;
        }}
        
        // Replace points with appropriate geometries
        for (let j = 0; j < count; j++) {{
          const x = positions[j * 3];
          const y = positions[j * 3 + 1];
          const z = positions[j * 3 + 2];
          
          const r = colors[j * 3];
          const g = colors[j * 3 + 1];
          const b = colors[j * 3 + 2];
          
          // Determine which shape to use based on sample ID and {variable2}
          let shapeName = 'Sphere'; // Default
          
          if (j < sampleIds.length) {{
            const sampleId = sampleIds[j];
            const variable2Value = sampleToVariable2[sampleId];
            
            if (variable2Value && variable2ToShape[variable2Value]) {{
              shapeName = variable2ToShape[variable2Value];
            }}
          }}
          
          // Create geometry based on shape type
          const geometryFunc = SHAPE_GEOMETRIES[shapeName];
          if (!geometryFunc) continue;
          
          const geometry = geometryFunc();
          const material = new THREE.MeshBasicMaterial({{
            color: new THREE.Color(r, g, b),
            transparent: true,
            opacity: 0.8
          }});
          
          const mesh = new THREE.Mesh(geometry, material);
          mesh.position.set(x, y, z);
          mesh.scale.set(0.3, 0.3, 0.3); // Adjust size as needed
          
          meshesParent.add(mesh);
        }}
        
        // Add the new meshes and remove (or hide) the original points
        scene.add(meshesParent);
        child.visible = false; // Hide instead of remove to preserve original data
        
        pointsReplaced = true;
        console.log(`Replaced ${{count}} points with custom geometries`);
      }}
    }}
    
    // Force a redraw
    if (sceneView.needsUpdate !== undefined) {{
      sceneView.needsUpdate = true;
    }}
    
    // Also try to trigger Emperor's render function
    if (empObj.drawFrame) {{
      empObj.drawFrame();
    }}
    
    return pointsReplaced;
  }} catch (e) {{
    console.error("Error replacing geometries:", e);
    return false;
  }}
}}

// Initialize after page load
document.addEventListener('DOMContentLoaded', function() {{
  console.log("Direct THREE.js shape override script loaded");
  
  // Wait for Emperor to fully initialize
  let attempts = 0;
  const maxAttempts = 20;
  
  function tryReplaceGeometries() {{
    attempts++;
    console.log(`Attempt ${{attempts}} to replace geometries`);
    
    const success = replaceGeometries();
    
    if (success) {{
      console.log("Successfully replaced geometries!");
    }} else if (attempts < maxAttempts) {{
      // Try again after a delay
      setTimeout(tryReplaceGeometries, 1000);
    }} else {{
      console.log(`Failed to replace geometries after ${{maxAttempts}} attempts`);
    }}
  }}
  
  // Start first attempt after 3 seconds to ensure Emperor is fully loaded
  setTimeout(tryReplaceGeometries, 3000);
}});
"""

# Also add standard JavaScript to select variable1 for coloring
custom_js = f"""
// Set the metadata field to '{variable1}' for coloring
setTimeout(function() {{
  // HANDLE COLORING BY {variable1.upper()}
  if (ec.controllers && ec.controllers.color) {{
    var colorController = ec.controllers.color;
    
    // First check if '{variable1}' is available in the dropdown
    var colorSelect = colorController.$select[0];
    var hasVariable1 = false;
    
    for (var i = 0; i < colorSelect.options.length; i++) {{
      if (colorSelect.options[i].value === '{variable1}') {{
        hasVariable1 = true;
        colorSelect.selectedIndex = i;
        
        // Trigger change event to apply the selection
        $(colorSelect).trigger('change');
        console.log('Auto-selected {variable1} for coloring');
        break;
      }}
    }}
    
    if (!hasVariable1) {{
      console.log('{variable1} category not found in available metadata');
    }}
  }}
  
  // RENAME AXIS LABELS
  function renameAxisLabels() {{
    // Method 1: Look for text elements in the SVG renderer
    var allText = document.querySelectorAll('text');
    for (var i = 0; i < allText.length; i++) {{
      var text = allText[i].textContent || allText[i].innerText;
      if (text.match(/PC1/i) || text.match(/PC 1/i)) {{
        allText[i].textContent = text.replace(/PC1/i, 'Axis 1').replace(/PC 1/i, 'Axis 1');
      }}
      if (text.match(/PC2/i) || text.match(/PC 2/i)) {{
        allText[i].textContent = text.replace(/PC2/i, 'Axis 2').replace(/PC 2/i, 'Axis 2');
      }}
      if (text.match(/PC3/i) || text.match(/PC 3/i)) {{
        allText[i].textContent = text.replace(/PC3/i, 'Axis 3').replace(/PC 3/i, 'Axis 3');
      }}
    }}
  }}
  
  // Run the axis renaming function repeatedly
  renameAxisLabels();
  
  var renameInterval = setInterval(renameAxisLabels, 500);
  
  // Stop trying after 10 seconds
  setTimeout(function() {{
    clearInterval(renameInterval);
  }}, 10000);
}}, 1000);
"""

# Look for the specific marker pattern in the HTML
marker_pattern = "/*__custom_on_ready_code__*/"
if marker_pattern in emperor_html:
    # Replace the marker with our custom JavaScript
    emperor_html = emperor_html.replace(marker_pattern, marker_pattern + "\n      " + custom_js)
else:
    # If the marker isn't found, find a suitable insertion point
    ready_function_end = "ec.ready = function () {"
    
    # Find the ec.ready function
    start_idx = emperor_html.find(ready_function_end)
    if start_idx != -1:
        # Insert our code after the opening brace of ec.ready
        insertion_idx = start_idx + len(ready_function_end)
        emperor_html = emperor_html[:insertion_idx] + "\n      " + custom_js + emperor_html[insertion_idx:]
    else:
        print("Warning: Could not find a suitable location to insert custom JavaScript.")

# Also perform more aggressive text replacement in the HTML
# This searches for any instances of PC1, PC2, PC3 with different capitalizations and spacings
def replace_pc_labels(html):
    # Define patterns and replacements with regex
    replacements = [
        (r'PC1(?!\d)', 'Axis 1'),
        (r'PC 1(?!\d)', 'Axis 1'),
        (r'pc1(?!\d)', 'Axis 1'),
        (r'Pc1(?!\d)', 'Axis 1'),
        (r'PC2(?!\d)', 'Axis 2'),
        (r'PC 2(?!\d)', 'Axis 2'),
        (r'pc2(?!\d)', 'Axis 2'),
        (r'Pc2(?!\d)', 'Axis 2'),
        (r'PC3(?!\d)', 'Axis 3'),
        (r'PC 3(?!\d)', 'Axis 3'),
        (r'pc3(?!\d)', 'Axis 3'),
        (r'Pc3(?!\d)', 'Axis 3'),
    ]
    
    import re
    modified = html
    for pattern, replacement in replacements:
        modified = re.sub(pattern, replacement, modified)
    
    return modified

# Apply the regex replacements
emperor_html = replace_pc_labels(emperor_html)

# Insert the direct shape manipulation script at the end of the HTML body
emperor_html = emperor_html.replace('</body>', f'<script type="text/javascript">{direct_shape_js}</script></body>')

# Convert absolute paths to relative paths
support_dir = get_emperor_support_files_dir()
if support_dir in emperor_html:
    emperor_html = emperor_html.replace(support_dir + '/', '')

# Ensure the output directory exists
# Save directly to the current directory (where the script is located)
# This will be public/standalone-viz/ in your Meteor app
output_path = "visualization.html"  # Changed filename to match expected

with open(output_path, 'w') as f:
    f.write(emperor_html)

print(f"Emperor visualization saved to {output_path}")
print(f"- {variable1} binned into {len(variable1_ranges)} categories with colors")
print(f"- {variable2} binned into {len(variable2_ranges)} categories with shapes")
print(f"- Using {variable1} for coloring and {variable2} for shapes")
print("- Variable-specific binning: each variable maintains its designated number of bins")
print("- Direct THREE.js manipulation for shapes included")
print("- Axes renamed from PC1, PC2, PC3 to Axis 1, Axis 2, Axis 3")
print("- Relative paths for better portability")
print("\nScript completed.")