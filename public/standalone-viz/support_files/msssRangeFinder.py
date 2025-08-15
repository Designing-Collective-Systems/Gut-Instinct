import pandas as pd
import numpy as np

def classify_MSSS(df, column_name):
    """Classify Multiple Sclerosis Severity Score into 5 severity levels"""
    def categorize_MSSS(msss_value):
        print(msss_value)
        if pd.isna(msss_value):
            return "a. nan"
        try:
            msss = float(msss_value)
            if msss <= 2.0:
                return "b. Very mild severity with MS"
            elif msss <= 4.0:
                return "c. Mild severity with MS"
            elif msss <= 6.0:
                return "d. Moderate severity with MS"
            elif msss <= 8.0:
                return "e. High severity with MS"
            else:
                return "f. Very high severity with or deathy by MS"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_MSSS)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df