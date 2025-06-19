import pandas as pd

def classify_sex(df, column_name):
    """Classify sex into categories with Female first"""
    def categorize_sex(sex_value):
        print(sex_value)
        if pd.isna(sex_value):
            return "c. nan"
        try:
            sex_str = str(sex_value).strip()
            if sex_str == 'F':
                return "a. Female"
            elif sex_str == 'M':
                return "b. Male"
            else:
                return "c. nan"
        except (ValueError, TypeError):
            return "c. nan"
    
    df[column_name] = df[column_name].apply(categorize_sex)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df