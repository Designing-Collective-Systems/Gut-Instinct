import pandas as pd
import numpy as np

def classify_typeOfMS(df, column_name):
    """Classify type of MS into specified categories"""
    def categorize_typeOfMS(type_value):
        # print(type_value)
        if pd.isna(type_value):
            return "e. nan"
        try:
            type_str = str(type_value).strip()
            if type_str == 'Control_RRMS':
                return "a. Control_RRMS"
            elif type_str == 'Control_PMS':
                return "b. Control_PMS"
            elif type_str == 'RRMS':
                return "c. RRMS"
            elif type_str == 'PMS':
                return "d. PMS"
            else:
                return "e. nan"
        except (ValueError, TypeError):
            return "e. nan"
    
    df[column_name] = df[column_name].apply(categorize_typeOfMS)
    return df