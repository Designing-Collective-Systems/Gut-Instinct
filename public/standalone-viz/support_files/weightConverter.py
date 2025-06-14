import pandas as pd
import numpy as np

def convert_weightKG_to_WeightLbs(df, column_name):
    """Convert weight values from kg to lbs and categorize into weight ranges"""
    if column_name != 'Weight' or column_name not in df.columns:
        return df
    
    def convert_and_categorize_weight(weight_value):
        if pd.isna(weight_value):
            return np.nan
        try:
            weight_kg = float(weight_value)
            weight_lbs = weight_kg * 2.20462  # 1 kg = 2.20462 lbs
            
            # Categorize into 5 weight ranges (in lbs)
            if weight_lbs < 110:
                return "a. Less than 110 lbs"
            elif weight_lbs < 140:
                return "b. 110-139 lbs"
            elif weight_lbs < 170:
                return "c. 140-169 lbs"
            elif weight_lbs < 200:
                return "d. 170-199 lbs"
            else:
                return "e. More than 200 lbs"
                
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(convert_and_categorize_weight)
    return df