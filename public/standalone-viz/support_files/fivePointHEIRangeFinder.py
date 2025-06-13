import pandas as pd
import numpy as np

def convert_five_point_HEI_to_grades(df, column_name):
    """Convert five point HEI values to grades"""
    
    def categorize_five_point_values(five_point_value):
        if pd.isna(five_point_value):
            return np.nan
        try:
            score = float(five_point_value)
            if score < 3:
                return "a. Major Dietary Deficiency of " + column_name
            elif score < 3.5:
                return "b. Poor Dietary Deficiency of " + column_name
            elif score < 4:
                return "c. Fair Dietary Intake of " + column_name
            elif score < 4.5:
                return "d. Good Dietary Intake of " + column_name
            else:
                return "e. Excellent Dietary Intake of " + column_name
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_five_point_values)
    return df

def sort_five_point_HEI_categories(ranges, variable_name):
    """Sort age categories in proper life stage order"""
    if variable_name == 'TOTALVEG' or variable_name == 'GREEN_AND_BEAN' or variable_name == 'TOTALFRUIT' or variable_name == 'WHOLEFRUIT' or variable_name == 'TOTPROT' or variable_name == 'SEAPLANT_PROT':
        # Define the proper order for age categories
        age_order = ["a. Major Dietary Deficiency of " + variable_name, 
                     "b. Poor Dietary Deficiency of " + variable_name, 
                     "c. Fair Dietary Intake of " + variable_name,
                     "d. Good Dietary Intake of " + variable_name,
                     "e. Excellent Dietary Intake of " + variable_name]
        # Sort based on the predefined order, keeping any other values at the end
        sorted_ranges = []
        for category in age_order:
            if category in ranges:
                sorted_ranges.append(category)
        # Add any unexpected categories at the end
        for category in ranges:
            if category not in sorted_ranges:
                sorted_ranges.append(category)
        return sorted_ranges
    else:
        return ranges