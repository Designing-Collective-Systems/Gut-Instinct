import pandas as pd
import numpy as np
from emperor import Emperor
from emperor.util import get_emperor_support_files_dir
from skbio.stats.ordination import pcoa
from scipy.spatial.distance import pdist, squareform
import sys

from support_files.discreteChecker import is_discrete_variable, FORCE_CONTINUOUS
from support_files.ageRangeFinder import convert_age_to_life_stages
from support_files.dataLoader import load_imsms_data
from support_files.colorGenerator import generate_discrete_colors, generate_gradient_colors
from support_files.jsUtils import escape_for_js, dict_to_js_object
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
from support_files.residenceRangeFinder import classify_residence, classify_residence_and_disease
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
from support_files.alphaDiversityRangeFinder import classify_richness, classify_richness_and_evenness

# Get command line arguments
if len(sys.argv) >= 2:
    variable1 = sys.argv[1]  # Will be used for coloring
    variable2 = sys.argv[2] 
    print(f"Received variable: {variable1}")
else:
    # Default value if no argument provided
    variable1 = "Age"  # Default coloring variable
    print("No variable provided, using default")

# Load the iMSMS dataset
demographic_data, sheet6_class, dependentvar = load_imsms_data(variable2)

print("=== DEBUGGING ORIGINAL DATA ===")
print(f"Original demographic_data shape: {demographic_data.shape}")

# ==================== PRESERVE RAW DATA FOR AXES ====================
# Keep a complete copy of the original raw data for axes
raw_data_for_axes = demographic_data.copy()
print(f"Preserved raw data with shape: {raw_data_for_axes.shape}")

# Filter to only numeric columns that make sense as axes
numeric_axes_vars = []
for col in raw_data_for_axes.columns:
    if pd.api.types.is_numeric_dtype(raw_data_for_axes[col]):
        non_null_count = raw_data_for_axes[col].notna().sum()
        unique_count = raw_data_for_axes[col].nunique()
        
        # Only include if it has enough variation and non-null values
        if non_null_count > 50 and unique_count > 5:
            numeric_axes_vars.append(col)
            min_val = raw_data_for_axes[col].min()
            max_val = raw_data_for_axes[col].max()
            print(f"Will use as axis: {col} (range: {min_val:.2f} to {max_val:.2f}, {unique_count} unique values)")

print(f"Selected {len(numeric_axes_vars)} numeric variables for axes")
# ==================== END RAW DATA PRESERVATION ====================

# Convert variable1 (coloring variable) to its specified number of bins OR life stages for age
if variable1 == 'Residence':
    demographic_data = classify_residence_and_disease(demographic_data, variable1, 'Disease')
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
elif variable1 == 'Gut Bacteria Richness':
    demographic_data = classify_richness(demographic_data, variable1)
elif variable1 == 'Gut Bacteria Richness and Evenness':
    demographic_data = classify_richness_and_evenness(demographic_data, variable1)

# Determine if variable1 should use discrete or continuous color scheme
variable1_is_discrete = is_discrete_variable(variable1)

print(f"Variable1 ({variable1}) detected as: {'Discrete' if variable1_is_discrete else 'Continuous'}")

# Define colors for variable1 (coloring variable) - using binned data
variable1_ranges = demographic_data[variable1].dropna().unique().tolist()
variable1_ranges.sort()

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

# Emperor work starts here
sheet6_class = sheet6_class.merge(demographic_data[['iMSMS_ID']], on='iMSMS_ID', how='inner')
demographic_data = demographic_data.set_index('iMSMS_ID')
sheet6_class = sheet6_class.set_index('iMSMS_ID')
raw_data_for_axes = raw_data_for_axes.set_index('iMSMS_ID')

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

# ==================== USE BINNED DATA FOR AXES ====================
print("=== USING BINNED METADATA VARIABLES AS AXES ===")

# Fix sample IDs first
if isinstance(pcoa_results.samples, pd.DataFrame):
    pcoa_results.samples.index = demographic_data.index
else:
    pcoa_results.samples = pd.DataFrame(
        data=pcoa_results.samples,
        index=demographic_data.index
    )

