import pandas as pd
import numpy as np

def classify_trinary_2(df, column_name):
    """Classify trinary values into Yes/No/Null categories"""
    def categorize_trinary_2(binary_value):
        # print(binary_value)
        if pd.isna(binary_value):
            return "a. nan"
        try:
            value_str = str(binary_value).strip().lower()
            if value_str == 'yes':
                return "b. Yes"
            elif value_str == 'no':
                return "c. No"
            else:
                return "a. nan"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_trinary_2)
    return df