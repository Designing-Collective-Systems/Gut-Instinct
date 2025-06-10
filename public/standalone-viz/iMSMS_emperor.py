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

# Define variables that should be treated as discrete
DISCRETE_VARIABLES = {
    'administration', 'allergies', 'allergy_specific', 'anxiety', 'asthma', 
    'birth_method', 'breastfeeding', 'depression', 'diet_no_special_needs', 
    'diet_special_needs', 'disease', 'disease_course', 'disease_course_control', 
    'dmt', 'eating_disorder', 'eczema', 'education', 'ethnicity', 'manic_depression_bipolar', 
    'ms_family', 'nsaids', 'nsaids_specifics', 'occupation', 'ocd', 'ocps_y_n', 
    'otc_meds', 'pets', 'postpartum_depression', 'probiotics', 'recreational_drug', 
    'sex', 'site', 'smoke', 'treated', 'treatment_status', 
    'treatments', 'treatments_control', 'type2diabetes', 'weight_change', 
    'which_ocp'
}

# Define variables that should always be treated as continuous (override other detection)
FORCE_CONTINUOUS = {
    'ADDSUG', 'age', 'Alcohol % of cals (%)', 'B1, B2 (mg)', 'Beta-carotene (mcg)', 'bmi', 
    'Bread, pasta, rice (1)', 'Calcium (mg)','Calories (Kcal)','Carbohydrate (g)', 
    'Carbohydrate (g) as % of cals', 'children_number', 'Cholestrol (mg)', 'csf_results', 
    'Dietary Fiber(g)', 'disease_duration', 'edss', 'FATTYACID', 'Fat (g)', 
    'Fat (g) as % of cals', 'Folate (mcg)', 'Fruits, fruit juices (cups)', 
    'Good oils, in foods ("teaspoons")', 'GREEN_AND_BEAN', 'HEI2015_TOTAL_SCORE', 'height', 
    'Iron (mg)', 'Magnesium (mg)',  'Meat, eggs, or beans (1)', 'Milk, cheese, yogurt (cups)', 
    'Monounsaturated fat (g)', 'MSSS', 'Niacin (mg)', 'otc_number', 'Polyunsaturated fat (g)', 
    'Potassium (mg)', 'Protein (g)', 'Protein (g) as % of cals', 'REFINEDGRAIN', 'relapse_number', 
    'roommates', 'rxmeds', 'rxmeds_number', 'Saturated fat (g)','Saturated fat (g) as % of cals',
    'SEAPLANT_PROT', 'SFA', 'SODIUM', 'Sodium (salt) (mg)', 'spms_year', 'Sweets % of cals (%)', 
    'Vegetables group (cups)', 'Vitamdietpairsumin A (RAE)', 'TOTALDAIRY', 'TOTALFRUIT','TOTALVEG', 
    'TOTPROT', 'Vitamin B6 (mg)', 'Vitamin C (mg)', 'vitamin D (IU)', 'Vitamin E (mg)',  'weight', 
    'WHOLEFRUIT','WHOLEGRAIN', 'Whole grains (1)', 'without potatoes (cups)', 'year_of_onset', 
    'Zinc (mg)',       
}

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

