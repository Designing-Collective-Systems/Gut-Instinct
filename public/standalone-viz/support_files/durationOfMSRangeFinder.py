import pandas as pd
import numpy as np

def classify_durationOfMS(df, column_name):
    """Classify duration of MS into ranges"""
    def categorize_durationOfMS(duration_value):
        print(duration_value)
        if pd.isna(duration_value):
            return "a. nan"
        try:
            duration = float(duration_value)
            if duration <= 10:
                return "b. 0 - 10 years"
            elif duration <= 20:
                return "c. 11 - 20 years"
            elif duration <= 30:
                return "d. 21 - 30 years"
            elif duration <= 40:
                return "e. 31 - 40 years"
            else:
                return "f. 41 - 53 years"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_durationOfMS)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df