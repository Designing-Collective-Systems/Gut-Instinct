import pandas as pd
import numpy as np

def classify_treatmentsApplied(df, column_name):
    """Classify treatments applied into specified categories"""
    def categorize_treatmentsApplied(treatment_value):
        # print(treatment_value)
        if pd.isna(treatment_value):
            return "o. nan"
        try:
            treatment_str = str(treatment_value).strip()
            if treatment_str == 'Control_Untreated':
                return "a. Control_Untreated"
            elif treatment_str == 'Control_Dimethyl fumarate':
                return "b. Control_Dimethyl fumarate"
            elif treatment_str == 'Control_Fingolimod':
                return "c. Control_Fingolimod"
            elif treatment_str == 'Control_Glatiramer acetate':
                return "d. Control_Glatiramer acetate"
            elif treatment_str == 'Control_Interferon':
                return "e. Control_Interferon"
            elif treatment_str == 'Control_Natalizumab':
                return "f. Control_Natalizumab"
            elif treatment_str == 'Control_ocrevus(rituxan)':
                return "g. Control_ocrevus(rituxan)"
            elif treatment_str == 'Untreated':
                return "h. Untreated"
            elif treatment_str == 'Dimethyl fumarate':
                return "i. Dimethyl fumarate"
            elif treatment_str == 'Fingolimod':
                return "j. Fingolimod"
            elif treatment_str == 'Glatiramer acetate':
                return "k. Glatiramer acetate"
            elif treatment_str == 'Interferon':
                return "l. Interferon"
            elif treatment_str == 'Natalizumab':
                return "m. Natalizumab"
            elif treatment_str == 'ocrevus(rituxan)':
                return "n. Ocrevus(rituxan)"
            else:
                return "o. nan"
        except (ValueError, TypeError):
            return "o. nan"
    
    df[column_name] = df[column_name].apply(categorize_treatmentsApplied)
    return df