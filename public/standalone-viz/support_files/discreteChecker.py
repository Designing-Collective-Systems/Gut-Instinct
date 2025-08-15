import pandas as pd
import numpy as np
from .variableDescriptions import DISCRETE_VARIABLES, FORCE_CONTINUOUS

def is_discrete_variable(variable_name):
    # Check forced continuous variables first
    if variable_name in FORCE_CONTINUOUS:
        return False
    
    # Check predefined discrete variables
    if variable_name in DISCRETE_VARIABLES:
        return True