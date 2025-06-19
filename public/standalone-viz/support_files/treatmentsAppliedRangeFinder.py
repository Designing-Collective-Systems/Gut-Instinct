import pandas as pd
import numpy as np

def classify_treatmentsApplied(df, column_name):
    """Classify treatments applied into 7 consolidated categories"""
    def categorize_treatmentsApplied(treatment_value):
        # print(treatment_value)
        if pd.isna(treatment_value):
            return "a. nan"
        try:
            treatment_str = str(treatment_value).strip()
            
            # All controls grouped together
            if treatment_str in ['Control_Untreated', 'Control_Dimethyl fumarate', 'Control_Fingolimod', 
                               'Control_Glatiramer acetate', 'Control_Interferon', 'Control_Natalizumab', 
                               'Control_ocrevus(rituxan)']:
                return "b. Controls"
            
            # Untreated
            elif treatment_str == 'Untreated':
                return "c. Untreated"
            
            # Oral medications (pills/tablets)
            elif treatment_str in ['Dimethyl fumarate', 'Fingolimod']:
                return f"d. Oral: {treatment_str}"
            
            # Injectable medications (self-administered)
            elif treatment_str in ['Glatiramer acetate', 'Interferon']:
                return f"e. Injectable: {treatment_str}"
            
            # Infusion therapies (IV administered)
            elif treatment_str in ['Natalizumab', 'ocrevus(rituxan)']:
                return f"f. Infusion: {treatment_str}"
            
            # Other/Unknown
            else:
                return "g. Other/Unknown"
                
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_treatmentsApplied)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df