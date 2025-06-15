import pandas as pd
import numpy as np

def classify_binary(df, column_name):
    """Classify binary values into Yes/No categories"""
    def categorize_binary(binary_value):
        # print(binary_value)
        if pd.isna(binary_value):
            return "c. nan"
        try:
            value = float(binary_value)
            if value == 1:
                return "a. Yes"
            elif value == 0:
                return "b. No"
            else:
                return "c. nan"
        except (ValueError, TypeError):
            return "c. nan"
    
    df[column_name] = df[column_name].apply(categorize_binary)
    return df