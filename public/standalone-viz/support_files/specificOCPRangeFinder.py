import pandas as pd
import numpy as np

def classify_oral_contraceptive(df, column_name):
    """Classify oral contraceptive pills into 11 broad categories"""
    def categorize_ocp(ocp_value):
        if pd.isna(ocp_value):
            return "a. nan"
        
        try:
            ocp_str = str(ocp_value).strip().lower()
            
            # Exact matches for each of the 47 unique values
            if ocp_str == " nomegestrol acetate + estradiol ":
                return "f. Estradiol"
            elif ocp_str == "apri 0.15mg":
                return "d. Desogestrel"
            elif ocp_str == "aviane":
                return "h. Levonorgestrel"
            elif ocp_str == "beyaz":
                return "e. Drospirenone"
            elif ocp_str == "celeste":
                return "i. Norgestimate"
            elif ocp_str == "cerazette":
                return "d. Desogestrel"
            elif ocp_str == "cerezette":
                return "d. Desogestrel"
            elif ocp_str == "crysell":
                return "k. Other combination pills"
            elif ocp_str == "desogen":
                return "d. Desogestrel"
            elif ocp_str == "desogestrel":
                return "d. Desogestrel"
            elif ocp_str == "dienopil":
                return "k. Other combination pills"
            elif ocp_str == "diva total":
                return "k. Other combination pills"
            elif ocp_str == "divina (ethynilestradiol, drospirenone)":
                return "e. Drospirenone"
            elif ocp_str == "divina drospirenone/ethynilestradiol":
                return "e. Drospirenone"
            elif ocp_str == "estradiol":
                return "f. Estradiol"
            elif ocp_str == "implant (progesterone)":
                return "g. Implants/Long-acting"
            elif ocp_str == "isis":
                return "k. Other combination pills"
            elif ocp_str == "isis mini":
                return "j. Progestin"
            elif ocp_str == "isis mini ":
                return "j. Progestin"
            elif ocp_str == "kala (ethinilestradiol 30mcg, drospirenone 3mg)":
                return "e. Drospirenone"
            elif ocp_str == "maxima md":
                return "k. Other combination pills"
            elif ocp_str == "microgestin":
                return "h. Levonorgestrel"
            elif ocp_str == "myzilra":
                return "k. Other combination pills"
            elif ocp_str == "norgestimate":
                return "i. Norgestimate"
            elif ocp_str == "norithistone":
                return "j. Progestin"
            elif ocp_str == "qlaira":
                return "f. Estradiol"
            elif ocp_str == "ridgebon":
                return "h. Levonorgestrel"
            elif ocp_str == "rigevidon":
                return "h. Levonorgestrel"
            elif ocp_str == "rubi":
                return "k. Other combination pills"
            elif ocp_str == "yasmin":
                return "e. Drospirenone"
            elif ocp_str == "yasminelle":
                return "e. Drospirenone"
            elif ocp_str == "yazmin":
                return "e. Drospirenone"
            elif ocp_str == "zinnia (ethinyl estradiol/ciproterone)":
                return "c. Ciproterone"
            elif ocp_str == "damsel (ethinyl estradiol 0.03mg, drospirenone 3mg)":
                return "e. Drospirenone"
            elif ocp_str == "diva total":
                return "k. Other combination pills"
            elif ocp_str == "divina":
                return "e. Drospirenone"
            elif ocp_str == "ethinilstradiol, drospirenone 3/20":
                return "e. Drospirenone"
            elif ocp_str == "lomedia":
                return "h. Levonorgestrel"
            elif ocp_str == "lutera":
                return "h. Levonorgestrel"
            elif ocp_str == "microgestin ":
                return "h. Levonorgestrel"
            elif ocp_str == "norgestimate and ethinyl estradiol":
                return "i. Norgestimate"
            elif ocp_str == "ortho tri cycline lo":
                return "i. Norgestimate"
            elif ocp_str == "signiorina":
                return "k. Other combination pills"
            elif ocp_str == "signorina":
                return "k. Other combination pills"
            elif ocp_str == "unknown":
                return "b. Unknown/Unspecified"
            elif ocp_str == "yasminelle":
                return "e. Drospirenone"
            else:
                # Fallback for any missed cases
                return "k. Other combination pills"
                
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_ocp)
    return df
