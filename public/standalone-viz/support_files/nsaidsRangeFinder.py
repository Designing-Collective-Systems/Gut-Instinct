import pandas as pd
import numpy as np

def classify_nsaid(df, column_name):
    """Classify specific NSAID values into 7 consolidated categories"""
    def categorize_nsaid(nsaid_value):
        if pd.isna(nsaid_value):
            return "a. nan"
        
        try:
            nsaid_str = str(nsaid_value).strip().lower()
            
            # Priority-based classification for the 264 unique values
            
            # 1. Ibuprofen/Naproxen-based (combined common NSAIDs)
            if ('ibuprofen' in nsaid_str or 'advil' in nsaid_str or 'motrin' in nsaid_str or 
                'brufen' in nsaid_str or 'ibuprufen' in nsaid_str or 'ibruprofen' in nsaid_str or
                'ibofrofen' in nsaid_str or 'naproxen' in nsaid_str or 'aleve' in nsaid_str or 
                'naprosyn' in nsaid_str or 'naproxem' in nsaid_str):
                return "b. Ibuprofen/Naproxen-based"
            
            # 2. Aspirin-based
            elif ('aspirin' in nsaid_str or 'asa ' in nsaid_str or 'acetylsalicylic' in nsaid_str or 
                  'bayer' in nsaid_str or 'asprin' in nsaid_str):
                return "c. Aspirin-based"
            
            # 3. Acetaminophen/Tylenol (not technically NSAIDs but often grouped)
            elif ('acetaminophen' in nsaid_str or 'tylenol' in nsaid_str or 'paracetamol' in nsaid_str or
                  'tyelenol' in nsaid_str):
                return "d. Acetaminophen/Tylenol"
            
            # 4. Other NSAIDs (combined diclofenac, COX-2 inhibitors, and other medications)
            elif ('diclofenac' in nsaid_str or 'voltaren' in nsaid_str or 'declofex' in nsaid_str or
                  'diclofenic' in nsaid_str or 'diclosenac' in nsaid_str or 'celecoxib' in nsaid_str or 
                  'celebrex' in nsaid_str or 'arcoxia' in nsaid_str or 'meloxicam' in nsaid_str or 
                  'mobic' in nsaid_str or 'maloxicam' in nsaid_str):
                return "e. Other NSAIDs"
            
            # 5. Usage patterns/frequency (combined as needed and frequency/dosage)
            elif ('as needed' in nsaid_str or 'as required' in nsaid_str or 'prn' in nsaid_str or
                  'when needed' in nsaid_str or 'ad-hoc' in nsaid_str or 'occasionally' in nsaid_str or
                  'on occasion' in nsaid_str or 'when necessary' in nsaid_str or 'when required' in nsaid_str or
                  (nsaid_str.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')) and 
                   ('/' in nsaid_str or 'mg' in nsaid_str or 'daily' in nsaid_str or 
                    'weekly' in nsaid_str or 'month' in nsaid_str or '/wk' in nsaid_str))):
                return "f. Usage patterns/frequency"
            
            # 6. Unknown/Unspecified/Other
            elif ('unknown' in nsaid_str or 'unclear' in nsaid_str or nsaid_str == 'n/a' or 
                  nsaid_str == 'na'):
                return "g. Unknown/Other"
            
            # 7. Fallback for any other entries
            else:
                return "g. Unknown/Other"
                
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_nsaid)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df