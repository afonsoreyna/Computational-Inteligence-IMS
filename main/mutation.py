import random
from random import sample

# Swap mutation swaps the positions of 2 random genes
def swap_mutation(individual):
    # Randomly select the 2 genes to mutate
    mut_indexes = sample(range(0, len(individual)), 2)
    # Swap the genes in the indexes selected
    individual[mut_indexes[0]], individual[mut_indexes[1]] = individual[mut_indexes[1]], individual[mut_indexes[0]]

    return individual

# Inversion mutation inverts a subset of genes within an individual's representation
def inversion_mutation(individual):
    # Randomly select 2 indexes
    mut_indexes = sample(range(0, len(individual)), 2)
    # Sort them
    mut_indexes.sort()
    # The genes within the selected subset are reversed
    individual[mut_indexes[0]:mut_indexes[1]] = individual[mut_indexes[0]:mut_indexes[1]][::-1]

    return individual

# Random mutation introduces random changes to the genes of an individual
def random_mutation(individual, mutation_rate=0.1, mutation_range=0.5):
    # Initialize the individual to be returned
    mutated_individual = []

    for gene in individual:
        # The mutation will happen to each gene with a certain probability
        if random.random() < mutation_rate:
            # Generate a random mutation value (for the current gene), that is sampled between -0.5 and 0.5 (predefined values), with an uniform distribution
            mutation = random.uniform(-mutation_range, mutation_range)
            # Mutate the gene by adding to its value the value of the mutation
            mutated_gene = gene + mutation
            # Since in our problem, it doesn't make sense to have negative values, since we can't have a negative quantity of food, if the mutated_gene
            # is negative, we will assign to it the value of 0
            if mutated_gene < 0:
                mutated_gene = 0
            # Add to the mutated_individual the mutated genes
            mutated_individual.append(mutated_gene)
        else:
            # If the gene isn't going to suffer any mutation, add it to the mutated_individual
            mutated_individual.append(gene)

    return mutated_individual

