import pandas as pd
import numpy as np
from emperor import Emperor
from emperor.util import get_emperor_support_files_dir
from skbio.stats.ordination import pcoa
from scipy.spatial.distance import pdist, squareform
import sys

from support_files.discreteChecker import is_discrete_variable
from support_files.ageRangeFinder import convert_age_to_life_stages
from support_files.dataLoader import load_imsms_data
from support_files.colorGenerator import generate_discrete_colors, generate_gradient_colors
from support_files.jsUtils import escape_for_js, dict_to_js_object
from support_files.threeJSGenerator import generate_direct_shape_js
from support_files.customColorGenerator import generate_custom_color_js
from support_files.uiHiderGenerator import generate_precise_hide_js, generate_precise_hide_css
from support_files.overlayGenerator import generate_overlay_js
from support_files.fivePointHEIRangeFinder import convert_five_point_HEI_to_grades
from support_files.tenPointHEIRangeFinder import convert_ten_point_HEI_to_grades
from support_files.HEIRangeFinder import convert_HEI_score_to_grades
from support_files.bmiRangeFinder import classify_bmi
from support_files.yearOfOnsetRangeFinder import classify_yearOfOnset
from support_files.weightConverter import convert_weightKG_to_WeightLbs
from support_files.heightConverter import convert_heightCM_to_HeightInches
from support_files.durationOfMSRangeFinder import classify_durationOfMS
from support_files.administrationRangeFinder import classify_administration
from support_files.typeOfMSRangeFinder import classify_typeOfMS
from support_files.treatmentStatusRangeFinder import classify_treatmentStatus
from support_files.treatmentsAppliedRangeFinder import classify_treatmentsApplied
from support_files.binaryToYesNoRangeConverter import classify_binary
from support_files.specificNeedInDietRangeConverter import classify_diet
from support_files.SPMSyearOfOnsetRangeFinder import classify_yearOfSPMSOnset
from support_files.edssRangeFinder import classify_EDSS
from support_files.residenceRangeFinder import classify_residence
from support_files.ethnicityRangeFinder import classify_ethnicity
from support_files.sexRangeFinder import classify_sex
from support_files.diseaseRangeFinder import classify_disease
from support_files.msssRangeFinder import classify_MSSS
from support_files.trinarytoYesNoNullRangeFinder import classify_trinary
from support_files.numberOfChildrenRangeFinder import classify_numberOfChildren
from support_files.numberOfRoommatesRangeFinder import classify_roommates
from support_files.methodOfBirthRangeFinder import classify_methodOfBirth
from support_files.allergyRangeFinder import classify_allergy
from support_files.specificOCPRangeFinder import classify_oral_contraceptive
from support_files.nsaidsRangeFinder import classify_nsaid
from support_files.trinaryToNoNullYesRangeFinder import classify_trinary_2
from support_files.differentOTCrangeFinder import classify_otc_medications
from support_files.smokingRangeFinder import classify_smoking_status
from support_files.educationRangeFinder import classify_education_level
from support_files.occupationRangeFinder import classify_occupation
from support_files.vitaminDRangeFinder import classify_vitamin_d

# Get command line arguments
if len(sys.argv) >= 3:
    variable1 = sys.argv[1]  # Will be used for coloring
    variable2 = sys.argv[2]  # Will be used for shapes
    print(f"Received variables: {variable1}, {variable2}")
else:
    # Default values if no arguments provided
    variable1 = "Age"  # Default coloring variable
    variable2 = "Height"  # Default shape variable
    print("No variables provided, using defaults")


# Load the iMSMS dataset
demographic_data, sheet6_class, dependentvar = load_imsms_data()

# Convert variable1 (coloring variable) to its specified number of bins OR life stages for age
if variable1 == 'Residence':
    demographic_data = classify_residence(demographic_data, variable1)
elif variable1 == 'Ethnicity':
    demographic_data = classify_ethnicity(demographic_data, variable1)
elif variable1 == 'Sex':
    demographic_data = classify_sex(demographic_data, variable1)
elif variable1 == 'Age':
    demographic_data = convert_age_to_life_stages(demographic_data, variable1)
elif variable1 == 'Weight':
    demographic_data = convert_weightKG_to_WeightLbs(demographic_data, variable1)
elif variable1 == 'Height':
    demographic_data = convert_heightCM_to_HeightInches(demographic_data, variable1)
elif variable1 == 'Body Mass Index':
    demographic_data = classify_bmi(demographic_data, variable1)
elif variable1 == 'MS Onset Year':
    demographic_data = classify_yearOfOnset(demographic_data, variable1)
elif variable1 == 'Disease':
    demographic_data = classify_disease(demographic_data, variable1)
elif variable1 == 'Duration of MS':
    demographic_data = classify_durationOfMS(demographic_data, variable1)
elif variable1 == 'Administration of Treatment':
    demographic_data = classify_administration(demographic_data, variable1)
