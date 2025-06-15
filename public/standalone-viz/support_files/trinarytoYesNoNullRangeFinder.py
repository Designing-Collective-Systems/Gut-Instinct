import pandas as pd
import numpy as np

def classify_trinary(df, column_name):
    """Classify trinary values into Yes/No/Null categories"""
    def categorize_trinary(binary_value):
        # print(binary_value)
        if pd.isna(binary_value):
            return "a. nan"
        try:
            value = float(binary_value)
            if value == 1:
                return "b. Yes"
            elif value == 0:
                return "c. No"
            else:
                return "a. nan"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_trinary)
    return df