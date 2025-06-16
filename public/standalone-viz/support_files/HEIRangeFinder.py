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