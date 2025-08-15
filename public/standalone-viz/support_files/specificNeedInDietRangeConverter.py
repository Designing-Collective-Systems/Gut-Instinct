import pandas as pd
import numpy as np

def classify_diet(df, column_name):
    """Classify dietary patterns into 7 consolidated categories"""
    def categorize_diet(diet_value):
        print(diet_value)
        if pd.isna(diet_value):
            return "a. No special diet"
        try:
            diet_str = str(diet_value).strip()
            
            # Gluten-free (includes combinations with gluten-free)
            if ('diet_gluten_free' in diet_str and 'diet_lactose_intolerance' not in diet_str):
                return "b. Gluten-free"
            
            # Lactose-free (includes combinations with lactose-free)
            elif ('diet_lactose_intolerance' in diet_str and 'diet_gluten_free' not in diet_str):
                return "c. Lactose-free"
            
            # Gluten-free + Lactose-free (both present)
            elif ('diet_lactose_intolerance' in diet_str and 'diet_gluten_free' in diet_str):
                return "d. Gluten-free + Lactose-free"
            
            # Plant-based diets (vegetarian, vegan, pescetarian and their combinations)
            elif ('diet_vegan' in diet_str or 'diet_vegetarian' in diet_str or 'diet_pescetarian' in diet_str):
                return "e. Plant-based diets"
            
            # Specialized diets (paleo and other specific dietary approaches)
            elif ('diet_paleo' in diet_str or diet_str == 'diet_others'):
                return "f. Specialized diets"
            
            # Other/Unknown
            else:
                return "g. Other/Unknown"
                
        except (ValueError, TypeError):
            return "a. No special diet"
    
    df[column_name] = df[column_name].apply(categorize_diet)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df