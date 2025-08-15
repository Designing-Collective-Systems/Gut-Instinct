import pandas as pd
import numpy as np

def classify_education_level(df, column_name):
    """Classify education level into ordered categories"""
    def categorize_education_level(education_value):
        print(education_value)
        if pd.isna(education_value):
            return "a. nan"
        try:
            education_str = str(education_value).strip()
            if education_str == 'Some High School':
                return "b. Some High School"
            elif education_str == 'High School Graduate':
                return "c. High School Graduate"
            elif education_str == 'Some College/Technical Degree':
                return "d. Some College/Technical Degree"
            elif education_str == 'College/University Degree':
                return "e. College/University Degree"
            elif education_str == 'Post-Graduate Education':
                return "f. Post-Graduate Education"
            else:
                return "a. nan"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_education_level)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df