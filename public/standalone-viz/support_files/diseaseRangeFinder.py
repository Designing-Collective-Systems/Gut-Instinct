import pandas as pd
import numpy as np

def classify_disease(df, column_name):
    """Classify disease into categories with Control first"""
    def categorize_disease(disease_value):
        print(disease_value)
        if pd.isna(disease_value):
            return "c. nan"
        try:
            disease_str = str(disease_value).strip()
            if disease_str == 'Control':
                return "a. Control"
            elif disease_str == 'MS':
                return "b. MS"
            else:
                return "c. nan"
        except (ValueError, TypeError):
            return "c. nan"
    
    df[column_name] = df[column_name].apply(categorize_disease)
    return df