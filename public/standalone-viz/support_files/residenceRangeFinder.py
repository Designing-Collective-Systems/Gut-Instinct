import pandas as pd

def classify_residence(df, column_name):
    """Classify residence into alphabetical categories"""
    def categorize_residence(residence_value):
        print(residence_value)
        if pd.isna(residence_value):
            return "h. nan"
        try:
            residence_str = str(residence_value).strip()
            if residence_str == 'Boston':
                return "a. Boston"
            elif residence_str == 'Buenos Aires':
                return "b. Buenos Aires"
            elif residence_str == 'Edinburgh':
                return "c. Edinburgh"
            elif residence_str == 'New York':
                return "d. New York"
            elif residence_str == 'Pittsburgh':
                return "e. Pittsburgh"
            elif residence_str == 'San Francisco':
                return "f. San Francisco"
            elif residence_str == 'San Sebastian':
                return "g. San Sebastian"
            else:
                return "h. nan"
        except (ValueError, TypeError):
            return "h. nan"
    
    df[column_name] = df[column_name].apply(categorize_residence)
    return df