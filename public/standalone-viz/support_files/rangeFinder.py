import pandas as pd
import numpy as np
from .discreteChecker import is_discrete_variable

def sort_ranges_numerically(ranges):
    """Sort ranges properly - if they contain numeric ranges, sort by the first number"""
    def extract_first_number(range_str):
        try:
            # Extract the first number before the dash
            if '-' in str(range_str):
                return float(str(range_str).split('-')[0])
            else:
                # If no dash, try to convert the whole string to float
                return float(str(range_str))
        except (ValueError, AttributeError):
            # If conversion fails, return the string for alphabetical sorting
            return str(range_str)
    
    return sorted(ranges, key=extract_first_number)

def convert_column_to_ranges(df, column_name, num_bins=4):
    if column_name not in df.columns:
        print(f"Warning: '{column_name}' column not found in data.")
        return df
    
    original_data = df[column_name].copy()
    if is_discrete_variable(column_name, original_data):
        # For discrete variables, keep original values but ensure they're strings
        df[column_name] = df[column_name].astype(str)
        return df
    
    # Check if column is already converted to categories
    if df[column_name].dtype == 'object' or df[column_name].dtype.name.startswith('str'):
        print(f"Warning: '{column_name}' column is not numeric. Creating categorical bins.")
        
        # Get unique values and create artificial bins
        unique_values = df[column_name].dropna().unique()
        
        if len(unique_values) <= num_bins:
            # If we have fewer unique values than bins, use the values directly
            sorted_unique = sorted(unique_values)
            value_map = {val: str(val) for val in sorted_unique}  # Keep original values as strings
            df[column_name] = df[column_name].map(value_map)
        else:
            # Create artificial bins by splitting unique values into num_bins groups
            sorted_values = sorted(unique_values)
            splits = np.array_split(sorted_values, num_bins)
            
            # Create mapping from values to descriptive range labels
            value_map = {}
            for i, split in enumerate(splits):
                if len(split) == 1:
                    range_label = str(split[0])
                else:
                    range_label = f"{split[0]}-{split[-1]}"
                for val in split:
                    value_map[val] = range_label
            
            df[column_name] = df[column_name].map(value_map)
    else:
        # Original numeric processing - create actual value ranges
        min_val = df[column_name].min()
        max_val = df[column_name].max()
        range_steps = np.linspace(min_val, max_val, num_bins + 1)
        
        # Create descriptive range labels with actual values
        range_labels = []
        for i in range(len(range_steps) - 1):
            range_labels.append(f"{round(range_steps[i], 1)}-{round(range_steps[i + 1], 1)}")
        
        # Store original values for comparison
        original_values = df[column_name].copy()
        df[column_name] = np.nan
        
        for i in range(len(range_steps) - 1):
            mask = (original_values >= range_steps[i]) & (original_values < range_steps[i + 1])
            df.loc[mask, column_name] = range_labels[i]
        
        # Handle edge case for maximum value
        df.loc[original_values == max_val, column_name] = range_labels[-1]
    
    return df