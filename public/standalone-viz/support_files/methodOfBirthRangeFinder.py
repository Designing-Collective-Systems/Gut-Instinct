import pandas as pd
import numpy as np

def classify_methodOfBirth(df, column_name):
    """Classify method of birth into alphabetical categories"""
    def categorize_methodOfBirth(birth_value):
        print(birth_value)
        if pd.isna(birth_value):
            return "a. nan"
        try:
            birth_str = str(birth_value).strip()
            if birth_str == 'Caesarean Section':
                return "b. Caesarean Section"
            elif birth_str == 'Vaginal Delivery':
                return "c. Vaginal Delivery"
            else:
                return "a. nan"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_methodOfBirth)
    return df