VARIABLE_DESCRIPTIONS = {
    'ADDSUG': 'Added sugar content in diet over 6-12 months. SEE HEI2015 information.',
    'FATTYACID': 'Fatty acid profile in diet over 6-12 months. SEE HEI2015 information.',
    'GREEN_AND_BEAN': 'Dark green vegetables and beans and peas in diet over 6-12 months. SEE HEI2015 information.',
    'TOTALDAIRY': 'Fat free dairy consumption over 6-12 months. SEE HEI2015 information.',
    'TOTALFRUIT': 'Fruit consumption(including fruit juice) over 6-12 months. SEE HEI2015 information.',
    'TOTALVEG': 'Vegetable consumption over 6-12 months. SEE HEI2015 information.',
    'TOTPROT': 'Protein consumption over 6-12 months. SEE HEI2015 information.',
    'HEI2015_TOTAL_SCORE': 'The HEI2015 is the latest iteration of the Healthy Eating Index, a tool designed to measure diet quality—that is, how closely an eating pattern or mix of foods matches the Dietary Guidelines for Americans recommendations. HEI2015 is a total value of ADDSUG, FATTYACID, GREEN_AND_BEAN, TOTALDAIRY, TOTALFRUIT, TOTALVEG, TOTPROT, REFINEDGRAIN, WHOLEFRUIT, WHOLEGRAIN, SFA, SEAPLANT_PROT, SODIUM',
    'REFINEDGRAIN': 'Refined grain consumption over 6-12 months. SEE HEI2015 information.',
    'WHOLEFRUIT': 'Fruit consumption(without fruit juice) over 6-12 months. SEE HEI2015 information.',
    'WHOLEGRAIN': 'Whole grain consumption over 6-12 months. SEE HEI2015 information.',
    'SFA': 'Saturated fat consumption over 6-12 months. SEE HEI2015 information.',
    'SEAPLANT_PROT': 'Protein consumption(seafood + plants) over 6-12 months.SEE HEI2015 information.',
    'SODIUM': 'Sodium consumption over 6-12 months. SEE HEI2015 information.',
    

            'administration': 'How the DMTs were administered to the participant with MS',

            'age': 'What is the participants age',

            'Alcohol % of cals (%)': 'FFQ calculation over last 6-12 months',

            'allergies': 'Does participant have an allergy',

            'allergy_specific': 'Participant allergy type',

            'anxiety': 'Does participant have anxiety or not',

            'asthma': 'Does participant have asthma or not',

    
            'Beta-carotene (mcg)': 'FFQ calculation over last 6-12 months',
    
            'birth_method': 'How was participant born',
    
            'bmi': 'Participant BMI calculated from height(cm) and weight(kg) measurements',

            'Bread, pasta, rice (1)': 'FFQ calculation over last 6-12 months',

            'breastfeeding': 'Did participant breastfeed as a child',

            'Calcium (mg)': 'FFQ calculation over last 6-12 months',
                    
            'Calories (Kcal)': 'FFQ calculation over last 6-12 months',

            'Carbohydrate (g)': 'FFQ calculation over last 6-12 months',

            'Carbohydrate (g) as % of cals': 'FFQ calculation over last 6-12 months',

            'children_number': 'participant children number',

            'Cholestrol (mg)': 'FFQ calculation over last 6-12 months',

            # 'csf_results': 'Cerebrospinal fluid analysis results for neurological markers',

            'depression': 'Does participant have depression or not',
    
            'diet_no_special_needs': 'Whether participant has dietary restrictions or not',
    
            'diet_special_needs': 'Dietary restriction(s) for participant',
    
            'Dietary Fiber(g)': 'FFQ calculation over last 6-12 months',

            'disease': 'Whether participant has MS or not',

    # 'disease_course': 'What type of MS the patient has: RRMS , SPMS or PPMS',

            'disease_course_control': 'MS patient + their controls corresponding pair value. Patient can have RRMS or PMS(SPMS and PPMS lumped together) If MS patient has RRMS, corresponding household member(control) would be control_RRMS. ',
            
            'disease_duration': 'How long the patient has had MS',

            'dmt': 'Among the 576 MS patients, 209 (36%) were untreated and 367 (63%) were treated with a disease modifying therapy (DMT). Note that this was done before the study. In page 17-18, we see that Participants were excluded if they received oral antibiotics within the past three months, corticosteroids within the past 30 days, or were on a disease modifying therapy for less than three months',
    
            'eating_disorder': 'Does participant have eating_disorder or not',

            'eczema': 'Does participant have eczema or not',
    
            'edss': 'The Expanded Disability Status Scale (EDSS) is a tool used to measure disability in people with multiple sclerosis (MS). It ranges from 0 to 10, with 0 being normal and 10 representing death due to MS.',

            'education': 'Highest level of formal education completed by participant',

            'ethnicity': 'What is the participants ethincity',

            'Fat (g)': 'FFQ calculation over last 6-12 months',

            'Fat (g) as % of cals': 'FFQ calculation over last 6-12 months',
    
            'Folate (mcg)': 'FFQ calculation over last 6-12 months',

            'Fruits, fruit juices (cups)': 'FFQ calculation over last 6-12 months',

            'Good oils, in foods ("teaspoons")': 'FFQ calculation over last 6-12 months',
    
            'height': 'Participant height measurement in centimeters',
    
            'household': 'FFQ calculation over last 6-12 months',

            'Iron (mg)': 'FFQ calculation over last 6-12 months',

            'Magnesium (mg)': 'FFQ calculation over last 6-12 months',

            'manic_depression_bipolar': 'Does participant have manic_depression_bipolar or not',

            'Meat, eggs, or beans (1)': 'FFQ calculation over last 6-12 months',

            'Milk, cheese, yogurt (cups)': 'FFQ calculation over last 6-12 months',
            
            'Monounsaturated fat (g)': 'FFQ calculation over last 6-12 monthss',

            'ms_family': 'Participant number of family member(s) with MS',

            'MSSS': 'The MSSS (Multiple Sclerosis Severity Score) is a tool used in multiple sclerosis (MS) to assess disease severity by combining disability (measured by the EDSS) with disease duration. It provides a score that ranges from 0 to 10.',

            'Niacin (mg)': 'FFQ calculation over last 6-12 months',

            'nsaids': 'Did participant use non-steroidal anti-inflammatory drugs',

            'nsaids_specifics': 'Type of non-steroidal anti-inflammatory drugs used by participant',

            'occupation': 'Participant occupation',

            'ocd': 'Does participant have ocd or not',

            'ocps_y_n': 'Did participant take oral contraceptive pills or not',

            'otc_meds': 'Does participant take Over-the-counter medication',

            'otc_number': 'Total count of different Over-the-counte medications used',

            'pets': 'Does participant have pets or not',

            'Polyunsaturated fat (g)': 'FFQ calculation over last 6-12 monthss',

            'postpartum_depression': 'Did female participant experience postpartum_depression or not',

            'Potassium (mg)': 'FFQ calculation over last 6-12 monthse',

            'probiotics': 'Has patient taken probiotics',

            'Protein (g)': 'FFQ calculation over last 6-12 monthss',

            'Protein (g) as % of cals': 'FFQ calculation over last 6-12 months',

            'recreational_drug': 'Does participant take recreational drugs',

    

            # 'relapse_number': 'Count of disease exacerbations or symptom flare-ups',

            'roommates': 'Participant roommates number',

            'rxmeds': 'Does participant take Prescription medication or not',

            'rxmeds_number': 'Participant total count of different prescription medications taken',

            'Saturated fat (g)': 'FFQ calculation over last 6-12 months',

            'Saturated fat (g) as % of cals': 'FFQ calculation over last 6-12 months',
    
            'sex': 'What is the participants sex',
    

            'site': '1152 participants were recruited from seven sites (recruiting centers) located in San Francisco, Boston, New York, Pittsburgh, Buenos Aires, Edinburgh and San Sebastián',

            'smoke': 'Participant smoke history',

            'Sodium (salt) (mg)': 'FFQ calculation over last 6-12 months',

            'spms_year': 'Year of secondary progressive multiple sclerosis diagnosis',
    
            'Sweets % of cals (%)': 'FFQ calculation over last 6-12 months',
            
            'treatment_control': 'MS patient treatment status + their controls corresponding pair value. Patient can be treated or Untreated. If MS patient is treated, corresponding household member(control) would be treated_HHC.',
    
    # 'treatment_status': 'For DMTs(see the note on DMTs), treatment_status is treated, control or untreated',

    # 'treatments': 'For DMTs(see the note on DMTs), Treatments included oral agents Fingolimod (n=71), and dimethyl fumarate (DMF, n=86);, injectables glatiramer acetate (GA, n=68) and interferon (IFN, n=87); and infusion agents anti-CD20 monoclonal antibodies (n=28), and natalizumab (n=27)',


            'treatments_control': '(see the note on DMTs), MS patient treatment + their controls corresponding pair value. If patient was treated with Fingolimod, control value would be control_Fingolimod',

            'type2diabetes': 'Does participant have type2diabetes or not',

            'Vegetables group (cups)': 'FFQ calculation over last 6-12 months',

            'Vitamdietpairsumin A (RAE)': 'FFQ calculation over last 6-12 months',

            'Vitamin B6 (mg)': 'FFQ calculation over last 6-12 months',

            'Vitamin C (mg)': 'FFQ calculation over last 6-12 months',

            'vitamin D (IU)': 'FFQ calculation over last 6-12 months',

            'Vitamin E (mg)': 'FFQ calculation over last 6-12 months',

            'weight': 'What is the participants weight in kg',

            # 'weight_change': 'Recent weight fluctuation patterns and magnitude',
    
            'which_ocp': 'Specific oral contraceptive pill(s) taken by participant',

            'Whole grains (1)': 'FFQ calculation over last 6-12 months',

            'without potatoes (cups)': 'FFQ calculation over last 6-12 months',

            'year_of_onset': 'Year when participant was diagnosed with MS',

            'Zinc (mg)': 'FFQ calculation over last 6-12 months'
}

