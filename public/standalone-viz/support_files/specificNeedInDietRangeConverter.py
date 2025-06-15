import pandas as pd
import numpy as np

def classify_diet(df, column_name):
    """Classify dietary patterns into 11 broad categories"""
    def categorize_diet(diet_value):
        print(diet_value)
        if pd.isna(diet_value):
            return "a. No special diet"
        try:
            diet_str = str(diet_value).strip()
            
            # Gluten-free
            if diet_str in ['diet_gluten_free', 'diet_gluten_free,diet_others']:
                return "b. Gluten-free"
            
            # Gluten-free + Lactose-free
            elif diet_str in ['diet_lactose_intolerance,diet_gluten_free', 
                             'diet_lactose_intolerance,diet_gluten_free,diet_others']:
                return "c. Gluten-free + Lactose-free"
            
            # Lactose-free
            elif diet_str in ['diet_lactose_intolerance', 'diet_lactose_intolerance,diet_others']:
                return "d. Lactose-free"
            
            # Paleo
            elif diet_str in ['diet_paleo', 'diet_gluten_free,diet_paleo', 
                             'diet_gluten_free,diet_paleo,diet_others',
                             'diet_lactose_intolerance,diet_gluten_free,diet_paleo',
                             'diet_lactose_intolerance,diet_gluten_free,diet_paleo,diet_others']:
                return "e. Paleo"
            
            # Pescetarian
            elif diet_str in ['diet_pescetarian', 'diet_pescetarian,diet_others',
                             'diet_gluten_free,diet_pescetarian',
                             'diet_lactose_intolerance,diet_gluten_free,diet_pescetarian',
                             'diet_lactose_intolerance,diet_pescetarian']:
                return "f. Pescetarian"
            
            # Pescetarian-Vegan hybrid
            elif diet_str in ['diet_pescetarian,diet_vegan', 'diet_pescetarian,diet_vegan,diet_others',
                             'diet_pescetarian,diet_vegan,diet_vegetarian']:
                return "g. Pescetarian-Vegan hybrid"
            
            # Pescetarian-Vegetarian
            elif diet_str == 'diet_pescetarian,diet_vegetarian':
                return "h. Pescetarian-Vegetarian"
            
            # Vegan
            elif diet_str == 'diet_vegan':
                return "i. Vegan"
            
            # Vegetarian
            elif diet_str in ['diet_vegetarian', 'diet_vegetarian,diet_others',
                             'diet_gluten_free,diet_vegetarian',
                             'diet_lactose_intolerance,diet_gluten_free,diet_vegetarian,diet_others']:
                return "j. Vegetarian"
            
            # Other special diets (second to last)
            elif diet_str == 'diet_others':
                return "k. Other special diets"
            
            else:
                return "a. No special diet"
                
        except (ValueError, TypeError):
            return "a. No special diet"
    
    df[column_name] = df[column_name].apply(categorize_diet)
    return df