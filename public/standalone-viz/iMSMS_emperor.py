import pandas as pd
import numpy as np
from emperor import Emperor
from emperor.util import get_emperor_support_files_dir
from skbio.stats.ordination import pcoa
from scipy.spatial.distance import pdist, squareform
import os
import re
import sys
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import json

# Import variable definitions from external file
from support_files.variableDescriptions import (
    VARIABLE_BIN_COUNTS
)
from support_files.discreteChecker import is_discrete_variable
from support_files.rangeFinder import convert_column_to_ranges, sort_ranges_numerically
from support_files.ageRangeFinder import convert_age_to_life_stages, sort_age_categories
from support_files.dataLoader import load_imsms_data
from support_files.colorGenerator import generate_discrete_colors, generate_gradient_colors
from support_files.jsUtils import escape_for_js, dict_to_js_object
from support_files.threeJSGenerator import generate_direct_shape_js
from support_files.customColorGenerator import generate_custom_color_js
from support_files.uiHiderGenerator import generate_precise_hide_js, generate_precise_hide_css
from support_files.overlayGenerator import generate_overlay_js

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


# Get bin counts for our variables
variable1_bins = VARIABLE_BIN_COUNTS.get(variable1, 5)  # Default to 5 if not specified
variable2_bins = VARIABLE_BIN_COUNTS.get(variable2, 4)  # Default to 4 if not specified

# Example usage:
print(f"Processing with Variable 1 (coloring): {variable1} ({variable1_bins} bins)")
print(f"Processing with Variable 2 (shapes): {variable2} ({variable2_bins} bins)")


# Load the iMSMS dataset
demographic_data, sheet6_class, dependentvar = load_imsms_data()

# Store original data for discrete/continuous analysis before any processing
original_variable1_data = demographic_data[variable1].copy() if variable1 in demographic_data.columns else None
original_variable2_data = demographic_data[variable2].copy() if variable2 in demographic_data.columns else None


# Determine if variable1 should use discrete or continuous color scheme BEFORE binning
variable1_is_discrete = is_discrete_variable(variable1, original_variable1_data) if original_variable1_data is not None else True
variable2_is_discrete = is_discrete_variable(variable2, original_variable2_data) if original_variable2_data is not None else True


print(f"Variable1 ({variable1}) detected as: {'Discrete' if variable1_is_discrete else 'Continuous'}")
print(f"Original data type: {original_variable1_data.dtype if original_variable1_data is not None else 'Unknown'}")
print(f"Unique values in original data: {len(original_variable1_data.dropna().unique()) if original_variable1_data is not None else 'Unknown'}")

# Convert variable1 (coloring variable) to its specified number of bins OR life stages for age
if variable1 == 'age':
    demographic_data = convert_age_to_life_stages(demographic_data, variable1)
else:
    demographic_data = convert_column_to_ranges(demographic_data, variable1, num_bins=variable1_bins)

# Convert variable2 (shape variable) to its specified number of bins OR life stages for age
if variable2 == 'age':
    demographic_data = convert_age_to_life_stages(demographic_data, variable2)
else:
    demographic_data = convert_column_to_ranges(demographic_data, variable2, num_bins=variable2_bins)

# Convert other numeric columns, excluding our target variables
# demographic_data = convert_to_ranges(demographic_data, num_bins=5, exclude_columns=[variable1, variable2])

# print(demographic_data)

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

# Define colors for variable1 (coloring variable) - ADAPTIVE COLOR SCHEME
variable1_ranges = demographic_data[variable1].dropna().unique().tolist()
if variable1_is_discrete or variable1 == 'age':
    if variable1 == 'age':
        variable1_ranges = sort_age_categories(variable1_ranges, variable1)
        # print(variable1_ranges)
    else:
        variable1_ranges.sort()  # Simple alphabetical sort for other discrete variables
else:
    variable1_ranges = sort_ranges_numerically(variable1_ranges)  # Numeric sort for continuous


# Generate appropriate color scheme based on the original data analysis
if variable1_is_discrete:
    colors_list = generate_discrete_colors(len(variable1_ranges))
    color_scheme_type = "discrete"
else:
    colors_list = generate_gradient_colors(len(variable1_ranges))
    color_scheme_type = "gradient (YlOrRd)"