# Sheet description
SHEET_DESCRIPTIONS = {
    'Dataset S1.2': 'Primary demographic and clinical characteristics dataset containing patient baseline information, medical history, and socioeconomic factors collected at study enrollment'
}

# Function to safely escape strings for JavaScript
def escape_for_js(text):
    """
    Safely escape a string for use in JavaScript.
    Handles quotes, backslashes, newlines, and other special characters.
    """
    if text is None:
        return 'null'
    
    # Convert to string and handle NaN/null values
    text = str(text)
    if text.lower() in ['nan', 'none', 'null']:
        return 'null'
    
    # Use JSON encoding which properly escapes all special characters
    return json.dumps(text)

# Function to safely convert dictionary to JavaScript object
def dict_to_js_object(d):
    """
    Convert a Python dictionary to a JavaScript object string with proper escaping.
    """
    js_pairs = []
    for key, value in d.items():
        escaped_key = escape_for_js(str(key))
        escaped_value = escape_for_js(str(value))
        js_pairs.append(f"{escaped_key}: {escaped_value}")
    
    return "{" + ", ".join(js_pairs) + "}"

# Function to determine if a variable should be treated as discrete
def is_discrete_variable(variable_name, data_series):
    """
    Determine if a variable should be treated as discrete based on:
    1. Forced continuous variables (always continuous)
    2. Predefined list of discrete variables
    3. Data type (string/object columns are discrete)
    4. Number of unique values relative to total samples (for original numeric data)
    """
    # Check forced continuous variables first
    if variable_name in FORCE_CONTINUOUS:
        return False
    
    # Check predefined discrete variables
    if variable_name in DISCRETE_VARIABLES:
        return True
    
    # If no data provided, default to discrete
    if data_series is None or len(data_series) == 0:
        return True
    
    # Check if data is non-numeric (strings/categories)
    if data_series.dtype == 'object' or data_series.dtype.name.startswith('str'):
        return True
    
    # For numeric data, check the characteristics of the original data
    non_null_data = data_series.dropna()
    if len(non_null_data) == 0:
        return True
    
    unique_values = non_null_data.unique()
    num_unique = len(unique_values)
    total_samples = len(non_null_data)
    
    # If fewer than 8 unique values total, treat as discrete
    # This catches small categorical scales (1-5 ratings, etc.)
    if num_unique < 8:
        return True
    
    # Check if all values are integers and there aren't many of them
    # This catches things like Likert scales, small counts, etc.
    if all(float(val).is_integer() for val in unique_values if not pd.isna(val)):
        # If range is small (less than 15) and most values are represented, treat as discrete
        value_range = max(unique_values) - min(unique_values)
        if value_range < 15 and num_unique > (value_range * 0.5):
            return True
    
    # If less than 15% of values are unique, treat as discrete
    # This is more restrictive than before to avoid misclassifying continuous variables
    unique_ratio = num_unique / total_samples
    if unique_ratio < 0.15:
        return True
    
    # If we have many unique values and they're spread out, treat as continuous
    return False

