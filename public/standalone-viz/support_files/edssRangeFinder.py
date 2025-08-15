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
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df