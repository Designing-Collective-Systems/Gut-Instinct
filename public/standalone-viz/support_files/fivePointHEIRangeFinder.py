import pandas as pd
import numpy as np

def convert_five_point_HEI_to_grades(df, column_name):
    """Convert five point HEI values to grades"""
    
    def categorize_five_point_values(five_point_value):
        if pd.isna(five_point_value):
            return "a. nan"
        try:
            score = float(five_point_value)
            if score < 3:
                return "f. Major Dietary Deficiency of " + column_name
            elif score < 3.5:
                return "e. Poor Dietary Deficiency of " + column_name
            elif score < 4:
                return "d. Fair Dietary Intake of " + column_name
            elif score < 4.5:
                return "c. Good Dietary Intake of " + column_name
            else:
                return "b. Excellent Dietary Intake of " + column_name
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_five_point_values)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df