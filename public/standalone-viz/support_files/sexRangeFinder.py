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
    return df