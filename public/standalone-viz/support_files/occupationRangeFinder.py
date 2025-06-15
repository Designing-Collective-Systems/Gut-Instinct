import pandas as pd
import numpy as np

def classify_occupation(df, column_name):
    """Classify occupation values into 11 broad categories"""
    def categorize_occupation(occupation_value):
        if pd.isna(occupation_value):
            return "a. nan"
        
        try:
            occupation_str = str(occupation_value).strip().lower()
            
            # Priority-based classification for the 622 unique occupation values
            
            # 1. Healthcare & Medical
            if ('nurse' in occupation_str or 'doctor' in occupation_str or 'physician' in occupation_str or 
                'medical' in occupation_str or 'health' in occupation_str or 'therapist' in occupation_str or
                'pharmacist' in occupation_str or 'dentist' in occupation_str or 'veterinar' in occupation_str or
                'clinical' in occupation_str or 'hospital' in occupation_str or 'surgery' in occupation_str or
                'practitioner' in occupation_str or 'midwife' in occupation_str):
                return "f. Healthcare & Medical"
            
            # 2. Education & Academia
            elif ('teacher' in occupation_str or 'professor' in occupation_str or 'education' in occupation_str or
                  'instructor' in occupation_str or 'tutor' in occupation_str or 'principal' in occupation_str or
                  'academic' in occupation_str or 'lecturer' in occupation_str or 'librarian' in occupation_str or
                  'school' in occupation_str and 'district' not in occupation_str):
                return "c. Education & Academia"
            
            # 3. Business & Management
            elif ('manager' in occupation_str or 'director' in occupation_str or 'executive' in occupation_str or
                  'ceo' in occupation_str or 'president' in occupation_str or 'supervisor' in occupation_str or
                  'coordinator' in occupation_str or 'administrator' in occupation_str or 'consultant' in occupation_str or
                  'business' in occupation_str or 'entrepreneur' in occupation_str):
                return "b. Business & Management"
            
            # 4. Finance & Accounting
            elif ('accountant' in occupation_str or 'finance' in occupation_str or 'financial' in occupation_str or
                  'banking' in occupation_str or 'bank' in occupation_str or 'actuary' in occupation_str or
                  'investment' in occupation_str or 'insurance' in occupation_str or 'audit' in occupation_str or
                  'cpa' in occupation_str or 'accounts' in occupation_str):
                return "d. Finance & Accounting"
            
            # 5. Technology & Engineering
            elif ('engineer' in occupation_str or 'software' in occupation_str or 'computer' in occupation_str or
                  'technology' in occupation_str or 'programmer' in occupation_str or 'analyst' in occupation_str or
                  'developer' in occupation_str or 'tech' in occupation_str or 'it ' in occupation_str or
                  'data' in occupation_str or 'scientist' in occupation_str or 'research' in occupation_str):
                return "j. Technology & Engineering"
            
            # 6. Sales & Marketing
            elif ('sales' in occupation_str or 'marketing' in occupation_str or 'advertising' in occupation_str or
                  'representative' in occupation_str or 'agent' in occupation_str or 'broker' in occupation_str or
                  'buyer' in occupation_str or 'vendor' in occupation_str):
                return "h. Sales & Marketing"
            
            # 7. Service & Retail
            elif ('service' in occupation_str or 'retail' in occupation_str or 'customer' in occupation_str or
                  'receptionist' in occupation_str or 'clerk' in occupation_str or 'cashier' in occupation_str or
                  'waiter' in occupation_str or 'server' in occupation_str or 'hospitality' in occupation_str or
                  'catering' in occupation_str or 'restaurant' in occupation_str):
                return "i. Service & Retail"
            
            # 8. Government & Legal
            elif ('government' in occupation_str or 'lawyer' in occupation_str or 'attorney' in occupation_str or
                  'legal' in occupation_str or 'police' in occupation_str or 'officer' in occupation_str or
                  'judge' in occupation_str or 'court' in occupation_str or 'civil service' in occupation_str or
                  'public service' in occupation_str):
                return "e. Government & Legal"
            
            # 9. Retired/Unemployed/Not Working
            elif ('retired' in occupation_str or 'unemployed' in occupation_str or 'disability' in occupation_str or
                  'homemaker' in occupation_str or 'housewife' in occupation_str or 'at home' in occupation_str or
                  'not working' in occupation_str or 'can not work' in occupation_str or 'disabled' in occupation_str or
                  'student' in occupation_str or 'undergraduate' in occupation_str or 'phd student' in occupation_str):
                return "g. Retired/Unemployed/Student"
            
            # 10. Other (all remaining occupations)
            else:
                return "k. Other"
                
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_occupation)
    return df