import pandas as pd
import numpy as np

def classify_treatmentStatus(df, column_name):
    """Classify treatment status into specified categories"""
    def categorize_treatmentStatus(status_value):
        # print(status_value)
        if pd.isna(status_value):
            return "e. nan"
        try:
            status_str = str(status_value).strip()
            if status_str == 'Untreated_HHC':
                return "a. Untreated_HHC"
            elif status_str == 'Treated_HHC':
                return "b. Treated_HHC"
            elif status_str == 'Untreated':
                return "c. Untreated"
            elif status_str == 'Treated':
                return "d. Treated"
            else:
                return "e. nan"
        except (ValueError, TypeError):
            return "e. nan"
    
    df[column_name] = df[column_name].apply(categorize_treatmentStatus)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df