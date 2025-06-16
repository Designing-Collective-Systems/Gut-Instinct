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