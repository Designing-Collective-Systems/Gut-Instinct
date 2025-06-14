import pandas as pd
import numpy as np

def classify_yearOfOnset(df, column_name):
    """Classify year of onset of MS"""
    
    def categorize_yearOfOnset(year_value):
        print(year_value)
        if pd.isna(year_value):
            return "g. nan"
        try:
            if year_value == 'Unclear':
                return "f. Unclear"
            else:
                year = float(year_value)
                if year <= 1974:
                    return "a. 1963 - 1974"
                elif year <= 1985:
                    return "b. 1975 - 1985"
                elif year <= 1996:
                    return "c. 1986 - 1996"
                elif year <= 2007:
                    return "d. 1997 - 2007"
                else:
                    return "e. 2008 - 2018"
        except (ValueError, TypeError):
            return np.nan
    
    df[column_name] = df[column_name].apply(categorize_yearOfOnset)
    return df

def sort_year_categories(ranges, variable_name):
    """Sort year categories"""
    if variable_name == 'year_of_onset':
        # Define the proper order for year of onset categories
        year_order = ["a. 1963 - 1974", "b. 1975 - 1985", "c. 1986 - 1996", "d. 1997 - 2007", "e. 2008 - 2018", "f. Unclear", "g. nan"]
        # Sort based on the predefined order, keeping any other values at the end
        sorted_ranges = []
        for category in year_order:
            if category in ranges:
                sorted_ranges.append(category)
        # Add any unexpected categories at the end
        for category in ranges:
            if category not in sorted_ranges:
                sorted_ranges.append(category)
        return sorted_ranges
    else:
        return ranges