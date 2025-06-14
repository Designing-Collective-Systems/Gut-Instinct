import pandas as pd
import numpy as np

def convert_age_to_life_stages(df, column_name):
    """Convert age values to life stage categories"""
    if column_name != 'Age' or column_name not in df.columns:
        return df
    
    def categorize_age(age_value):
        if pd.isna(age_value):
            return np.nan
        try:
            age = float(age_value)
            if age < 35:
                return "a. Young adults"
            elif age < 55:
                return "b. Middle age adults"
            else:
                return "c. Older adults"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_age)
    return df

def sort_age_categories(ranges, variable_name):
    """Sort age categories in proper life stage order"""
    if variable_name == 'Age':
        # Define the proper order for age categories
        age_order = ["a. Young adults", "b. Middle age adults", "c. Older adults"]
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