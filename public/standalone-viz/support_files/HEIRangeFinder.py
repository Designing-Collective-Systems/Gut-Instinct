import pandas as pd
import numpy as np

def convert_HEI_score_to_grades(df, column_name):
    """Convert 100 point HEI value to grades"""
    
    def categorize_HEI_point_values(hundred_point_value):
        if pd.isna(hundred_point_value):
            return np.nan
        try:
            score = float(hundred_point_value)
            if score < 60:
                return "a. Really Poor Diet Quality"
            elif score < 70:
                return "b. Poor Diet Quality"
            elif score < 80:
                return "c. Fair Diet Quality"
            elif score < 90:
                return "d. Good Diet Quality"
            else:
                return "e. Excellent Diet Quality"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_HEI_point_values)
    return df

def sort_HEI_categories(ranges, variable_name):
    """Sort HEI categories in proper life stage order"""
    if variable_name == 'HEI2015_TOTAL_SCORE':
        # Define the proper order for HEI categories
        hundered_point_order = ["a. Really Poor Diet Quality", 
                     "b. Poor Diet Quality", 
                     "c. Fair Diet Quality",
                     "d. Good Diet Quality",
                     "e. Excellent Diet Quality"]
        # Sort based on the predefined order, keeping any other values at the end
        sorted_ranges = []
        for category in hundered_point_order:
            if category in ranges:
                sorted_ranges.append(category)
        # Add any unexpected categories at the end
        for category in ranges:
            if category not in sorted_ranges:
                sorted_ranges.append(category)
        return sorted_ranges
    else:
        return ranges