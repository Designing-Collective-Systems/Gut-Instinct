import pandas as pd
import numpy as np

def convert_ten_point_HEI_to_grades(df, column_name):
    """Convert ten point HEI values to grades"""
    
    def categorize_ten_point_values(ten_point_value):
        if pd.isna(ten_point_value):
            return "a. nan"
        try:
            score = float(ten_point_value)
            if score < 6:
                return "f. Major Dietary Deficiency of " + column_name
            elif score < 7:
                return "e. Poor Dietary Deficiency of " + column_name
            elif score < 8:
                return "d. Fair Dietary Intake of " + column_name
            elif score < 9:
                return "c. Good Dietary Intake of " + column_name
            else:
                return "b. Excellent Dietary Intake of " + column_name
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_ten_point_values)
    return df