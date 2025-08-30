import pandas as pd
import numpy as np

def convert_age_to_life_stages(df, column_name):
    """Convert age values to life stage categories"""
    if column_name != 'Age' or column_name not in df.columns:
        return df
    
    def categorize_age(age_value):
        if pd.isna(age_value):
            return np.nan
        try:
            age = float(age_value)
            if age < 35:
                return "a. Young adults"
            elif age < 55:
                return "b. Middle age adults"
            else:
                return "c. Older adults"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_age)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category}"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df