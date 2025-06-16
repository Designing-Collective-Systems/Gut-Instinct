import pandas as pd
import numpy as np

def convert_age_to_life_stages(df, column_name):
    """Convert age values to life stage categories"""
    if column_name != 'Age' or column_name not in df.columns:
        return df
    
    def categorize_age(age_value):
        if pd.isna(age_value):
            return np.nan
        try:
            age = float(age_value)
            if age < 35:
                return "a. Young adults"
            elif age < 55:
                return "b. Middle age adults"
            else:
                return "c. Older adults"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_age)
    return df