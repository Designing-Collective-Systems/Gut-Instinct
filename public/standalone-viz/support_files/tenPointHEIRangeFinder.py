import pandas as pd
import numpy as np

def convert_ten_point_HEI_to_grades(df, column_name):
    """Convert ten point HEI values to grades"""
    
    def categorize_ten_point_values(ten_point_value):
        if pd.isna(ten_point_value):
            return np.nan
        try:
            score = float(ten_point_value)
            if score < 6:
                return "a. Major Dietary Deficiency of " + column_name
            elif score < 7:
                return "b. Poor Dietary Deficiency of " + column_name
            elif score < 8:
                return "c. Fair Dietary Intake of " + column_name
            elif score < 9:
                return "d. Good Dietary Intake of " + column_name
            else:
                return "e. Excellent Dietary Intake of " + column_name
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_ten_point_values)
    return df

def sort_ten_point_HEI_categories(ranges, variable_name):
    """Sort 10 point categories in proper life stage order"""
    if variable_name == 'WHOLEGRAIN' or variable_name == 'TOTALDAIRY' or variable_name == 'FATTYACID' or variable_name == 'SODIUM' or variable_name == 'REFINEDGRAIN' or variable_name == 'ADDSUG' or variable_name == 'SFA':
        # Define the proper order for 10 point categories
        ten_point_order = ["a. Major Dietary Deficiency of " + variable_name, 
                     "b. Poor Dietary Deficiency of " + variable_name, 
                     "c. Fair Dietary Intake of " + variable_name,
                     "d. Good Dietary Intake of " + variable_name,
                     "e. Excellent Dietary Intake of " + variable_name]
        # Sort based on the predefined order, keeping any other values at the end
        sorted_ranges = []
        for category in ten_point_order:
            if category in ranges:
                sorted_ranges.append(category)
        # Add any unexpected categories at the end
        for category in ranges:
            if category not in sorted_ranges:
                sorted_ranges.append(category)
        return sorted_ranges
    else:
        return ranges