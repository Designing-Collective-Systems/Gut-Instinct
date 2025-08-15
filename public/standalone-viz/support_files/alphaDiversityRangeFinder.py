import pandas as pd
import numpy as np

def classify_richness(df, column_name):
    """Classify chao1 scores into specified categories"""
    def categorize_richness(chaoOne_value):
        # print(admin_value)
        if pd.isna(chaoOne_value):
            return "a. nan"
        try:
            chaoOne = float(chaoOne_value)
            if chaoOne <= 173.16:
                return "f. Bad Diversity of Gut Bacteria"
            elif chaoOne <= 213.85:
                return "e. Poor Diversity of Gut Bacteria"
            elif chaoOne <= 256.58:
                return "d. Fair Diversity of Gut Bacteria"
            elif chaoOne <= 316.03:
                return "c. Good Diversity of Gut Bacteria"
            else:
                return "b. Excellent Diversity of Gut Bacteria"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_richness)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df


def classify_richness_and_evenness(df, column_name):
    """Classify shannon scores into specified categories"""
    def categorize_richness_and_evenness(shannon_value):
        # print(admin_value)
        if pd.isna(shannon_value):
            return "a. nan"
        try:
            shannon = float(shannon_value)
            if shannon <= 4.62:
                return "f. Bad Diversity of Gut Bacteria"
            elif shannon <= 5.15:
                return "e. Poor Diversity of Gut Bacteria"
            elif shannon <= 5.55:
                return "d. Fair Diversity of Gut Bacteria"
            elif shannon <= 5.97:
                return "c. Good Diversity of Gut Bacteria"
            else:
                return "b. Excellent Diversity of Gut Bacteria"
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_richness_and_evenness)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df