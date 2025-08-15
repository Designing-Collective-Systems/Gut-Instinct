import pandas as pd
import numpy as np

def classify_allergy(df, column_name):
    """Classify specific allergy values into 7 consolidated categories"""
    def categorize_allergy(allergy_value):
        if pd.isna(allergy_value):
            return "a. nan"
        
        try:
            allergy_str = str(allergy_value).strip().lower()
            
            # Exact matches for each of the 285 unique values
            if allergy_str == "amoxicillin":
                return "b. Medications/Drugs"
            elif allergy_str == "ampicillin":
                return "b. Medications/Drugs"
            elif allergy_str == "animal hair, pollen, hops, dust mites":
                return "c. Environmental/Animals"
            elif allergy_str == "antibiotic":
                return "b. Medications/Drugs"
            elif allergy_str == "as a child ~5, a number of things.  given shots at home.":
                return "g. Unknown/Other"
            elif allergy_str == "bee venom":
                return "c. Environmental/Animals"
            elif allergy_str == "bee/wasp stings, mosquitos, sulfa, statins, cantalope":
                return "c. Environmental/Animals"
            elif allergy_str == "bees":
                return "c. Environmental/Animals"
            elif allergy_str == "brufen":
                return "b. Medications/Drugs"
            elif allergy_str == "cat":
                return "c. Environmental/Animals"
            elif allergy_str == "cat hair":
                return "c. Environmental/Animals"
            elif allergy_str == "cats":
                return "c. Environmental/Animals"
            elif allergy_str == "cats dogs":
                return "c. Environmental/Animals"
            elif allergy_str == "cats grass trees":
                return "c. Environmental/Animals"
            elif allergy_str == "cats, dogs, erythromycin ":
                return "c. Environmental/Animals"
            elif allergy_str == "cats, dogs, horses, dust, some grasses":
                return "c. Environmental/Animals"
            elif allergy_str == "cats, horses, rabbits":
                return "c. Environmental/Animals"
            elif allergy_str == "cipro, benzoin, pineapple":
                return "b. Medications/Drugs"
            elif allergy_str == "codeine, plavix":
                return "b. Medications/Drugs"
            elif allergy_str == "codine":
                return "b. Medications/Drugs"
            elif allergy_str == "cortisone":
                return "b. Medications/Drugs"
            elif allergy_str == "cows milk, squid ink, house dust":
                return "d. Food"
            elif allergy_str == "crab":
                return "d. Food"
            elif allergy_str == "dairy (slightly)":
                return "d. Food"
            elif allergy_str == "down, wool":
                return "e. Materials/Chemicals"
            elif allergy_str == "dust ,hay fever":
                return "c. Environmental/Animals"
            elif allergy_str == "dust and cats via scratch test":
                return "c. Environmental/Animals"
            elif allergy_str == "dust mites, grass pollen, penicillins":
                return "b. Medications/Drugs"
            elif allergy_str == "dust, cats, shellfish":
                return "c. Environmental/Animals"
            elif allergy_str == "elastoplast":
                return "e. Materials/Chemicals"
            elif allergy_str == "environmental":
                return "c. Environmental/Animals"
            elif allergy_str == "fibreglass":
                return "e. Materials/Chemicals"
            elif allergy_str == "fur, feathers, dust.":
                return "c. Environmental/Animals"
            elif allergy_str == "gluten and dairy":
                return "d. Food"
            elif allergy_str == "grass pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "grasses":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever, penicilin":
                return "b. Medications/Drugs"
            elif allergy_str == "hay fever as a child":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever, animal fur":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever/pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "hay, dust":
                return "c. Environmental/Animals"
            elif allergy_str == "hayfever":
                return "c. Environmental/Animals"
            elif allergy_str == "hayfever, linalool, limonene, ":
                return "c. Environmental/Animals"
            elif allergy_str == "hidroclorotiacide":
                return "b. Medications/Drugs"
            elif allergy_str == "ibuprofen":
                return "b. Medications/Drugs"
            elif allergy_str == "keflex, shellfish, septra":
                return "b. Medications/Drugs"
            elif allergy_str == "macrobid/sulfa":
                return "b. Medications/Drugs"
            elif allergy_str == "mold, house dust, grasses":
                return "c. Environmental/Animals"
            elif allergy_str == "mold, seasonal allergies (dust;pollen)":
                return "c. Environmental/Animals"
            elif allergy_str == "morphine [ general body rash]":
                return "b. Medications/Drugs"
            elif allergy_str == "mostly grasses & sulfa":
                return "b. Medications/Drugs"
            elif allergy_str == "mostly trees and grasses. took shots in youth and after moving to ca":
                return "c. Environmental/Animals"
            elif allergy_str == "n/a":
                return "g. Unknown/Other"
            elif allergy_str == "nickel & acrylic":
                return "e. Materials/Chemicals"
            elif allergy_str == "nickel, dust mites, penicillin ":
                return "b. Medications/Drugs"
            elif allergy_str == "nifedipine, cats, some farm animals":
                return "b. Medications/Drugs"
            elif allergy_str == "nuts":
                return "d. Food"
            elif allergy_str == "oak, rye grass":
                return "c. Environmental/Animals"
            elif allergy_str == "penicilin":
                return "b. Medications/Drugs"
            elif allergy_str == "penicilin, erythromycin, possibly solumedrol":
                return "b. Medications/Drugs"
            elif allergy_str == "penicilin, keflex":
                return "b. Medications/Drugs"
            elif allergy_str == "penicilin, tyelenol":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillan":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillen":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin ":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin , colophony ":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin and seasonal":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin latex":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin, hayfever":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin, aspirin, coconut milk, grass pollen":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin, erytromycin, maize intolerant":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin, sulfa, flexeril, daypro, clindamycin, latex, banana, kiwi":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin, sulfa, pit fruits":
                return "b. Medications/Drugs"
            elif allergy_str == "pine nuts and cat hair":
                return "d. Food"
            elif allergy_str == "pine nuts":
                return "d. Food"
            elif allergy_str == "plasters":
                return "e. Materials/Chemicals"
            elif allergy_str == "pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen (hay fever)":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen - have not had issues for 10 years":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, dust":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, grass":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, mold, dust,mites":
                return "c. Environmental/Animals"
            elif allergy_str == "pollens":
                return "c. Environmental/Animals"
            elif allergy_str == "ponstan unknown foods":
                return "b. Medications/Drugs"
            elif allergy_str == "previously had allergy to fruit  during alopecia sudden episode around 6 years ago ":
                return "d. Food"
            elif allergy_str == "salicylate":
                return "b. Medications/Drugs"
            elif allergy_str == "scents and grass":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal allergies - oak, weeds, etc.":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal allergies - unspecified":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal pollens":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal/year round":
                return "c. Environmental/Animals"
            elif allergy_str == "septrin,diclofenac":
                return "b. Medications/Drugs"
            elif allergy_str == "septrum,codeine,blood pressure tablets,":
                return "b. Medications/Drugs"
            elif allergy_str == "shellfish":
                return "d. Food"
            elif allergy_str == "shellfish, nitrofurantoin":
                return "d. Food"
            elif allergy_str == "smoke ":
                return "c. Environmental/Animals"
            elif allergy_str == "snails":
                return "d. Food"
            elif allergy_str == "some pollens":
                return "c. Environmental/Animals"
            elif allergy_str == "some nuts":
                return "d. Food"
            elif allergy_str == "stemetil":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfa":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfa drugs and environmental ":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfa, dust, mold, grass":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfas, had some skin allergies due to food intake (cinnamon, fermented food)":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfur drugs, curry":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfur, thimerasole":
                return "b. Medications/Drugs"
            elif allergy_str == "teflon spray coating":
                return "e. Materials/Chemicals"
            elif allergy_str == "tree pollen, penicillin, ibuprofen":
                return "b. Medications/Drugs"
            elif allergy_str == "tree pollen, rabbit brush":
                return "c. Environmental/Animals"
            elif allergy_str == "trees, pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "usual things,pollens grass mites mold, but went away when ms emerged in 1995. asthma disappeared after moving from moldy apartment and to countryside.  skin rash was probably psoriasis, maybe not eczema. i consider myself allergy free now.":
                return "c. Environmental/Animals"
            elif allergy_str == "uv b , trimpmithroprin":
                return "b. Medications/Drugs"
            elif allergy_str == "wool, feathers, dust":
                return "c. Environmental/Animals"
            elif allergy_str == "all fur, most pollens (most grasses), dust, vicodin":
                return "b. Medications/Drugs"
            elif allergy_str == "allergic to almost everything until age 15 - grass, dust, cat dander, no food allergies, torodol (anaphylactic), eggs on their own":
                return "b. Medications/Drugs"
            elif allergy_str == "amoxicilin":
                return "b. Medications/Drugs"
            elif allergy_str == "amoxicillan":
                return "b. Medications/Drugs"
            elif allergy_str == "ampicillin, juniper":
                return "b. Medications/Drugs"
            elif allergy_str == "animal dander, dust mites, dust, mold, and doxepin":
                return "b. Medications/Drugs"
            elif allergy_str == "ants":
                return "c. Environmental/Animals"
            elif allergy_str == "as a child, i was mildly allergic to everything according to the tests -- dogs, cats, plants, etc.  i don't worry about it much though.":
                return "c. Environmental/Animals"
            elif allergy_str == "ashwanganda":
                return "b. Medications/Drugs"
            elif allergy_str == "azithromycin":
                return "b. Medications/Drugs"
            elif allergy_str == "bactrim":
                return "b. Medications/Drugs"
            elif allergy_str == "bees":
                return "c. Environmental/Animals"
            elif allergy_str == "brazil nuts":
                return "d. Food"
            elif allergy_str == "cantaloupe and some other melons":
                return "d. Food"
            elif allergy_str == "cats":
                return "c. Environmental/Animals"
            elif allergy_str == "cats, dust and dust mites, pollens":
                return "c. Environmental/Animals"
            elif allergy_str == "cats, mold, trees":
                return "c. Environmental/Animals"
            elif allergy_str == "cats, seasonal allergies":
                return "c. Environmental/Animals"
            elif allergy_str == "chicken":
                return "d. Food"
            elif allergy_str == "chocolate, strawberry, mites":
                return "d. Food"
            elif allergy_str == "citrics":
                return "d. Food"
            elif allergy_str == "cloranphenicol":
                return "b. Medications/Drugs"
            elif allergy_str == "codiene. iodine,bee venum,":
                return "b. Medications/Drugs"
            elif allergy_str == "compazine, peppermint, beets, pollens":
                return "b. Medications/Drugs"
            elif allergy_str == "copaxone, rebif":
                return "b. Medications/Drugs"
            elif allergy_str == "currently unidentified":
                return "g. Unknown/Other"
            elif allergy_str == "demerol":
                return "b. Medications/Drugs"
            elif allergy_str == "dipirone":
                return "b. Medications/Drugs"
            elif allergy_str == "dogs, cats, horses, grass, crabgrass":
                return "c. Environmental/Animals"
            elif allergy_str == "dogs, cats, pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "dogs, mites":
                return "c. Environmental/Animals"
            elif allergy_str == "dust":
                return "c. Environmental/Animals"
            elif allergy_str == "dust mites":
                return "c. Environmental/Animals"
            elif allergy_str == "dust, cats, rabbit":
                return "c. Environmental/Animals"
            elif allergy_str == "dust, grass etc":
                return "c. Environmental/Animals"
            elif allergy_str == "dust, grasses":
                return "c. Environmental/Animals"
            elif allergy_str == "dust, iodine":
                return "b. Medications/Drugs"
            elif allergy_str == "dust, olive pollen, ragweed, cat dander":
                return "c. Environmental/Animals"
            elif allergy_str == "dust, pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "dust, pollen, grass":
                return "c. Environmental/Animals"
            elif allergy_str == "dust, pollen, some pet dander":
                return "c. Environmental/Animals"
            elif allergy_str == "dust, pollen, sulfur, codeine":
                return "b. Medications/Drugs"
            elif allergy_str == "dust, ragweed, pollen, cats, dogs":
                return "c. Environmental/Animals"
            elif allergy_str == "dustmites":
                return "c. Environmental/Animals"
            elif allergy_str == "dyes, preservatives, dust mites":
                return "e. Materials/Chemicals"
            elif allergy_str == "environmental allergies to trees, grasses, weeds, etc.":
                return "c. Environmental/Animals"
            elif allergy_str == "erythromycin, shellfish":
                return "b. Medications/Drugs"
            elif allergy_str == "food allergies":
                return "d. Food"
            elif allergy_str == "grass":
                return "c. Environmental/Animals"
            elif allergy_str == "grass and tree pollens, cat dander":
                return "c. Environmental/Animals"
            elif allergy_str == "grass pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "grass, pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "grass, pollen, cats, mold":
                return "c. Environmental/Animals"
            elif allergy_str == "grass/dust":
                return "c. Environmental/Animals"
            elif allergy_str == "grass/dust, lactose intolerant":
                return "c. Environmental/Animals"
            elif allergy_str == "grasses":
                return "c. Environmental/Animals"
            elif allergy_str == "grasses, pollens":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever, cats, cat dander":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever, mold, dust, dogs, cats":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever, olive trees":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever, skin issues ":
                return "c. Environmental/Animals"
            elif allergy_str == "hay fever, swordfish":
                return "d. Food"
            elif allergy_str == "hay fewer":
                return "c. Environmental/Animals"
            elif allergy_str == "hayfever":
                return "c. Environmental/Animals"
            elif allergy_str == "house dust":
                return "c. Environmental/Animals"
            elif allergy_str == "house dust, dustmites, cat dander, feathers, some pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "ibuprofen":
                return "b. Medications/Drugs"
            elif allergy_str == "iodine (iv) tetracycline":
                return "b. Medications/Drugs"
            elif allergy_str == "kiwi":
                return "d. Food"
            elif allergy_str == "lactose intolerant, penicillin":
                return "b. Medications/Drugs"
            elif allergy_str == "latex and wool":
                return "e. Materials/Chemicals"
            elif allergy_str == "latex, wool":
                return "e. Materials/Chemicals"
            elif allergy_str == "lipitor, fentanyl":
                return "b. Medications/Drugs"
            elif allergy_str == "metals, dust":
                return "e. Materials/Chemicals"
            elif allergy_str == "mites":
                return "c. Environmental/Animals"
            elif allergy_str == "mites, corticoids":
                return "b. Medications/Drugs"
            elif allergy_str == "mites, dust":
                return "c. Environmental/Animals"
            elif allergy_str == "mites, dust, animal's fur, nuts":
                return "c. Environmental/Animals"
            elif allergy_str == "mites, pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "mold, cats, dogs":
                return "c. Environmental/Animals"
            elif allergy_str == "mold, dust, animal dander, late blooming trees, mangos":
                return "c. Environmental/Animals"
            elif allergy_str == "mold, dust, pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "mold, pollen, some animal dander":
                return "c. Environmental/Animals"
            elif allergy_str == "molds":
                return "c. Environmental/Animals"
            elif allergy_str == "mushrooms, lima beans, peas, shellfish":
                return "d. Food"
            elif allergy_str == "nickel":
                return "e. Materials/Chemicals"
            elif allergy_str == "night shade family  pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "octopus":
                return "d. Food"
            elif allergy_str == "onions":
                return "d. Food"
            elif allergy_str == "pcn":
                return "b. Medications/Drugs"
            elif allergy_str == "peanut":
                return "d. Food"
            elif allergy_str == "peanuts":
                return "d. Food"
            elif allergy_str == "peanuts, hazelnuts":
                return "d. Food"
            elif allergy_str == "pencillin":
                return "b. Medications/Drugs"
            elif allergy_str == "pencillin, seasonal allergies":
                return "b. Medications/Drugs"
            elif allergy_str == "pencillin, spores, sulfa":
                return "b. Medications/Drugs"
            elif allergy_str == "pencillin, sulfa":
                return "b. Medications/Drugs"
            elif allergy_str == "penecillin":
                return "b. Medications/Drugs"
            elif allergy_str == "penicilin":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillan":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin, quinolones":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin, ragweed":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin, shellfish, red wine":
                return "b. Medications/Drugs"
            elif allergy_str == "penicillin; certain pollens":
                return "b. Medications/Drugs"
            elif allergy_str == "pennacillan":
                return "b. Medications/Drugs"
            elif allergy_str == "pets, season allergies, dust mites":
                return "c. Environmental/Animals"
            elif allergy_str == "poison ivy":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen ":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen (normal hay fever type allergies)":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen's":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, animal fir, dust, fungus":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, cat dander":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, cats, dogs, dust mites":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, dust mites":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, dust, meds, mold etc":
                return "b. Medications/Drugs"
            elif allergy_str == "pollen, etc":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, mites":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, mites, dust":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, mold, cats":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, mold, pomegranate":
                return "d. Food"
            elif allergy_str == "pollen, molds":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, penicillin":
                return "b. Medications/Drugs"
            elif allergy_str == "pollen, pet dander":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, ragweed, dust, dust mites":
                return "c. Environmental/Animals"
            elif allergy_str == "pollen, strawberry":
                return "d. Food"
            elif allergy_str == "pollens":
                return "c. Environmental/Animals"
            elif allergy_str == "prednizone, solumedrol":
                return "b. Medications/Drugs"
            elif allergy_str == "seafood - shellfish":
                return "d. Food"
            elif allergy_str == "seasonal":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal ":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal allergies":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal allergies and cats":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal allergies, grass":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal grass pollen":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal, dust, pets":
                return "c. Environmental/Animals"
            elif allergy_str == "seasonal/grass etc":
                return "c. Environmental/Animals"
            elif allergy_str == "sesame seeds":
                return "d. Food"
            elif allergy_str == "shellfish":
                return "d. Food"
            elif allergy_str == "shrimp, possibly also some drug used in dental surgery":
                return "d. Food"
            elif allergy_str == "some antibiotics":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfa":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfa drugs":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfa medication":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfa medications, keflex":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfa, codeine drugs":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfamides":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfanilamide, codeine, morphine, dilaudid- macrodantin, propoxyxphene hcl, (pyridium-baridium":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfites":
                return "d. Food"
            elif allergy_str == "sulfur":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfur, penicillin":
                return "b. Medications/Drugs"
            elif allergy_str == "sulfur; tysabri":
                return "b. Medications/Drugs"
            elif allergy_str == "sulpha, seasonal tree pollens and grasses":
                return "b. Medications/Drugs"
            elif allergy_str == "tetanus injection":
                return "f. Medical Procedures"
            elif allergy_str == "tetracyclin":
                return "b. Medications/Drugs"
            elif allergy_str == "tetracycline, opioids, sulfa drugs":
                return "b. Medications/Drugs"
            elif allergy_str == "tobramycin  and demorol":
                return "b. Medications/Drugs"
            elif allergy_str == "tomatoes":
                return "d. Food"
            elif allergy_str == "trees, grasses, weeds":
                return "c. Environmental/Animals"
            elif allergy_str == "unknown":
                return "g. Unknown/Other"
            elif allergy_str == "valproic acid, carbamacepine":
                return "b. Medications/Drugs"
            elif allergy_str == "walnuts and hazelnuts":
                return "d. Food"
            elif allergy_str == "year round allergies to many plants/trees outside":
                return "c. Environmental/Animals"
            elif allergy_str == "zoloft, pineapple":
                return "b. Medications/Drugs"
            else:
                # Fallback for any missed cases
                return "g. Unknown/Other"
                
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_allergy)
    # Get value counts
    counts = df[column_name].value_counts().sort_index()
        
    # Create a mapping of category to "category - count values"
    count_mapping = {}
    for category, count in counts.items():
        count_mapping[category] = f"{category} - {count} values"
    
    # Apply the count summary to each cell
    df[column_name] = df[column_name].map(count_mapping)

    return df