# Function to generate discrete color palette
def generate_discrete_colors(num_categories):
    """Generate distinct colors for discrete categories"""
    # Extended color palette for discrete variables
    discrete_colors = [
        '#1f77b4',  # blue
        '#ff7f0e',  # orange
        '#2ca02c',  # green
        '#d62728',  # red
        '#9467bd',  # purple
        '#8c564b',  # brown
        '#e377c2',  # pink
        '#7f7f7f',  # gray
        '#bcbd22',  # olive
        '#17becf',  # cyan
        '#aec7e8',  # light blue
        '#ffbb78',  # light orange
        '#98df8a',  # light green
        '#ff9896',  # light red
        '#c5b0d5',  # light purple
        '#c49c94',  # light brown
        '#f7b6d3',  # light pink
        '#c7c7c7',  # light gray
        '#dbdb8d',  # light olive
        '#9edae5'   # light cyan
    ]
    
    # If we need more colors than available, generate additional ones
    if num_categories > len(discrete_colors):
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        
        # Use matplotlib's tab20 colormap for additional colors
        tab20 = plt.cm.get_cmap('tab20')
        additional_colors = [mcolors.rgb2hex(tab20(i)) for i in np.linspace(0, 1, num_categories)]
        return additional_colors
    
    return discrete_colors[:num_categories]