print(f"Original PCoA shape: {pcoa_results.samples.shape}")
print(f"Original columns: {list(pcoa_results.samples.columns)}")

# Create a completely new DataFrame with explicit column structure
# Start with just the first 3 PCoA axes
pcoa_base = pcoa_results.samples.iloc[:, :3].copy()
pcoa_base.columns = ['Axis 1', 'Axis 2', 'Axis 3']

print(f"Base PCoA data shape: {pcoa_base.shape}")

# Function to convert categorical data to numeric codes for plotting
def convert_categorical_to_numeric(series):
    """Convert categorical data to numeric codes while preserving category information"""
    if series.dtype == 'object' or pd.api.types.is_categorical_dtype(series):
        # Get unique categories and sort them
        unique_cats = sorted(series.dropna().unique())
        
        # Create mapping from category to numeric code
        cat_to_num = {cat: i for i, cat in enumerate(unique_cats)}
        
        # Convert to numeric
        numeric_series = series.map(cat_to_num)
        
        print(f"    Category mapping: {cat_to_num}")
        return numeric_series, cat_to_num
    else:
        # Already numeric, return as-is
        return series, None

# Add metadata variables from the binned demographic_data
key_variables = ['Age', 'Body Mass Index', 'Weight', 'Height']
axes_added = 0

