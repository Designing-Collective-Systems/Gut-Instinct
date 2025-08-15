import pandas as pd
import numpy as np

def classify_smoking_status(df, column_name):
    """Classify smoking status into ordered categories"""
    def categorize_smoking_status(smoking_value):
        print(smoking_value)
        if pd.isna(smoking_value):
            return "a. nan"
        try:
            smoking_str = str(smoking_value).strip().lower()
            if smoking_str == 'nonsmoker':
                return "b. Non smoker"
            elif smoking_str == 'formersmoker':
                return "c. Former smoker"
            elif smoking_str == 'smoker':
                return "d. Smoker"
            else:
                return "a. nan"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_smoking_status)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df