elif variable1 == 'Type of MS':
    demographic_data = classify_typeOfMS(demographic_data, variable1)
elif variable1 == 'Treatment Status':
    demographic_data = classify_treatmentStatus(demographic_data, variable1)
elif variable1 == 'Treatments Applied':
    demographic_data = classify_treatmentsApplied(demographic_data, variable1)
elif variable1 == 'Special need with diet':
    demographic_data = classify_binary(demographic_data, variable1)
elif variable1 == 'Specific need with diet':
    demographic_data = classify_diet(demographic_data, variable1)
elif variable1 == 'SPMS onset year':
    demographic_data = classify_yearOfSPMSOnset(demographic_data, variable1)
elif variable1 == 'Expanded Disability Status Scale':
    demographic_data = classify_EDSS(demographic_data, variable1)
elif variable1 == 'Multiple Sclerosis Severity Score':
    demographic_data = classify_MSSS(demographic_data, variable1)
elif variable1 == 'Disease modifying therapy' or variable1 == 'Breastfeeding at birth' or variable1 == 'Allergies' or variable1 == 'Asthma' or variable1 == 'Eating Disorder' or variable1 == 'Eczema' or variable1 == 'Anxiety' or variable1 == 'Manic depression(Bipolar disorder)' or variable1 == 'Obsessive Compulsory Disorder' or variable1 == 'Depression' or variable1 == 'Depression after giving birth' or variable1 == 'Type 2 Diabetes' or variable1 == 'Family Member with MS' or variable1 == 'Oral contraceptive pills' or variable1 == 'Non-steroidal anti-inflammatory drugs' or variable1 == 'Probiotics' or variable1 == 'Recreational drug use' or variable1 == 'Pets':
    demographic_data = classify_trinary(demographic_data, variable1)
elif variable1 == 'Number of Children':
    demographic_data = classify_numberOfChildren(demographic_data, variable1)
elif variable1 == 'Roommates':
    demographic_data = classify_roommates(demographic_data, variable1)
elif variable1 == 'Method of birth':
    demographic_data = classify_methodOfBirth(demographic_data, variable1)
elif variable1 == 'Specific Allergy':
    demographic_data = classify_allergy(demographic_data, variable1)
elif variable1 == 'Specific oral contraceptive pills':
    demographic_data = classify_oral_contraceptive(demographic_data, variable1)
elif variable1 == 'Specific non-steroidal anti-inflammatory drugs':
    demographic_data = classify_nsaid(demographic_data, variable1)
elif variable1 == 'Over the counter medication':
    demographic_data = classify_trinary_2(demographic_data, variable1)
elif variable1 == 'Different Over the Counter Medications':
    demographic_data = classify_otc_medications(demographic_data, variable1)
elif variable1 == 'Smoking Status':
    demographic_data = classify_smoking_status(demographic_data, variable1)
elif variable1 == 'Education level':
    demographic_data = classify_education_level(demographic_data, variable1)
elif variable1 == 'Occupation':
    demographic_data = classify_occupation(demographic_data, variable1)
elif variable1 == 'Vitamin D':
    demographic_data = classify_vitamin_d(demographic_data, variable1)
elif variable1 == 'Total Vegetables' or variable1 == 'Greens and Beans' or variable1 == 'Total Fruit' or variable1 == 'Whole Fruit' or variable1 == 'Total Protein Foods' or variable1 == 'Seafood and Plant Proteins':
    demographic_data = convert_five_point_HEI_to_grades(demographic_data, variable1)
elif variable1 == 'Whole Grains' or variable1 == 'Dairy' or variable1 == 'Fatty Acids' or variable1 == 'Sodium' or variable1 == 'Refined Grains' or variable1 == 'Added Sugars' or variable1 == 'Saturated Fats':
    demographic_data = convert_ten_point_HEI_to_grades(demographic_data, variable1)
elif variable1 == 'Healthy Eating Index Score':
    demographic_data = convert_HEI_score_to_grades(demographic_data, variable1)
else: 
    exit

# Convert variable2 (shape variable) to its specified number of bins OR life stages for age
if variable2 == 'Residence':
    demographic_data = classify_residence(demographic_data, variable2)
elif variable2 == 'Ethnicity':
    demographic_data = classify_ethnicity(demographic_data, variable2)
elif variable2 == 'Sex':
    demographic_data = classify_sex(demographic_data, variable2)
elif variable2 == 'Age':
    demographic_data = convert_age_to_life_stages(demographic_data, variable2)
elif variable2 == 'Weight':
    demographic_data = convert_weightKG_to_WeightLbs(demographic_data, variable2)
elif variable2 == 'Height':
    demographic_data = convert_heightCM_to_HeightInches(demographic_data, variable2)
elif variable2 == 'Body Mass Index':
  demographic_data = classify_bmi(demographic_data, variable2)
elif variable2 == 'MS Onset Year':
    demographic_data = classify_yearOfOnset(demographic_data, variable2)