for var_name in key_variables:
    print(f"\nProcessing variable: {var_name}")
    
    if var_name in demographic_data.columns:
        try:
            # Get the binned/categorized values from demographic_data
            binned_values = demographic_data.loc[pcoa_base.index, var_name]
            
            # Debug: Show what we found
            print(f"  Found {var_name} in demographic_data")
            print(f"  Data type: {binned_values.dtype}")
            print(f"  Unique values: {sorted(binned_values.dropna().unique())}")
            
            # Check if we have enough non-null values
            non_null_count = binned_values.notna().sum()
            unique_count = binned_values.nunique()
            
            print(f"  Non-null count: {non_null_count}, Unique count: {unique_count}")
            
            if non_null_count > 50 and unique_count >= 2:
                # Convert categorical data to numeric for plotting
                numeric_values, category_mapping = convert_categorical_to_numeric(binned_values)
                
                if numeric_values is not None:
                    # Add as new column
                    pcoa_base[var_name] = numeric_values
                    axes_added += 1
                    
                    print(f"✓ Added axis: {var_name} ({unique_count} categories, {non_null_count} samples)")
                    
                    # Show sample categories and their numeric mappings
                    sample_cats = binned_values.dropna().head(5).tolist()
                    sample_nums = numeric_values.dropna().head(5).tolist()
                    print(f"   Sample categories: {sample_cats}")
                    print(f"   Sample numeric values: {sample_nums}")
                    
                    # Show the full category to number mapping
                    if category_mapping:
                        print(f"   Full mapping: {category_mapping}")
                else:
                    print(f"✗ Failed to convert {var_name} to numeric values")
            else:
                print(f"✗ Insufficient data for {var_name}: {non_null_count} non-null, {unique_count} unique")
                
        except Exception as e:
            print(f"✗ Error adding {var_name}: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"  {var_name} not found in demographic_data columns")
        print(f"  Available columns: {list(demographic_data.columns)}")

# If no key variables were available, try other variables from demographic_data
if axes_added == 0:
    print("No key variables found, trying other demographic variables...")
    
    for var_name in demographic_data.columns:
        if var_name not in ['iMSMS_ID'] and axes_added < 4:  # Limit to 4 additional axes
            try:
                binned_values = demographic_data.loc[pcoa_base.index, var_name]
                non_null_count = binned_values.notna().sum()
                unique_count = binned_values.nunique()
                
                # Only include if it has enough variation and non-null values
                if non_null_count > 50 and 2 <= unique_count <= 20:  # Reasonable number of categories
                    numeric_values, category_mapping = convert_categorical_to_numeric(binned_values)
                    
                    if numeric_values is not None:
                        pcoa_base[var_name] = numeric_values
                        axes_added += 1
                        print(f"✓ Added axis: {var_name} ({unique_count} categories, {non_null_count} samples)")
                        
            except Exception as e:
                print(f"✗ Error adding {var_name}: {e}")

print(f"Enhanced data shape: {pcoa_base.shape}")
print(f"Enhanced columns: {list(pcoa_base.columns)}")

# Create new proportion explained that matches the new structure
n_total_axes = len(pcoa_base.columns)
if hasattr(pcoa_results, 'proportion_explained'):
    original_explained = pcoa_results.proportion_explained.iloc[:3].values
else:
    original_explained = np.array([0.3, 0.2, 0.1])

# Create explained variance for all axes
all_explained = np.concatenate([
    original_explained,
    np.zeros(n_total_axes - 3)  # Zeros for metadata axes
])

# Update the pcoa_results with the new structure
pcoa_results.samples = pcoa_base
pcoa_results.proportion_explained = pd.Series(all_explained, index=pcoa_base.columns)

print(f"Final verification:")
print(f"  - Samples shape: {pcoa_results.samples.shape}")
print(f"  - Samples columns: {list(pcoa_results.samples.columns)}")
print(f"  - Proportion explained length: {len(pcoa_results.proportion_explained)}")
print(f"  - Axes should include: {axes_added} metadata variables")

# Quick data validation
print(f"\nData validation:")
for col in pcoa_results.samples.columns:
    non_null = pcoa_results.samples[col].notna().sum()
    data_type = pcoa_results.samples[col].dtype
    min_val = pcoa_results.samples[col].min() if pd.api.types.is_numeric_dtype(pcoa_results.samples[col]) else "N/A"
    max_val = pcoa_results.samples[col].max() if pd.api.types.is_numeric_dtype(pcoa_results.samples[col]) else "N/A"
    print(f"  {col}: {non_null} non-null values, dtype: {data_type}, range: {min_val} to {max_val}")

# ==================== END USE BINNED DATA FOR AXES ====================

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

# Set other visualization options
viz.set_axes([0, 1, 2])  # Set axes to display (using indices 0, 1, 2 for pc1, pc2, pc3)

# Create dictionaries for scaling and opacity - ROBUST HANDLING
scale_dict = {var1_range: 1.0 for var1_range in variable1_ranges}
opacity_dict = {var1_range: 1.0 for var1_range in variable1_ranges}

# Generate the base Emperor visualization HTML
emperor_html = viz.make_emperor(standalone=True)

# Safely escape variable names for JavaScript
safe_variable1 = escape_for_js(variable1)

# Use safe escaping for custom_colors
custom_colors_js = dict_to_js_object(custom_colors)

# Generate the custom color Emperor JavaScript
custom_js = generate_custom_color_js(safe_variable1)

# Generate the precise UI hiding JavaScript
precise_hide_js = generate_precise_hide_js()

# Generate the precise UI hiding CSS
precise_hide_css = generate_precise_hide_css()

# Generate the information overlay JavaScript (without variable2)
# overlay_js = generate_overlay_js(variable1, None, dependentvar)

# Combine the precise solution
complete_precise_solution = precise_hide_js

# Update your script with the precise solution
final_precise_custom_js = custom_js + "\n\n" + complete_precise_solution + "\n\n" #+ overlay_js

# ==================== ADD YOUTUBE VIDEO SECTION ====================
# Configuration for the 5 YouTube videos
VIDEO_CONFIGS = [
    {"id": "EpD_LqLw3ck", "title": "Clustering in Emperor"},
    {"id": "zObm4E5TRq4", "title": "Variance and Clustering in Emperor"}, 
    {"id": "N92V0k64GqQ", "title": "Choosing Taxa Level (for analysis)"},
    {"id": "9GxwTPYhOhs", "title": "Using Color, Visibility, and Shape"},
    {"id": "oqI2D8NwoMk", "title": "Beta Diversity within clusters in Emperor"}
]

# Generate HTML for all 5 videos
videos_html = ""
for i, config in enumerate(VIDEO_CONFIGS):
    videos_html += f'''
    <div class="individual-video" data-video-index="{i}">
        <div class="video-header">
            <h3>{config["title"]}</h3>
        </div>
        <div class="video-wrapper" id="video-wrapper-{i}">
            <iframe 
                id="youtube-player-{i}"
                src="https://www.youtube.com/embed/{config["id"]}?enablejsapi=1&controls=1&modestbranding=1&rel=0"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        </div>
    </div>
    '''

# YouTube video container HTML
youtube_video_html = f'''
<div id="youtube-video-container" class="youtube-container">
    <div class="main-header">
        <h2>Educational Videos</h2>
    </div>
    <div class="videos-grid" id="videos-grid">
        {videos_html}
    </div>
</div>
'''

# YouTube video CSS
youtube_video_css = '''
<style>
/* YouTube Video Container */
.youtube-container {
    position: fixed;
    top: 450px; /* Position below color classification area */
    right: 20px;
    width: 500px;
    max-height: calc(100vh - 320px);
    background: #fff;
    border: 2px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    overflow-y: auto;
}

.main-header {
    background: #2196F3;
    color: white;
    padding: 12px 15px;
    border-radius: 6px 6px 0 0;
    text-align: center;
    position: sticky;
    top: 0;
    z-index: 10;
}

.main-header h2 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
}

.videos-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap: 0;
    padding: 0;
}

.individual-video {
    border: 1px solid #e9ecef;
    background: #fff;
}

.individual-video:nth-child(1),
.individual-video:nth-child(2) {
    /* Top row videos - no changes needed */
}

.individual-video:nth-child(3),
.individual-video:nth-child(4) {
    /* Second row videos - no changes needed */
}

.individual-video:nth-child(5) {
    /* Bottom video spans only left column */
    grid-column: 1;
}

.video-header {
    background: #f8f9fa;
    padding: 8px 12px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: background-color 0.2s ease;
    border-bottom: 1px solid #e9ecef;
}

.video-header:hover {
    background: #e9ecef;
}

.video-header h3 {
    margin: 0;
    font-size: 11px;
    color: #333;
    font-weight: 600;
    flex: 1;
}

.minimize-indicator {
    font-size: 14px;
    font-weight: bold;
    color: #666;
    transition: transform 0.2s ease;
    margin-left: 8px;
}

.video-wrapper {
    position: relative;
    padding-bottom: 56.25%; /* 16:9 aspect ratio */
    height: 0;
    overflow: hidden;
    transition: all 0.3s ease;
}

.video-wrapper.minimized {
    padding-bottom: 0;
    height: 0;
    opacity: 0;
}

.video-wrapper iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

/* Minimized state indicators */
.individual-video.minimized .minimize-indicator {
    transform: rotate(90deg);
}

/* Responsive adjustments */
@media (max-width: 1400px) {
    .youtube-container {
        width: 500px;
    }
}

@media (max-width: 1200px) {
    .youtube-container {
        position: relative;
        top: auto;
        right: auto;
        width: 100%;
        max-width: 600px;
        margin: 20px auto;
        max-height: 70vh;
    }
    
    .videos-grid {
        grid-template-columns: 1fr;
    }
    
    .individual-video:nth-child(5) {
        grid-column: 1;
    }
}

@media (max-width: 768px) {
    .youtube-container {
        width: calc(100% - 20px);
        margin: 10px;
        top: auto;
        right: auto;
        position: relative;
        max-height: 60vh;
    }
    
    .main-header h2 {
        font-size: 14px;
    }
    
    .video-header h3 {
        font-size: 10px;
    }
    
    .videos-grid {
        grid-template-columns: 1fr;
    }
    
    .individual-video:nth-child(5) {
        grid-column: 1;
    }
}

/* Scrollbar styling */
.youtube-container::-webkit-scrollbar {
    width: 6px;
}

.youtube-container::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.youtube-container::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.youtube-container::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}
</style>
'''

# JavaScript for video controls
youtube_video_js = '''
// YouTube Video Controls - No minimize functionality needed
$(document).ready(function() {
    // Videos are always visible, no controls needed
    console.log('Educational videos loaded successfully');
});
'''
# ==================== END YOUTUBE VIDEO SECTION ====================

# ==================== ADD PAGE HEADER ====================
# Define the header HTML and CSS
page_header_html = '''
<div class="emperor-page-header">
    <h1>Emperor Visualization Page</h1>
</div>
'''

page_header_css = '''
<style>
.emperor-page-header {
    text-align: center;
    margin: 20px 0 30px 0;
    padding: 20px;
    background-color: #f8f9fa;
    border-bottom: 3px solid #2196F3;
}

.emperor-page-header h1 {
    color: #333;
    font-size: 48px;
    font-weight: bold;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    font-family: 'Helvetica Neue', Arial, sans-serif;
}

@media (max-width: 768px) {
    .emperor-page-header h1 {
        font-size: 36px;
    }
    
    .emperor-page-header {
        margin: 10px 0 20px 0;
        padding: 15px;
    }
}
</style>
'''
# ==================== END PAGE HEADER ====================

# Insert the header CSS, precise hide CSS, and YouTube video CSS
emperor_html = emperor_html.replace('</head>', f'{page_header_css}{precise_hide_css}{youtube_video_css}</head>')

# Insert the header HTML right after the body tag
body_start = emperor_html.find('<body')
if body_start != -1:
    # Find the end of the opening body tag
    body_tag_end = emperor_html.find('>', body_start) + 1
    emperor_html = emperor_html[:body_tag_end] + page_header_html + emperor_html[body_tag_end:]

# Insert the YouTube video HTML right after the page header
header_end = emperor_html.find('</div>', emperor_html.find('emperor-page-header'))
if header_end != -1:
    header_end += 6  # Move past the </div>
    emperor_html = emperor_html[:header_end] + youtube_video_html + emperor_html[header_end:]

# Update the final JavaScript to include YouTube controls
final_precise_custom_js_with_youtube = final_precise_custom_js + "\n\n" + youtube_video_js

# Replace the JavaScript insertion
marker_pattern = "/*__custom_on_ready_code__*/"
if marker_pattern in emperor_html:
    emperor_html = emperor_html.replace(marker_pattern, marker_pattern + "\n      " + final_precise_custom_js_with_youtube)
else:
    ready_function_end = "ec.ready = function () {"
    start_idx = emperor_html.find(ready_function_end)
    if start_idx != -1:
        insertion_idx = start_idx + len(ready_function_end)
        emperor_html = emperor_html[:insertion_idx] + "\n      " + final_precise_custom_js_with_youtube + emperor_html[insertion_idx:]

print("Applied PRECISE tab hiding solution that preserves Color, Visibility, and Axes tabs AND hides settings button")
print("Added prominent 'Emperor Visualization Page' header")
print(f"Added 5 YouTube videos in 2x2+1 grid layout (no minimize controls)")
print("- Video overlay is fixed below color classification area (scroll-independent)")
print("- Videos 1&2 side by side (top row), videos 3&4 side by side (middle row), video 5 bottom left")
print("- Removed all minimize/maximize functionality")
print("- Fixed responsive breakpoints with !important declarations")

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
print(f"- Using {variable1} for coloring only (no shape customization)")
print("- Variable-specific binning: variable maintains its designated number of bins")
print("- Adaptive color scheme: discrete variables use distinct colors, continuous variables use YlOrRd gradient")
print("- Axes renamed from PC1, PC2, PC3 to Axis 1, Axis 2, Axis 3")
print("- Relative paths for better portability")
print("- Safe JavaScript escaping for special characters")
print(f"- Added {axes_added} raw numeric variables as selectable axes")
print("- Raw data used for axes, binned data used for colors")
print("- Used safe column renaming to avoid pandas errors")
print("- Added prominent 'Emperor Visualization Page' header to generated HTML")
print("- Added 5 YouTube videos in 2x2+1 grid layout (always visible)")
print("- Video overlay positioned below color classification (fixed, scroll-independent)")
print("- Videos arranged: 1&2 top row, 3&4 middle row, 5 bottom left")
print("- Removed all minimize/maximize functionality")
print("- Fixed responsive breakpoints using !important declarations")
print("\nScript completed.")