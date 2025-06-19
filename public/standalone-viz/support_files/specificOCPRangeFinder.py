import pandas as pd
import numpy as np

def classify_oral_contraceptive(df, column_name):
    """Classify oral contraceptive pills into 7 consolidated categories"""
    def categorize_ocp(ocp_value):
        if pd.isna(ocp_value):
            return "a. nan"
        
        try:
            ocp_str = str(ocp_value).strip().lower()
            
            # Exact matches for each of the 47 unique values
            if ocp_str == " nomegestrol acetate + estradiol ":
                return "b. Combination pills"
            elif ocp_str == "apri 0.15mg":
                return "b. Combination pills"
            elif ocp_str == "aviane":
                return "b. Combination pills"
            elif ocp_str == "beyaz":
                return "b. Combination pills"
            elif ocp_str == "celeste":
                return "b. Combination pills"
            elif ocp_str == "cerazette":
                return "c. Progestin-only pills"
            elif ocp_str == "cerezette":
                return "c. Progestin-only pills"
            elif ocp_str == "crysell":
                return "b. Combination pills"
            elif ocp_str == "desogen":
                return "b. Combination pills"
            elif ocp_str == "desogestrel":
                return "c. Progestin-only pills"
            elif ocp_str == "dienopil":
                return "b. Combination pills"
            elif ocp_str == "diva total":
                return "b. Combination pills"
            elif ocp_str == "divina (ethynilestradiol, drospirenone)":
                return "b. Combination pills"
            elif ocp_str == "divina drospirenone/ethynilestradiol":
                return "b. Combination pills"
            elif ocp_str == "estradiol":
                return "d. Estrogen-only"
            elif ocp_str == "implant (progesterone)":
                return "e. Long-acting methods"
            elif ocp_str == "isis":
                return "b. Combination pills"
            elif ocp_str == "isis mini":
                return "c. Progestin-only pills"
            elif ocp_str == "isis mini ":
                return "c. Progestin-only pills"
            elif ocp_str == "kala (ethinilestradiol 30mcg, drospirenone 3mg)":
                return "b. Combination pills"
            elif ocp_str == "maxima md":
                return "b. Combination pills"
            elif ocp_str == "microgestin":
                return "b. Combination pills"
            elif ocp_str == "myzilra":
                return "b. Combination pills"
            elif ocp_str == "norgestimate":
                return "c. Progestin-only pills"
            elif ocp_str == "norithistone":
                return "c. Progestin-only pills"
            elif ocp_str == "qlaira":
                return "b. Combination pills"
            elif ocp_str == "ridgebon":
                return "b. Combination pills"
            elif ocp_str == "rigevidon":
                return "b. Combination pills"
            elif ocp_str == "rubi":
                return "b. Combination pills"
            elif ocp_str == "yasmin":
                return "b. Combination pills"
            elif ocp_str == "yasminelle":
                return "b. Combination pills"
            elif ocp_str == "yazmin":
                return "b. Combination pills"
            elif ocp_str == "zinnia (ethinyl estradiol/ciproterone)":
                return "b. Combination pills"
            elif ocp_str == "damsel (ethinyl estradiol 0.03mg, drospirenone 3mg)":
                return "b. Combination pills"
            elif ocp_str == "diva total":
                return "b. Combination pills"
            elif ocp_str == "divina":
                return "b. Combination pills"
            elif ocp_str == "ethinilstradiol, drospirenone 3/20":
                return "b. Combination pills"
            elif ocp_str == "lomedia":
                return "b. Combination pills"
            elif ocp_str == "lutera":
                return "b. Combination pills"
            elif ocp_str == "microgestin ":
                return "b. Combination pills"
            elif ocp_str == "norgestimate and ethinyl estradiol":
                return "b. Combination pills"
            elif ocp_str == "ortho tri cycline lo":
                return "b. Combination pills"
            elif ocp_str == "signiorina":
                return "b. Combination pills"
            elif ocp_str == "signorina":
                return "b. Combination pills"
            elif ocp_str == "unknown":
                return "f. Unknown/Unspecified"
            elif ocp_str == "yasminelle":
                return "b. Combination pills"
            else:
                # Fallback for any missed cases
                return "g. Other"
                
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_ocp)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df