# Function to generate gradient colors (YlOrRd scheme)
def generate_gradient_colors(num_bins):
    """Generate gradient colors using Yellow-Orange-Red scheme"""
    
    # Use matplotlib's YlOrRd colormap
    cmap = plt.cm.get_cmap('YlOrRd')
    # Generate colors from light (0.2) to dark (1.0) to ensure we get the full range
    # Starting at 0.2 instead of 0.0 to avoid too pale colors
    colors = [mcolors.rgb2hex(cmap(0.2 + (0.8 * i / (num_bins - 1)))) for i in range(num_bins)]
    
    return colors

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
    
    original_data = df[column_name].copy()
    if is_discrete_variable(column_name, original_data):
        # For discrete variables, keep original values but ensure they're strings
        df[column_name] = df[column_name].astype(str)
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
dependentvar = 'order'
sheet6_class = pd.read_excel(S6_PATH, sheet_name=dependentvar)

# Merge the demographic data
demographic_data = (sheet1_2
                   .merge(sheet3, on='iMSMS_ID', how='inner')
                   .merge(sheet2, on='iMSMS_ID', how='inner')
                   )

# print(demographic_data.columns.tolist())

# Store original data for discrete/continuous analysis before any processing
original_variable1_data = demographic_data[variable1].copy() if variable1 in demographic_data.columns else None
original_variable2_data = demographic_data[variable2].copy() if variable2 in demographic_data.columns else None


# Determine if variable1 should use discrete or continuous color scheme BEFORE binning
variable1_is_discrete = is_discrete_variable(variable1, original_variable1_data) if original_variable1_data is not None else True
variable2_is_discrete = is_discrete_variable(variable2, original_variable2_data) if original_variable2_data is not None else True


print(f"Variable1 ({variable1}) detected as: {'Discrete' if variable1_is_discrete else 'Continuous'}")
print(f"Original data type: {original_variable1_data.dtype if original_variable1_data is not None else 'Unknown'}")
print(f"Unique values in original data: {len(original_variable1_data.dropna().unique()) if original_variable1_data is not None else 'Unknown'}")

# Convert variable1 (coloring variable) to its specified number of bins
demographic_data = convert_column_to_ranges(demographic_data, variable1, num_bins=variable1_bins)

# Convert variable2 (shape variable) to its specified number of bins
demographic_data = convert_column_to_ranges(demographic_data, variable2, num_bins=variable2_bins)

# Convert other numeric columns, excluding our target variables
demographic_data = convert_to_ranges(demographic_data, num_bins=5, exclude_columns=[variable1, variable2])

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

# Sort ranges properly - if they contain numeric ranges, sort by the first number
def sort_ranges_numerically(ranges):
    def extract_first_number(range_str):
        try:
            # Extract the first number before the dash
            if '-' in str(range_str):
                return float(str(range_str).split('-')[0])
            else:
                # If no dash, try to convert the whole string to float
                return float(str(range_str))
        except (ValueError, AttributeError):
            # If conversion fails, return the string for alphabetical sorting
            return str(range_str)
    
    return sorted(ranges, key=extract_first_number)

# Define colors for variable1 (coloring variable) - ADAPTIVE COLOR SCHEME
variable1_ranges = demographic_data[variable1].dropna().unique().tolist()

if variable1_is_discrete:
    variable1_ranges.sort()  # Simple alphabetical sort for discrete variables
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
if variable2_is_discrete:
    variable2_ranges.sort()  # Simple alphabetical sort for discrete variables
else:
    variable2_ranges = sort_ranges_numerically(variable2_ranges)  # Numeric sort for continuous

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
# Convert the shape mapping to JavaScript format using safe escaping
shape_mapping_js = dict_to_js_object(custom_shapes)

