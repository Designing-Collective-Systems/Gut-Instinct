import pandas as pd

def classify_residence(df, column_name):
    """Classify residence into alphabetical categories"""
    def categorize_residence(residence_value):
        print(residence_value)
        if pd.isna(residence_value):
            return "h. nan"
        try:
            residence_str = str(residence_value).strip()
            if residence_str == 'Boston':
                return "a. Boston"
            elif residence_str == 'Buenos Aires':
                return "b. Buenos Aires"
            elif residence_str == 'Edinburgh':
                return "c. Edinburgh"
            elif residence_str == 'New York':
                return "d. New York"
            elif residence_str == 'Pittsburgh':
                return "e. Pittsburgh"
            elif residence_str == 'San Francisco':
                return "f. San Francisco"
            elif residence_str == 'San Sebastian':
                return "g. San Sebastian"
            else:
                return "h. nan"
        except (ValueError, TypeError):
            return "h. nan"
    
    df[column_name] = df[column_name].apply(categorize_residence)
    return df



# def classify_residence_and_disease(df, residence_column, disease_column):
#     """Classify residence and disease into alphabetical categories"""
#     def categorize_residence(residence_value, disease_value):
#         print(f"Residence: {residence_value}, Disease: {disease_value}")
#         if pd.isna(residence_value) or pd.isna(disease_value):
#             return "c. nan"
#         try:
#             residence_str = str(residence_value).strip()
#             disease_str = str(disease_value).strip()
            
#             if disease_str == 'Control':
#                 return "a. People without MS"
#             else:
#                 return "b. People with MS"
#         except (ValueError, TypeError):
#             return "c. nan"
    
#     df[residence_column] = df.apply(lambda row: categorize_residence(row[residence_column], row[disease_column]), axis=1)
#     return df


def classify_residence_and_disease(df, residence_column, disease_column):
    """Classify residence and disease into alphabetical categories"""
    def categorize_residence(residence_value, disease_value):
        print(f"Residence: {residence_value}, Disease: {disease_value}")
        if pd.isna(residence_value) or pd.isna(disease_value):
            return "g. nan"
        try:
            residence_str = str(residence_value).strip()
            disease_str = str(disease_value).strip()
            
            if disease_str == 'Control':
                if residence_str == 'Edinburgh':
                    return "a. People without MS in Z1. Edinburgh"
                elif residence_str == 'San Sebastian':
                    return "b. People without MS in Z2. San Sebastian"
                elif residence_str == 'Boston' or residence_str == 'New York' or residence_str == 'Pittsburgh':
                    return "c. People without MS in Z3. Boston/New York/Pittsburgh"
                elif residence_str == 'San Francisco':
                    return "d. People without MS in Z4. San Francisco"
                elif residence_str == 'Buenos Aires':
                    return "e. People without MS in Z5. Buenos Aires"
                else:
                    return "g. nan"
            else:
                return "f. People with MS"
        except (ValueError, TypeError):
            return "g. nan"
    
    df[residence_column] = df.apply(lambda row: categorize_residence(row[residence_column], row[disease_column]), axis=1)
    # Get value counts
    counts = df[residence_column].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[residence_column] = df[residence_column].map(count_mapping)

    return df