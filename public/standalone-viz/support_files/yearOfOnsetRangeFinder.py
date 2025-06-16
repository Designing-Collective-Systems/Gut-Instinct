import pandas as pd
import numpy as np

def classify_yearOfOnset(df, column_name):
    """Classify year of onset of MS"""
    
    def categorize_yearOfOnset(year_value):
        print(year_value)
        if pd.isna(year_value):
            return "a. nan"
        try:
            if year_value == 'Unclear':
                return "b. Unclear"
            else:
                year = float(year_value)
                if year <= 1974:
                    return "g. 1963 - 1974"
                elif year <= 1985:
                    return "f. 1975 - 1985"
                elif year <= 1996:
                    return "e. 1986 - 1996"
                elif year <= 2007:
                    return "d. 1997 - 2007"
                else:
                    return "c. 2008 - 2018"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_yearOfOnset)
    return df