elif variable2 == 'Disease':
    demographic_data = classify_disease(demographic_data, variable2)
elif variable2 == 'Duration of MS':
    demographic_data = classify_durationOfMS(demographic_data, variable2)
elif variable2 == 'Administration of Treatment':
    demographic_data = classify_administration(demographic_data, variable2)
elif variable2 == 'Type of MS':
    demographic_data = classify_typeOfMS(demographic_data, variable2)
elif variable2 == 'Treatment Status':
    demographic_data = classify_treatmentStatus(demographic_data, variable2)
elif variable2 == 'Treatments Applied':
    demographic_data = classify_treatmentsApplied(demographic_data, variable2)
elif variable2 == 'Special need with diet':
    demographic_data = classify_binary(demographic_data, variable2)
elif variable2 == 'Specific need with diet':
    demographic_data = classify_diet(demographic_data, variable2)
elif variable2 == 'SPMS onset year':
    demographic_data = classify_yearOfSPMSOnset(demographic_data, variable2)
elif variable2 == 'Expanded Disability Status Scale':
    demographic_data = classify_EDSS(demographic_data, variable2)
elif variable2 == 'Multiple Sclerosis Severity Score':
    demographic_data = classify_MSSS(demographic_data, variable2)
elif variable2 == 'Disease modifying therapy' or variable2 == 'Breastfeeding at birth' or variable2 == 'Allergies' or variable2 == 'Asthma' or variable2 == 'Eating Disorder' or variable2 == 'Eczema' or variable2 == 'Anxiety' or variable2 == 'Manic depression(Bipolar disorder)' or variable2 == 'Obsessive Compulsory Disorder' or variable2 == 'Depression' or variable2 == 'Depression after giving birth' or variable2 == 'Type 2 Diabetes' or variable2 == 'Family Member with MS' or variable2 == 'Oral contraceptive pills' or variable2 == 'Non-steroidal anti-inflammatory drugs' or variable2 == 'Probiotics' or variable1 == 'Recreational drug use' or variable2 == "Pets":
    demographic_data = classify_trinary(demographic_data, variable2)
elif variable2 == 'Number of Children':
    demographic_data = classify_numberOfChildren(demographic_data, variable2)
elif variable2 == 'Roommates':
    demographic_data = classify_roommates(demographic_data, variable2)
elif variable2 == 'Method of birth':
    demographic_data = classify_methodOfBirth(demographic_data, variable2)
elif variable2 == 'Specific Allergy':
    demographic_data = classify_allergy(demographic_data, variable2)
elif variable2 == 'Specific oral contraceptive pills':
    demographic_data = classify_oral_contraceptive(demographic_data, variable2)
elif variable2 == 'Specific non-steroidal anti-inflammatory drugs':
    demographic_data = classify_nsaid(demographic_data, variable2)
elif variable2 == 'Over the counter medication':
    demographic_data = classify_trinary_2(demographic_data, variable2)
elif variable2 == 'Different Over the Counter Medications':
    demographic_data = classify_otc_medications(demographic_data, variable2)
elif variable2 == 'Smoking Status':
    demographic_data = classify_smoking_status(demographic_data, variable2)
elif variable2 == 'Education level':
    demographic_data = classify_education_level(demographic_data, variable2)
elif variable2 == 'Occupation':
    demographic_data = classify_occupation(demographic_data, variable2)
elif variable2 == 'Vitamin D':
    demographic_data = classify_vitamin_d(demographic_data, variable2)
elif variable2 == 'Total Vegetables' or variable2 == 'Greens and Beans' or variable2 == 'Total Fruit' or variable2 == 'Whole Fruit' or variable2 == 'Total Protein Foods' or variable2 == 'Seafood and Plant Proteins':
    demographic_data = convert_five_point_HEI_to_grades(demographic_data, variable2)
elif variable2 == 'Whole Grains' or variable2 == 'Dairy' or variable2 == 'Fatty Acids' or variable2 == 'Sodium' or variable2 == 'Refined Grains' or variable2 == 'Added Sugars' or variable2 == 'Saturated Fats':
    demographic_data = convert_ten_point_HEI_to_grades(demographic_data, variable2)
elif variable2 == 'Healthy Eating Index Score':
    demographic_data = convert_HEI_score_to_grades(demographic_data, variable2)
else:
    exit


# Determine if variable1 should use discrete or continuous color scheme BEFORE binning
variable1_is_discrete = is_discrete_variable(variable1)
variable2_is_discrete = is_discrete_variable(variable2)


print(f"Variable1 ({variable1}) detected as: {'Discrete' if variable1_is_discrete else 'Continuous'}")
print(f"Variable2 ({variable2}) detected as: {'Discrete' if variable2_is_discrete else 'Continuous'}")

# Define colors for variable1 (coloring variable) - ADAPTIVE COLOR SCHEME
variable1_ranges = demographic_data[variable1].dropna().unique().tolist()
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


# Emperor work starts here

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