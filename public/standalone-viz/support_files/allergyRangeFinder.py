import pandas as pd
import numpy as np

def classify_allergy(df, column_name):
    """Classify specific allergy values into 11 broad categories"""
    def categorize_allergy(allergy_value):
        if pd.isna(allergy_value):
            return "a. nan"
        
        try:
            allergy_str = str(allergy_value).strip().lower()
            
            # Exact matches for each of the 285 unique values
            if allergy_str == "amoxicillin":
                return "i. Medications/Drugs"
            elif allergy_str == "ampicillin":
                return "i. Medications/Drugs"
            elif allergy_str == "animal hair, pollen, hops, dust mites":
                return "c. Animals/Pets"
            elif allergy_str == "antibiotic":
                return "i. Medications/Drugs"
            elif allergy_str == "as a child ~5, a number of things.  given shots at home.":
                return "b. Unknown/Unspecified"
            elif allergy_str == "bee venom":
                return "g. Insects/Stings"
            elif allergy_str == "bee/wasp stings, mosquitos, sulfa, statins, cantalope":
                return "g. Insects/Stings"
            elif allergy_str == "bees":
                return "g. Insects/Stings"
            elif allergy_str == "brufen":
                return "i. Medications/Drugs"
            elif allergy_str == "cat":
                return "c. Animals/Pets"
            elif allergy_str == "cat hair":
                return "c. Animals/Pets"
            elif allergy_str == "cats":
                return "c. Animals/Pets"
            elif allergy_str == "cats dogs":
                return "c. Animals/Pets"
            elif allergy_str == "cats grass trees":
                return "c. Animals/Pets"
            elif allergy_str == "cats, dogs, erythromycin ":
                return "c. Animals/Pets"
            elif allergy_str == "cats, dogs, horses, dust, some grasses":
                return "c. Animals/Pets"
            elif allergy_str == "cats, horses, rabbits":
                return "c. Animals/Pets"
            elif allergy_str == "cipro, benzoin, pineapple":
                return "i. Medications/Drugs"
            elif allergy_str == "codeine, plavix":
                return "i. Medications/Drugs"
            elif allergy_str == "codine":
                return "i. Medications/Drugs"
            elif allergy_str == "cortisone":
                return "i. Medications/Drugs"
            elif allergy_str == "cows milk, squid ink, house dust":
                return "e. Food"
            elif allergy_str == "crab":
                return "e. Food"
            elif allergy_str == "dairy (slightly)":
                return "e. Food"
            elif allergy_str == "down, wool":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "dust ,hay fever":
                return "d. Environmental/Seasonal"
            elif allergy_str == "dust and cats via scratch test":
                return "c. Animals/Pets"
            elif allergy_str == "dust mites, grass pollen, penicillins":
                return "i. Medications/Drugs"
            elif allergy_str == "dust, cats, shellfish":
                return "c. Animals/Pets"
            elif allergy_str == "elastoplast":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "environmental":
                return "d. Environmental/Seasonal"
            elif allergy_str == "fibreglass":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "fur, feathers, dust.":
                return "c. Animals/Pets"
            elif allergy_str == "gluten and dairy":
                return "e. Food"
            elif allergy_str == "grass pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "grasses":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hay fever":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hay fever, penicilin":
                return "i. Medications/Drugs"
            elif allergy_str == "hay fever as a child":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hay fever, animal fur":
                return "c. Animals/Pets"
            elif allergy_str == "hay fever/pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hay, dust":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hayfever":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hayfever, linalool, limonene, ":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hidroclorotiacide":
                return "i. Medications/Drugs"
            elif allergy_str == "ibuprofen":
                return "i. Medications/Drugs"
            elif allergy_str == "keflex, shellfish, septra":
                return "i. Medications/Drugs"
            elif allergy_str == "macrobid/sulfa":
                return "i. Medications/Drugs"
            elif allergy_str == "mold, house dust, grasses":
                return "f. Indoor allergens"
            elif allergy_str == "mold, seasonal allergies (dust;pollen)":
                return "f. Indoor allergens"
            elif allergy_str == "morphine [ general body rash]":
                return "i. Medications/Drugs"
            elif allergy_str == "mostly grasses & sulfa":
                return "i. Medications/Drugs"
            elif allergy_str == "mostly trees and grasses. took shots in youth and after moving to ca":
                return "d. Environmental/Seasonal"
            elif allergy_str == "n/a":
                return "b. Unknown/Unspecified"
            elif allergy_str == "nickel & acrylic":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "nickel, dust mites, penicillin ":
                return "i. Medications/Drugs"
            elif allergy_str == "nifedipine, cats, some farm animals":
                return "i. Medications/Drugs"
            elif allergy_str == "nuts":
                return "e. Food"
            elif allergy_str == "oak, rye grass":
                return "d. Environmental/Seasonal"
            elif allergy_str == "penicilin":
                return "i. Medications/Drugs"
            elif allergy_str == "penicilin, erythromycin, possibly solumedrol":
                return "i. Medications/Drugs"
            elif allergy_str == "penicilin, keflex":
                return "i. Medications/Drugs"
            elif allergy_str == "penicilin, tyelenol":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillan":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillen":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin ":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin , colophony ":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin and seasonal":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin latex":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin, hayfever":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin, aspirin, coconut milk, grass pollen":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin, erytromycin, maize intolerant":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin, sulfa, flexeril, daypro, clindamycin, latex, banana, kiwi":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin, sulfa, pit fruits":
                return "i. Medications/Drugs"
            elif allergy_str == "pine nuts and cat hair":
                return "e. Food"
            elif allergy_str == "pine nuts":
                return "e. Food"
            elif allergy_str == "plasters":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen (hay fever)":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen - have not had issues for 10 years":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, dust":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, grass":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, mold, dust,mites":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollens":
                return "d. Environmental/Seasonal"
            elif allergy_str == "ponstan unknown foods":
                return "i. Medications/Drugs"
            elif allergy_str == "previously had allergy to fruit  during alopecia sudden episode around 6 years ago ":
                return "e. Food"
            elif allergy_str == "salicylate":
                return "i. Medications/Drugs"
            elif allergy_str == "scents and grass":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal allergies - oak, weeds, etc.":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal allergies - unspecified":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal pollens":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal/year round":
                return "d. Environmental/Seasonal"
            elif allergy_str == "septrin,diclofenac":
                return "i. Medications/Drugs"
            elif allergy_str == "septrum,codeine,blood pressure tablets,":
                return "i. Medications/Drugs"
            elif allergy_str == "shellfish":
                return "e. Food"
            elif allergy_str == "shellfish, nitrofurantoin":
                return "e. Food"
            elif allergy_str == "smoke ":
                return "d. Environmental/Seasonal"
            elif allergy_str == "snails":
                return "e. Food"
            elif allergy_str == "some pollens":
                return "d. Environmental/Seasonal"
            elif allergy_str == "some nuts":
                return "e. Food"
            elif allergy_str == "stemetil":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfa":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfa drugs and environmental ":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfa, dust, mold, grass":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfas, had some skin allergies due to food intake (cinnamon, fermented food)":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfur drugs, curry":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfur, thimerasole":
                return "i. Medications/Drugs"
            elif allergy_str == "teflon spray coating":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "tree pollen, penicillin, ibuprofen":
                return "i. Medications/Drugs"
            elif allergy_str == "tree pollen, rabbit brush":
                return "d. Environmental/Seasonal"
            elif allergy_str == "trees, pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "usual things,pollens grass mites mold, but went away when ms emerged in 1995. asthma disappeared after moving from moldy apartment and to countryside.  skin rash was probably psoriasis, maybe not eczema. i consider myself allergy free now.":
                return "d. Environmental/Seasonal"
            elif allergy_str == "uv b , trimpmithroprin":
                return "i. Medications/Drugs"
            elif allergy_str == "wool, feathers, dust":
                return "c. Animals/Pets"
            elif allergy_str == "all fur, most pollens (most grasses), dust, vicodin":
                return "i. Medications/Drugs"
            elif allergy_str == "allergic to almost everything until age 15 - grass, dust, cat dander, no food allergies, torodol (anaphylactic), eggs on their own":
                return "i. Medications/Drugs"
            elif allergy_str == "amoxicilin":
                return "i. Medications/Drugs"
            elif allergy_str == "amoxicillan":
                return "i. Medications/Drugs"
            elif allergy_str == "ampicillin, juniper":
                return "i. Medications/Drugs"
            elif allergy_str == "animal dander, dust mites, dust, mold, and doxepin":
                return "i. Medications/Drugs"
            elif allergy_str == "ants":
                return "g. Insects/Stings"
            elif allergy_str == "as a child, i was mildly allergic to everything according to the tests -- dogs, cats, plants, etc.  i don't worry about it much though.":
                return "c. Animals/Pets"
            elif allergy_str == "ashwanganda":
                return "i. Medications/Drugs"
            elif allergy_str == "azithromycin":
                return "i. Medications/Drugs"
            elif allergy_str == "bactrim":
                return "i. Medications/Drugs"
            elif allergy_str == "bees":
                return "g. Insects/Stings"
            elif allergy_str == "brazil nuts":
                return "e. Food"
            elif allergy_str == "cantaloupe and some other melons":
                return "e. Food"
            elif allergy_str == "cats":
                return "c. Animals/Pets"
            elif allergy_str == "cats, dust and dust mites, pollens":
                return "c. Animals/Pets"
            elif allergy_str == "cats, mold, trees":
                return "c. Animals/Pets"
            elif allergy_str == "cats, seasonal allergies":
                return "c. Animals/Pets"
            elif allergy_str == "chicken":
                return "e. Food"
            elif allergy_str == "chocolate, strawberry, mites":
                return "e. Food"
            elif allergy_str == "citrics":
                return "e. Food"
            elif allergy_str == "cloranphenicol":
                return "i. Medications/Drugs"
            elif allergy_str == "codiene. iodine,bee venum,":
                return "i. Medications/Drugs"
            elif allergy_str == "compazine, peppermint, beets, pollens":
                return "i. Medications/Drugs"
            elif allergy_str == "copaxone, rebif":
                return "i. Medications/Drugs"
            elif allergy_str == "currently unidentified":
                return "b. Unknown/Unspecified"
            elif allergy_str == "demerol":
                return "i. Medications/Drugs"
            elif allergy_str == "dipirone":
                return "i. Medications/Drugs"
            elif allergy_str == "dogs, cats, horses, grass, crabgrass":
                return "c. Animals/Pets"
            elif allergy_str == "dogs, cats, pollen":
                return "c. Animals/Pets"
            elif allergy_str == "dogs, mites":
                return "c. Animals/Pets"
            elif allergy_str == "dust":
                return "f. Indoor allergens"
            elif allergy_str == "dust mites":
                return "f. Indoor allergens"
            elif allergy_str == "dust, cats, rabbit":
                return "c. Animals/Pets"
            elif allergy_str == "dust, grass etc":
                return "d. Environmental/Seasonal"
            elif allergy_str == "dust, grasses":
                return "d. Environmental/Seasonal"
            elif allergy_str == "dust, iodine":
                return "i. Medications/Drugs"
            elif allergy_str == "dust, olive pollen, ragweed, cat dander":
                return "c. Animals/Pets"
            elif allergy_str == "dust, pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "dust, pollen, grass":
                return "d. Environmental/Seasonal"
            elif allergy_str == "dust, pollen, some pet dander":
                return "c. Animals/Pets"
            elif allergy_str == "dust, pollen, sulfur, codeine":
                return "i. Medications/Drugs"
            elif allergy_str == "dust, ragweed, pollen, cats, dogs":
                return "c. Animals/Pets"
            elif allergy_str == "dustmites":
                return "f. Indoor allergens"
            elif allergy_str == "dyes, preservatives, dust mites":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "environmental allergies to trees, grasses, weeds, etc.":
                return "d. Environmental/Seasonal"
            elif allergy_str == "erythromycin, shellfish":
                return "i. Medications/Drugs"
            elif allergy_str == "food allergies":
                return "e. Food"
            elif allergy_str == "grass":
                return "d. Environmental/Seasonal"
            elif allergy_str == "grass and tree pollens, cat dander":
                return "c. Animals/Pets"
            elif allergy_str == "grass pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "grass, pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "grass, pollen, cats, mold":
                return "c. Animals/Pets"
            elif allergy_str == "grass/dust":
                return "d. Environmental/Seasonal"
            elif allergy_str == "grass/dust, lactose intolerant":
                return "d. Environmental/Seasonal"
            elif allergy_str == "grasses":
                return "d. Environmental/Seasonal"
            elif allergy_str == "grasses, pollens":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hay fever":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hay fever, cats, cat dander":
                return "c. Animals/Pets"
            elif allergy_str == "hay fever, mold, dust, dogs, cats":
                return "c. Animals/Pets"
            elif allergy_str == "hay fever, olive trees":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hay fever, skin issues ":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hay fever, swordfish":
                return "e. Food"
            elif allergy_str == "hay fewer":
                return "d. Environmental/Seasonal"
            elif allergy_str == "hayfever":
                return "d. Environmental/Seasonal"
            elif allergy_str == "house dust":
                return "f. Indoor allergens"
            elif allergy_str == "house dust, dustmites, cat dander, feathers, some pollen":
                return "c. Animals/Pets"
            elif allergy_str == "ibuprofen":
                return "i. Medications/Drugs"
            elif allergy_str == "iodine (iv) tetracycline":
                return "i. Medications/Drugs"
            elif allergy_str == "kiwi":
                return "e. Food"
            elif allergy_str == "lactose intolerant, penicillin":
                return "i. Medications/Drugs"
            elif allergy_str == "latex and wool":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "latex, wool":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "lipitor, fentanyl":
                return "i. Medications/Drugs"
            elif allergy_str == "metals, dust":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "mites":
                return "f. Indoor allergens"
            elif allergy_str == "mites, corticoids":
                return "i. Medications/Drugs"
            elif allergy_str == "mites, dust":
                return "f. Indoor allergens"
            elif allergy_str == "mites, dust, animal's fur, nuts":
                return "c. Animals/Pets"
            elif allergy_str == "mites, pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "mold, cats, dogs":
                return "c. Animals/Pets"
            elif allergy_str == "mold, dust, animal dander, late blooming trees, mangos":
                return "c. Animals/Pets"
            elif allergy_str == "mold, dust, pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "mold, pollen, some animal dander":
                return "c. Animals/Pets"
            elif allergy_str == "molds":
                return "f. Indoor allergens"
            elif allergy_str == "mushrooms, lima beans, peas, shellfish":
                return "e. Food"
            elif allergy_str == "nickel":
                return "j. Metals/Materials/Chemicals"
            elif allergy_str == "night shade family  pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "octopus":
                return "e. Food"
            elif allergy_str == "onions":
                return "e. Food"
            elif allergy_str == "pcn":
                return "i. Medications/Drugs"
            elif allergy_str == "peanut":
                return "e. Food"
            elif allergy_str == "peanuts":
                return "e. Food"
            elif allergy_str == "peanuts, hazelnuts":
                return "e. Food"
            elif allergy_str == "pencillin":
                return "i. Medications/Drugs"
            elif allergy_str == "pencillin, seasonal allergies":
                return "i. Medications/Drugs"
            elif allergy_str == "pencillin, spores, sulfa":
                return "i. Medications/Drugs"
            elif allergy_str == "pencillin, sulfa":
                return "i. Medications/Drugs"
            elif allergy_str == "penecillin":
                return "i. Medications/Drugs"
            elif allergy_str == "penicilin":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillan":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin, quinolones":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin, ragweed":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin, shellfish, red wine":
                return "i. Medications/Drugs"
            elif allergy_str == "penicillin; certain pollens":
                return "i. Medications/Drugs"
            elif allergy_str == "pennacillan":
                return "i. Medications/Drugs"
            elif allergy_str == "pets, season allergies, dust mites":
                return "c. Animals/Pets"
            elif allergy_str == "poison ivy":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen ":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen (normal hay fever type allergies)":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen's":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, animal fir, dust, fungus":
                return "c. Animals/Pets"
            elif allergy_str == "pollen, cat dander":
                return "c. Animals/Pets"
            elif allergy_str == "pollen, cats, dogs, dust mites":
                return "c. Animals/Pets"
            elif allergy_str == "pollen, dust mites":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, dust, meds, mold etc":
                return "i. Medications/Drugs"
            elif allergy_str == "pollen, etc":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, mites":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, mites, dust":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, mold, cats":
                return "c. Animals/Pets"
            elif allergy_str == "pollen, mold, pomegranate":
                return "e. Food"
            elif allergy_str == "pollen, molds":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, penicillin":
                return "i. Medications/Drugs"
            elif allergy_str == "pollen, pet dander":
                return "c. Animals/Pets"
            elif allergy_str == "pollen, ragweed, dust, dust mites":
                return "d. Environmental/Seasonal"
            elif allergy_str == "pollen, strawberry":
                return "e. Food"
            elif allergy_str == "pollens":
                return "d. Environmental/Seasonal"
            elif allergy_str == "prednizone, solumedrol":
                return "i. Medications/Drugs"
            elif allergy_str == "seafood - shellfish":
                return "e. Food"
            elif allergy_str == "seasonal":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal ":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal allergies":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal allergies and cats":
                return "c. Animals/Pets"
            elif allergy_str == "seasonal allergies, grass":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal grass pollen":
                return "d. Environmental/Seasonal"
            elif allergy_str == "seasonal, dust, pets":
                return "c. Animals/Pets"
            elif allergy_str == "seasonal/grass etc":
                return "d. Environmental/Seasonal"
            elif allergy_str == "sesame seeds":
                return "e. Food"
            elif allergy_str == "shellfish":
                return "e. Food"
            elif allergy_str == "shrimp, possibly also some drug used in dental surgery":
                return "e. Food"
            elif allergy_str == "some antibiotics":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfa":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfa drugs":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfa medication":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfa medications, keflex":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfa, codeine drugs":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfamides":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfanilamide, codeine, morphine, dilaudid- macrodantin, propoxyxphene hcl, (pyridium-baridium":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfites":
                return "e. Food"
            elif allergy_str == "sulfur":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfur, penicillin":
                return "i. Medications/Drugs"
            elif allergy_str == "sulfur; tysabri":
                return "i. Medications/Drugs"
            elif allergy_str == "sulpha, seasonal tree pollens and grasses":
                return "i. Medications/Drugs"
            elif allergy_str == "tetanus injection":
                return "h. Medical procedures/Injections"
            elif allergy_str == "tetracyclin":
                return "i. Medications/Drugs"
            elif allergy_str == "tetracycline, opioids, sulfa drugs":
                return "i. Medications/Drugs"
            elif allergy_str == "tobramycin  and demorol":
                return "i. Medications/Drugs"
            elif allergy_str == "tomatoes":
                return "e. Food"
            elif allergy_str == "trees, grasses, weeds":
                return "d. Environmental/Seasonal"
            elif allergy_str == "unknown":
                return "b. Unknown/Unspecified"
            elif allergy_str == "valproic acid, carbamacepine":
                return "i. Medications/Drugs"
            elif allergy_str == "walnuts and hazelnuts":
                return "e. Food"
            elif allergy_str == "year round allergies to many plants/trees outside":
                return "d. Environmental/Seasonal"
            elif allergy_str == "zoloft, pineapple":
                return "i. Medications/Drugs"
            else:
                # Fallback for any missed cases
                return "k. Multiple/Other"
                
        except (ValueError, TypeError):
            return "a. nan"
    
    df[column_name] = df[column_name].apply(categorize_allergy)
    return df
