import pandas as pd
import numpy as np

def classify_roommates(df, column_name):
    """Classify number of roommates into ordered categories"""
    def categorize_roommates(roommates_value):
        print(roommates_value)
        if pd.isna(roommates_value):
            return "a. nan"
        try:
            roommates = int(float(roommates_value))
            if roommates == 1:
                return "b. 1 roommate"
            elif roommates == 2:
                return "c. 2 roommates"
            else:
                return "a. nan"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_roommates)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df