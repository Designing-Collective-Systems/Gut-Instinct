import pandas as pd
import numpy as np

def classify_bmi(df, column_name):
    """Convert bmi values """
    if column_name != 'bmi' or column_name not in df.columns:
        return df
    
    def categorize_bmi(bmi_value):
        if pd.isna(bmi_value):
            return np.nan
        try:
            bmi = float(bmi_value)
            if bmi < 18.5:
                return "a. Underweight"
            elif bmi < 25:
                return "b. Normal weight"
            elif bmi < 30:
                return "c. Overweight"
            else:
                return "d. Obese"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_bmi)
    return df

def sort_bmi_categories(ranges, variable_name):
    """Sort bmi categories"""
    if variable_name == 'bmi':
        # Define the proper order for bmi categories
        bmi_order = ["a. Underweight", "b. Normal weight", "c. Overweight", "d. Obese"]
        # Sort based on the predefined order, keeping any other values at the end
        sorted_ranges = []
        for category in bmi_order:
            if category in ranges:
                sorted_ranges.append(category)
        # Add any unexpected categories at the end
        for category in ranges:
            if category not in sorted_ranges:
                sorted_ranges.append(category)
        return sorted_ranges
    else:
        return ranges