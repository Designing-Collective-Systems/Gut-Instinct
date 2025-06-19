import pandas as pd
import numpy as np

def classify_otc_medications(df, column_name):
    """Classify over the counter medications count into ordered categories"""
    def categorize_otc_medications(otc_value):
        print(otc_value)
        if pd.isna(otc_value):
            return "a. nan"
        try:
            otc_count = int(float(otc_value))
            if otc_count == 0:
                return "b. 0 medications"
            elif otc_count < 1:
                return "c. 1 medication"
            elif otc_count == 2:
                return "d. 2 medications"
            elif otc_count == 3:
                return "e. 3 medications"
            elif otc_count == 4:
                return "f. 4 medications"
            elif otc_count >= 5:
                return "g. 5+ medications"
            else:
                return "a. nan"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_otc_medications)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df