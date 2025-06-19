import pandas as pd
import numpy as np

def classify_binary(df, column_name):
    """Classify binary values into Yes/No categories"""
    def categorize_binary(binary_value):
        # print(binary_value)
        if pd.isna(binary_value):
            return "c. nan"
        try:
            value = float(binary_value)
            if value == 1:
                return "a. Yes"
            elif value == 0:
                return "b. No"
            else:
                return "c. nan"
        except (ValueError, TypeError):
            return "c. nan"
    
    df[column_name] = df[column_name].apply(categorize_binary)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df