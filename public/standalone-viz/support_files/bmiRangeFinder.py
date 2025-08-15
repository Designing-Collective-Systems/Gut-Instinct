import pandas as pd
import numpy as np

def classify_bmi(df, column_name):
    """Convert bmi values """
    if column_name != 'Body Mass Index' or column_name not in df.columns:
        return df
    
    def categorize_bmi(bmi_value):
        if pd.isna(bmi_value):
            return np.nan
        try:
            bmi = float(bmi_value)
            if bmi < 18.5:
                return "a. Underweight"
            elif bmi < 25:
                return "b. Normal weight"
            elif bmi < 30:
                return "c. Overweight"
            else:
                return "d. Obese"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_bmi)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df