import random
import pandas as pd

foods = pd.read_excel("SDP_data.xlsx")
foods.set_index("Commodity", inplace = True)

# Define the number of genes (scaling factors)
num_genes = len(foods)

# Define the target macronutrient ratio
target_macros = {
            'Calories': 3,
            'Protein': 70,
            'Calcium': 0.8,
            'Iron': 12,
            'Vitamin A': 5,
            'Vitamin B1': 1.8,
            'Vitamin B2': 2.7,
            'Niacin': 18,
            'Vitamin C': 75
}


