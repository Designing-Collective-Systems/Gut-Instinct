import pandas as pd
import numpy as np

def convert_HEI_score_to_grades(df, column_name):
    """Convert 100 point HEI value to grades"""
    
    def categorize_HEI_point_values(hundred_point_value):
        if pd.isna(hundred_point_value):
            return "a. nan"
        try:
            score = float(hundred_point_value)
            if score < 60:
                return "f. Really Poor Diet Quality"
            elif score < 70:
                return "e. Poor Diet Quality"
            elif score < 80:
                return "d. Fair Diet Quality"
            elif score < 90:
                return "c. Good Diet Quality"
            else:
                return "b. Excellent Diet Quality"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_HEI_point_values)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df