import pandas as pd
import os
import sys

def load_imsms_data():
    """
    Load and merge iMSMS dataset files.
    
    Returns:
        tuple: (demographic_data, sheet6_class) where:
            - demographic_data: merged demographic and clinical data
            - sheet6_class: taxonomic data for the specified dependent variable
    """
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Look for the dataset in the same directory as the script, or one level up
    possible_dataset_locations = [
        os.path.join(script_dir, 'iMSMS_dataset'),
        os.path.join(script_dir, '..', 'iMSMS_dataset'),
        os.path.join(script_dir, '..', '..', 'iMSMS_dataset'),
        'iMSMS_dataset'  # Relative path (original)
    ]
    
    dataset_dir = None
    for location in possible_dataset_locations:
        test_file = os.path.join(location, 'Supplementary_Dataset_S1.xlsx')
        if os.path.exists(test_file):
            dataset_dir = location
            break
    
    if not dataset_dir:
        print("Dataset not found in any of the following locations:")
        for location in possible_dataset_locations:
            print(f"  - {os.path.abspath(location)}")
        sys.exit(1)
    
    # Construct file paths
    S1_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S1.xlsx')
    S2_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S2.xlsx')
    S3_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S3.xlsx')
    S6_PATH = os.path.join(dataset_dir, 'Supplementary_Dataset_S6.xlsx')
    
    # Load the Excel files
    sheet1_2 = pd.read_excel(S1_PATH, sheet_name='Dataset S1.2')
    sheet2 = pd.read_excel(S2_PATH, sheet_name='Dataset S2')
    sheet3 = pd.read_excel(S3_PATH, sheet_name='Dataset S3')
    
    dependentvar = 'order'
    sheet6_class = pd.read_excel(S6_PATH, sheet_name=dependentvar)
    
    # Merge the demographic data
    demographic_data = (sheet1_2
                       .merge(sheet3, on='iMSMS_ID', how='inner')
                       .merge(sheet2, on='iMSMS_ID', how='inner')
                       )
    
    return demographic_data, sheet6_class, dependentvar