import pandas as pd
import numpy as np

def classify_numberOfChildren(df, column_name):
    """Classify number of children into ordered categories"""
    def categorize_numberOfChildren(children_value):
        print(children_value)
        if pd.isna(children_value):
            return "a. nan"
        try:
            children = int(float(children_value))
            if children == 1:
                return "b. 1 child"
            elif children == 2:
                return "c. 2 children"
            elif children == 3:
                return "d. 3 children"
            elif children == 4:
                return "e. 4 children"
            else:
                return "a. nan"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_numberOfChildren)
    return df