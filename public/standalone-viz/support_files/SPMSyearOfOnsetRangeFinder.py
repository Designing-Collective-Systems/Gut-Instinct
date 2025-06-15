import pandas as pd
import numpy as np

def classify_yearOfSPMSOnset(df, column_name):
    """Classify year of onset of SPMS"""
    
    def categorize_yearOfSPMSOnset(year_value):
        # print(year_value)
        if pd.isna(year_value):
            return "g. nan"
        try:
            if year_value == 'Unknown' or year_value == 'unkown' or year_value == "not recorded":
                return "f. Unknown"
            elif year_value == '35 years ago':
                return "a. 1983 - 1989"
            else:
                year = float(year_value)
                if year <= 1989:
                    return "a. 1983 - 1989"
                elif year <= 1996:
                    return "b. 1990 - 1996"
                elif year <= 2003:
                    return "c. 1997 - 2003"
                elif year <= 2010:
                    return "d. 2004 - 2010"
                else:
                    return "e. 2011 - 2017"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_yearOfSPMSOnset)
    return df