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