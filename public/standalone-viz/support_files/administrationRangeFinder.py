import pandas as pd
import numpy as np

def classify_administration(df, column_name):
    """Classify administration types into specified categories"""
    def categorize_administration(admin_value):
        # print(admin_value)
        if pd.isna(admin_value):
            return "f. nan"
        try:
            admin_str = str(admin_value).strip()
            if admin_str == 'Control':
                return "a. Control"
            elif admin_str == 'Untreated':
                return "b. Untreated"
            elif admin_str == 'Infused':
                return "c. Infused"
            elif admin_str == 'Oral':
                return "d. Oral"
            elif admin_str == 'Subcutaneous':
                return "e. Subcutaneous"
            else:
                return "f. nan"
        except (ValueError, TypeError):
            return "f. nan"
    
    # Apply the classification
    df[column_name] = df[column_name].apply(categorize_administration)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df