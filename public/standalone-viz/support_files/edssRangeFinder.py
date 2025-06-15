import pandas as pd
import numpy as np

def classify_EDSS(df, column_name):
    """Classify Expanded Disability Status Scale into 5 levels"""
    def categorize_EDSS(edss_value):
        print(edss_value)
        if pd.isna(edss_value):
            return "f. nan"
        try:
            edss = float(edss_value)
            if edss <= 2.5:
                return "a. Minimal disability with MS"
            elif edss <= 4.5:
                return "b. Mild disability with MS"
            elif edss <= 6.5:
                return "c. Moderate disability with MS"
            elif edss <= 8.5:
                return "d. Severe disability with MS"
            else:
                return "e. Very severe disability with or death by MS"
        except (ValueError, TypeError):
            return "f. nan"
    
    df[column_name] = df[column_name].apply(categorize_EDSS)
    return df