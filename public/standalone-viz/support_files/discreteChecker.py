import pandas as pd
import numpy as np
from .variableDescriptions import DISCRETE_VARIABLES, FORCE_CONTINUOUS

def is_discrete_variable(variable_name, data_series):
    """
    Determine if a variable should be treated as discrete based on:
    1. Forced continuous variables (always continuous)
    2. Predefined list of discrete variables
    3. Data type (string/object columns are discrete)
    4. Number of unique values relative to total samples (for original numeric data)
    """
    # Check forced continuous variables first
    if variable_name in FORCE_CONTINUOUS:
        return False
    
    # Check predefined discrete variables
    if variable_name in DISCRETE_VARIABLES:
        return True
    
    # If no data provided, default to discrete
    if data_series is None or len(data_series) == 0:
        return True
    
    # Check if data is non-numeric (strings/categories)
    if data_series.dtype == 'object' or data_series.dtype.name.startswith('str'):
        return True
    
    # For numeric data, check the characteristics of the original data
    non_null_data = data_series.dropna()
    if len(non_null_data) == 0:
        return True
    
    unique_values = non_null_data.unique()
    num_unique = len(unique_values)
    total_samples = len(non_null_data)
    
    # If fewer than 8 unique values total, treat as discrete
    # This catches small categorical scales (1-5 ratings, etc.)
    if num_unique < 8:
        return True
    
    # Check if all values are integers and there aren't many of them
    # This catches things like Likert scales, small counts, etc.
    if all(float(val).is_integer() for val in unique_values if not pd.isna(val)):
        # If range is small (less than 15) and most values are represented, treat as discrete
        value_range = max(unique_values) - min(unique_values)
        if value_range < 15 and num_unique > (value_range * 0.5):
            return True
    
    # If less than 15% of values are unique, treat as discrete
    # This is more restrictive than before to avoid misclassifying continuous variables
    unique_ratio = num_unique / total_samples
    if unique_ratio < 0.15:
        return True
    
    # If we have many unique values and they're spread out, treat as continuous
    return False