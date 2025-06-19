import pandas as pd

def classify_ethnicity(df, column_name):
    """Classify ethnicity into categories with null first"""
    def categorize_ethnicity(ethnicity_value):
        print(ethnicity_value)
        if pd.isna(ethnicity_value):
            return "a. null"
        try:
            ethnicity_str = str(ethnicity_value).strip()
            if ethnicity_str == 'Asian':
                return "b. Asian"
            elif ethnicity_str == 'Black':
                return "c. Black"
            elif ethnicity_str == 'Caucasian/Hispanic':
                return "d. Caucasian/Hispanic"
            else:
                return "a. null"
        except (ValueError, TypeError):
            return "a. null"
    
    df[column_name] = df[column_name].apply(categorize_ethnicity)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df