# Safely escape variable names for JavaScript
safe_variable1 = escape_for_js(variable1)
safe_variable2 = escape_for_js(variable2)

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
  }},
  'Diamond': function() {{
    return new THREE.OctahedronGeometry(0.5);
  }},
  'Ring': function() {{
    return new THREE.TorusGeometry(0.4, 0.1, 8, 16);
  }},
  'Icosahedron': function() {{
    return new THREE.IcosahedronGeometry(0.5);
  }},
  'Square': function() {{
    return new THREE.BoxGeometry(0.8, 0.8, 0.2);
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
  
  // Find variable2 index in metadata
  let variable2Index = -1;
  for (let i = 0; i < metadataHeaders.length; i++) {{
    if (metadataHeaders[i] === {safe_variable2}) {{
      variable2Index = i;
      break;
    }}
  }}
  
  if (variable2Index === -1) {{
    console.log("Variable2 field not found in metadata");
    return false;
  }}
  
  // Create a map from sample ID to variable2 value
  const sampleToVariable2 = {{}};
  for (const sampleId in metadata) {{
    if (metadata.hasOwnProperty(sampleId)) {{
      sampleToVariable2[sampleId] = metadata[sampleId][variable2Index];
    }}
  }}
  
  // Map variable2 values to shape types - DYNAMIC MAPPING
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
          
          // Determine which shape to use based on sample ID and variable2
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
# Use safe escaping for custom_colors
custom_colors_js = dict_to_js_object(custom_colors)

custom_js = f"""
// Set the metadata field to variable1 for coloring
setTimeout(function() {{
  // HANDLE COLORING BY VARIABLE1
  if (ec.controllers && ec.controllers.color) {{
    var colorController = ec.controllers.color;
    
    // First check if variable1 is available in the dropdown
    var colorSelect = colorController.$select[0];
    var hasVariable1 = false;
    
    for (var i = 0; i < colorSelect.options.length; i++) {{
      if (colorSelect.options[i].value === {safe_variable1}) {{
        hasVariable1 = true;
        colorSelect.selectedIndex = i;
        
        // IMPORTANT: Don't trigger change event to preserve our custom color scheme
        // The Python code has already set up the correct colors
        console.log('Auto-selected variable1 for coloring (preserving custom color scheme)');
        break;
      }}
    }}
    
    if (!hasVariable1) {{
      console.log('Variable1 category not found in available metadata');
    }}
    
    // Preserve the custom color mapping that was set in Python
    // Store our custom colors to prevent Emperor from overriding them
    var customColorMapping = {custom_colors_js};
    
    // Override Emperor's color update function to preserve our colors
    if (colorController.setPlottableAttributes) {{
      var originalSetPlottableAttributes = colorController.setPlottableAttributes;
      colorController.setPlottableAttributes = function(group) {{
        // Call the original function
        originalSetPlottableAttributes.call(this, group);
        
        // Then restore our custom colors
        var decomp = ec.sceneViews[0].decomp;
        if (decomp && decomp.plottable) {{
          var metadata = decomp.plottable.metadata;
          var metadataHeaders = decomp.plottable.metadata_headers;
          
          // Find variable1 index
          var variable1Index = metadataHeaders.indexOf({safe_variable1});
          if (variable1Index !== -1) {{
            for (var i = 0; i < decomp.plottable.sample_ids.length; i++) {{
              var sampleId = decomp.plottable.sample_ids[i];
              var variable1Value = metadata[sampleId][variable1Index];
              
              if (customColorMapping[variable1Value]) {{
                var color = customColorMapping[variable1Value];
                // Convert hex to RGB
                var r = parseInt(color.slice(1, 3), 16) / 255;
                var g = parseInt(color.slice(3, 5), 16) / 255;
                var b = parseInt(color.slice(5, 7), 16) / 255;
                
                decomp.plottable.colors[i] = [r, g, b];
              }}
            }}
            
            // Force update of the visualization
            decomp.plottable.needsUpdate = true;
            if (ec.sceneViews[0].needsUpdate !== undefined) {{
              ec.sceneViews[0].needsUpdate = true;
            }}
          }}
        }}
      }};
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

# More precise hiding that preserves Color and Shape AND hides settings button
precise_hide_js = """
// Precise tab hiding that preserves Color and Shape + hides settings
function preciseHideUnwantedTabs() {
    console.log("Starting precise tab hiding (preserving Color and Shape, hiding settings)...");
    
    // Exact text matches to hide (case-sensitive)
    const exactTextsToHide = ['Visibility', 'Opacity', 'Scale', 'Axes', 'Animations'];
    
    // Exact text matches to preserve (case-insensitive)
    const exactTextsToKeep = ['color', 'shape'];
    
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
    
    // Method 2: Hide specific content panels by ID, but preserve color and shape
    const contentIdsToHide = [
        '#visibility-tab', '#opacity-tab', '#scale-tab', '#axes-tab', '#animations-tab',
        '#visibility', '#opacity', '#scale', '#axes', '#animations'
    ];
    
    contentIdsToHide.forEach(id => {
        const element = document.querySelector(id);
        if (element) {
            element.style.display = 'none';
            hiddenCount++;
            console.log(`Hidden content by ID: ${id}`);
        }
    });
    
    // Method 3: Force show Color and Shape elements
    const forceShowSelectors = [
        'a[href*="color"]', 'a[href*="shape"]',
        'button[data-target*="color"]', 'button[data-target*="shape"]',
        '[id*="color"]', '[id*="shape"]',
        '[aria-controls*="color"]', '[aria-controls*="shape"]'
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
                // Don't hide if it's related to color or shape
                const elementText = element.textContent.toLowerCase();
                if (!elementText.includes('color') && !elementText.includes('shape')) {
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
        
        // Don't hide if it's related to color or shape
        if (textContent.includes('color') || textContent.includes('shape')) {
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

# Precise CSS that doesn't use positional selectors + hides settings
precise_hide_css = """
<style>
/* Hide specific tab links by href patterns - but preserve color and shape */
a[href*="visibility"]:not([href*="color"]):not([href*="shape"]),
a[href*="opacity"]:not([href*="color"]):not([href*="shape"]),
a[href*="scale"]:not([href*="color"]):not([href*="shape"]),
a[href*="axes"]:not([href*="color"]):not([href*="shape"]),
a[href*="animation"]:not([href*="color"]):not([href*="shape"]) {
    display: none !important;
}

/* Hide specific content panels by ID - but preserve color and shape */
[id="visibility-tab"], [id="opacity-tab"], [id="scale-tab"],
[id="axes-tab"], [id="animations-tab"],
[id="visibility"], [id="opacity"], [id="scale"],
[id="axes"], [id="animations"] {
    display: none !important;
}

/* Hide by data-target attributes - but preserve color and shape */
button[data-target*="visibility"]:not([data-target*="color"]):not([data-target*="shape"]),
button[data-target*="opacity"]:not([data-target*="color"]):not([data-target*="shape"]),
button[data-target*="scale"]:not([data-target*="color"]):not([data-target*="shape"]),
button[data-target*="axes"]:not([data-target*="color"]):not([data-target*="shape"]),
button[data-target*="animation"]:not([data-target*="color"]):not([data-target*="shape"]) {
    display: none !important;
}

/* Hide settings button by common patterns */
.settings-btn, .gear-icon, .fa-gear, .fa-cog, .fa-settings,
button[title*="setting" i]:not([class*="color"]):not([class*="shape"]),
button[aria-label*="setting" i]:not([class*="color"]):not([class*="shape"]),
[data-toggle="modal"]:not([class*="color"]):not([class*="shape"]),
.btn[data-target*="setting" i]:not([class*="color"]):not([class*="shape"]) {
    display: none !important;
}

/* Hide toolbar buttons except essential ones */
.btn-toolbar button:not([class*="color"]):not([class*="shape"]):not(.btn-primary) {
    display: none !important;
}

/* Force show Color and Shape elements */
a[href*="color"], a[href*="shape"],
button[data-target*="color"], button[data-target*="shape"],
[id*="color"], [id*="shape"],
[aria-controls*="color"], [aria-controls*="shape"] {
    display: block !important;
    visibility: visible !important;
}

/* Alternative: Hide by aria-controls but preserve color and shape */
[aria-controls="visibility"], [aria-controls="opacity"],
[aria-controls="scale"], [aria-controls="axes"],
[aria-controls="animations"] {
    display: none !important;
}

/* Don't hide color and shape controls */
[aria-controls*="color"], [aria-controls*="shape"] {
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

# Debug function to see what's actually happening
debug_preservation_js = """
// Debug function to see what tabs are found and what we're doing to them
function debugTabPreservation() {
    console.log("\\n=== DEBUGGING TAB PRESERVATION ===");
    
    const allTabs = document.querySelectorAll('a, button, [role="tab"], .nav-link');
    console.log(`Found ${allTabs.length} potential tab elements`);
    
    allTabs.forEach((tab, index) => {
        const text = tab.textContent.trim();
        const href = tab.getAttribute('href') || '';
        const dataTarget = tab.getAttribute('data-target') || '';
        const ariaControls = tab.getAttribute('aria-controls') || '';
        const isVisible = window.getComputedStyle(tab).display !== 'none';
        
        if (text.length > 0 && text.length < 50) {
            console.log(`Tab ${index}: "${text}"`);
            console.log(`  href: "${href}"`);
            console.log(`  data-target: "${dataTarget}"`);
            console.log(`  aria-controls: "${ariaControls}"`);
            console.log(`  visible: ${isVisible}`);
            console.log(`  element:`, tab);
            console.log('---');
        }
    });
    
    // Specifically look for Color and Shape tabs
    const colorTabs = Array.from(allTabs).filter(tab => 
        tab.textContent.toLowerCase().includes('color')
    );
    const shapeTabs = Array.from(allTabs).filter(tab => 
        tab.textContent.toLowerCase().includes('shape')
    );
    
    console.log(`\\nColor tabs found: ${colorTabs.length}`);
    colorTabs.forEach(tab => console.log('  Color tab:', tab.textContent.trim(), tab));
    
    console.log(`\\nShape tabs found: ${shapeTabs.length}`);
    shapeTabs.forEach(tab => console.log('  Shape tab:', tab.textContent.trim(), tab));
    
    // Look for settings buttons
    const settingsButtons = Array.from(document.querySelectorAll('button, a')).filter(btn => {
        const innerHTML = btn.innerHTML.toLowerCase();
        const title = (btn.getAttribute('title') || '').toLowerCase();
        const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
        
        return innerHTML.includes('gear') || innerHTML.includes('cog') || 
               innerHTML.includes('setting') || title.includes('setting') ||
               ariaLabel.includes('setting') || innerHTML.includes('⚙');
    });
    
    console.log(`\\nSettings buttons found: ${settingsButtons.length}`);
    settingsButtons.forEach(btn => console.log('  Settings button:', btn.textContent.trim(), btn));
}

setTimeout(debugTabPreservation, 2000);
setTimeout(debugTabPreservation, 6000);
"""

# Add this debugging code right after the VARIABLE_DESCRIPTIONS definition:
debug_descriptions_js = f"""
// Debug: Check if descriptions are properly defined
console.log("=== DEBUGGING VARIABLE DESCRIPTIONS ===");
console.log("Variable1:", {escape_for_js(variable1)});
console.log("Variable2:", {escape_for_js(variable2)});

const testDescriptions = {dict_to_js_object(VARIABLE_DESCRIPTIONS)};
console.log("Total descriptions loaded:", Object.keys(testDescriptions).length);
console.log("Variable1 description:", testDescriptions[{escape_for_js(variable1)}]);
console.log("Variable2 description:", testDescriptions[{escape_for_js(variable2)}]);

const testSheetDescriptions = {dict_to_js_object(SHEET_DESCRIPTIONS)};
console.log("Sheet descriptions:", testSheetDescriptions);
"""

# Fix the overlay JavaScript by escaping variables in Python first
overlay_js = f"""
// Create information overlays
function createInfoOverlays() {{
  console.log("=== CREATING INFO OVERLAYS ===");
  
  // Get variable descriptions
  const variableDescriptions = {dict_to_js_object(VARIABLE_DESCRIPTIONS)};
  const sheetDescriptions = {dict_to_js_object(SHEET_DESCRIPTIONS)};
  
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
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Color Variable</div>
      <div style="font-weight: bold; color: #0066cc; margin-bottom: 5px;">{escape_for_js(variable1)}</div>
      <div style="color: #555; margin-bottom: 15px;">${{var1Description}}</div>
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
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Shape Variable</div>
      <div style="font-weight: bold; color: #0066cc; margin-bottom: 5px;">{escape_for_js(variable2)}</div>
      <div style="color: #555; margin-bottom: 15px;">${{var2Description}}</div>
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
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Taxa</div>
      <div style="font-weight: bold; color: #0066cc; margin-bottom: 5px;">{escape_for_js(dependentvar)}</div>
      <div style="color: #555; margin-bottom: 15px;">${{sheetDescription}}</div>
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
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Study Information</div>
      <div style="color: #555; margin-bottom: 15px;">${{overlay4Description}}</div>
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
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;">HEI2015 Information</div>
      <div style="color: #555; margin-bottom: 15px;">${{overlay5Description}}</div>
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
      <div style="font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px;">FFQ Information</div>
      <div style="color: #555; margin-bottom: 15px;">${{overlay6Description}}</div>
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

// Create overlays when page loads
setTimeout(createInfoOverlays, 2000);

// Recreate overlays if they get removed by dynamic content
setInterval(function() {{
  if (document.querySelectorAll('.info-overlay').length < 3) {{
    createInfoOverlays();
  }}
}}, 5000);
"""


# Combine the precise solution
complete_precise_solution = precise_hide_js + "\n\n" + debug_preservation_js

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