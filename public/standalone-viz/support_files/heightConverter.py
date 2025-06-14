import pandas as pd
import numpy as np

def convert_heightCM_to_HeightInches(df, column_name):
    """Convert height values from cm to feet and inches and categorize into height ranges"""
    if column_name != 'Height' or column_name not in df.columns:
        return df
    
    def convert_and_categorize_height(height_value):
        if pd.isna(height_value):
            return np.nan
        try:
            height_cm = float(height_value)
            total_inches = height_cm / 2.54  # 1 inch = 2.54 cm
            
            # Categorize into 5 height ranges (in feet and inches)
            # Range: 144.78 cm (4'9") to 255.7 cm (8'4")
            if total_inches < 62:  # < 5'2"
                return "a. Smaller than 5'2\""
            elif total_inches < 66:  # 5'2" to 5'5"
                return "b. 5'2\" - 5'5\""
            elif total_inches < 70:  # 5'6" to 5'9"
                return "c. 5'6\" - 5'9\""
            elif total_inches < 74:  # 5'10" to 6'1"
                return "d. 5'10\" - 6'1\""
            else:  # ≥ 6'2"
                return "e. Taller than 6'2\""
                
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(convert_and_categorize_height)
    return df