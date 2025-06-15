import pandas as pd
import numpy as np

def classify_vitamin_d(df, column_name):
    """Classify Vitamin D (IU) into 3 levels plus null"""
    def categorize_vitamin_d(vitamin_d_value):
        # print(vitamin_d_value)
        # Check for various types of empty/null values
        if (pd.isna(vitamin_d_value) or 
            vitamin_d_value == "" or 
            vitamin_d_value == " " or
            str(vitamin_d_value).strip() == "" or
            str(vitamin_d_value).strip().lower() == "nan" or
            vitamin_d_value is None):
            return "d. nan"
        try:
            vitamin_d_amount = float(vitamin_d_value)
            if 0 <= vitamin_d_amount < 400:
                return "c. POOR Vitamin D intake"
            elif 400 <= vitamin_d_amount < 600:
                return "b. GOOD Vitamin D intake"
            elif 600 <= vitamin_d_amount <= 800:
                return "a. EXCELLENT Vitamin D intake"
            else:
                return "d. nan"
        except (ValueError, TypeError):
            return "d. nan"
    
    df[column_name] = df[column_name].apply(categorize_vitamin_d)
    return df