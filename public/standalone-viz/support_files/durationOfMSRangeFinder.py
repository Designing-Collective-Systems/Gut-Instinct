import pandas as pd
import numpy as np

def classify_durationOfMS(df, column_name):
    """Classify duration of MS into ranges"""
    def categorize_durationOfMS(duration_value):
        print(duration_value)
        if pd.isna(duration_value):
            return "f. nan"
        try:
            duration = float(duration_value)
            if duration <= 10:
                return "a. 0 - 10 years"
            elif duration <= 20:
                return "b. 11 - 20 years"
            elif duration <= 30:
                return "c. 21 - 30 years"
            elif duration <= 40:
                return "d. 31 - 40 years"
            else:
                return "e. 41 - 53 years"
        except (ValueError, TypeError):
            return "f. nan"
    
    df[column_name] = df[column_name].apply(categorize_durationOfMS)
    return df