# Create custom color mapping
custom_colors = {}
for i, range_val in enumerate(variable1_ranges):
    custom_colors[range_val] = colors_list[i]

print(f"Variable1 ({variable1}) ranges found: {variable1_ranges}")
print(f"Color scheme: {color_scheme_type}")
print(f"Color mapping: {custom_colors}")

# Define shapes for variable2 (shape variable) - ROBUST HANDLING
variable2_ranges = demographic_data[variable2].dropna().unique().tolist()
if variable2_is_discrete or variable2 == 'age':
    if variable2 == 'age':
        variable2_ranges = sort_age_categories(variable2_ranges, variable2)
    else:
        variable2_ranges.sort()  # Simple alphabetical sort for other discrete variables
else:
    variable2_ranges = sort_ranges_numerically(variable2_ranges)  # Numeric sort for continuous

# Define shapes (expand shape palette to handle more bins)
available_shapes = [
    # 'Star',
    # 'Cylinder', 
    # 'Sphere',
    # 'Cone',
    # 'Diamond',        # Additional shapes if needed
    # 'Ring',
    # 'Icosahedron',
    # 'Square'

    'Star',
    'Star', 
    'Star',
    'Star',
    'Star',        # Additional shapes if needed
    'Star',
    'Star',
    'Star'
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


# Generate the base Emperor visualization HTML
emperor_html = viz.make_emperor(standalone=True)

# Create the direct shape override JavaScript (updated to use variable2)
# Convert the shape mapping to JavaScript format using safe escaping
shape_mapping_js = dict_to_js_object(custom_shapes)

# Safely escape variable names for JavaScript
safe_variable1 = escape_for_js(variable1)
safe_variable2 = escape_for_js(variable2)

# Generate the direct shape manipulation JavaScript
direct_shape_js = generate_direct_shape_js(safe_variable2, shape_mapping_js)

# Also add standard JavaScript to select variable1 for coloring
# Use safe escaping for custom_colors
custom_colors_js = dict_to_js_object(custom_colors)

# Generate the custom color Emperor JavaScript
custom_js = generate_custom_color_js(safe_variable1)

# Generate the precise UI hiding JavaScript
precise_hide_js = generate_precise_hide_js()

# Generate the precise UI hiding CSS
precise_hide_css = generate_precise_hide_css()

# Generate the information overlay JavaScript
overlay_js = generate_overlay_js(variable1, variable2, dependentvar)

# Combine the precise solution
complete_precise_solution = precise_hide_js

# Update your script with the precise solution
final_precise_custom_js = custom_js + "\n\n" + complete_precise_solution + "\n\n" + overlay_js

# Insert the precise CSS and JavaScript
emperor_html = emperor_html.replace('</head>', f'{precise_hide_css}</head>')

# Replace the JavaScript insertion
marker_pattern = "/*__custom_on_ready_code__*/"
if marker_pattern in emperor_html:
    emperor_html = emperor_html.replace(marker_pattern, marker_pattern + "\n      " + final_precise_custom_js)
else:
    ready_function_end = "ec.ready = function () {"
    start_idx = emperor_html.find(ready_function_end)
    if start_idx != -1:
        insertion_idx = start_idx + len(ready_function_end)
        emperor_html = emperor_html[:insertion_idx] + "\n      " + final_precise_custom_js + emperor_html[insertion_idx:]

print("Applied PRECISE tab hiding solution that preserves Color and Shape tabs AND hides settings button")
print("This version specifically avoids hiding Color and Shape tabs while hiding the settings gear icon")


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
print(f"- {variable1} binned into {len(variable1_ranges)} categories with {color_scheme_type} colors")
print(f"- {variable2} binned into {len(variable2_ranges)} categories with shapes")
print(f"- Using {variable1} for coloring and {variable2} for shapes")
print("- Variable-specific binning: each variable maintains its designated number of bins")
print("- Adaptive color scheme: discrete variables use distinct colors, continuous variables use YlOrRd gradient")
print("- Direct THREE.js manipulation for shapes included")
print("- Axes renamed from PC1, PC2, PC3 to Axis 1, Axis 2, Axis 3")
print("- Relative paths for better portability")
print("- Safe JavaScript escaping for special characters")
print("\nScript completed.")