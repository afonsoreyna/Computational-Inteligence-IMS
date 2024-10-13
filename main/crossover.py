import random
from random import randint, sample

# Single Point crossover chooses one index in the parents and recombine their genes from that point, creating 2 offsprings.
def single_point_co(p1, p2):
    # Choose the crossover point, that is going to be a random integer number between 1 and the size of the parent minus 2
    co_point = randint(1, len(p1)-2)

    # The offspring1 will have the genes of the parent1 from the beginning until the crossover point, and it will have the genes of the
    # parent 2 from that point until the end. For the offspring2, the reverse happens.
    offspring1 = p1[:co_point] + p2[co_point:]
    offspring2 = p2[:co_point] + p1[co_point:]

    return offspring1, offspring2

# In Multi Point crossover, the same as in Single Point crossover happens, but having more than one crossover point.
def multi_point_co(p1, p2):
    # Choose randomly the number of crossover points, that will be between 2 and 5
    num_co_points = randint(2, 5)
    # Choose randomly num_co_points numbers from 0 to the size of the parent1 minus 1, that will be the crossover points
    co_points = sorted(sample(range(len(p1)), num_co_points))

    # Initialize the offsprings
    offspring1 = []
    offspring2 = []

    # Do a for loop that iterates over the number of crossover points plus one
    for i in range(num_co_points + 1):
        # Define the start and end indexes of the intervals, in which the change of genes will happen
        start = co_points[i-1] if i > 0 else 0
        end = co_points[i] if i < num_co_points else len(p1)

        # If i is an even number, the genes are taken from p1 and added to offspring1, while the genes of p2 are added to offspring2.
        # If i is an odd number, the opposite will happen. This addition of genes is done between intervals defined by the crossover points.
        if i % 2 == 0:
            offspring1.extend(p1[start:end])
            offspring2.extend(p2[start:end])
        else:
            offspring1.extend(p2[start:end])
            offspring2.extend(p1[start:end])

    return offspring1, offspring2

# The Uniform crossover recombines genes between 2 parents, by randomly selecting the genes either from one parent or the other, with equal probability
def uniform_co(p1, p2):
    # Initialize the offsprings
    offspring1 = []
    offspring2 = []

    # gene1 corresponds to the genes in p1 and gene2 to the genes in p2
    for gene1, gene2 in zip(p1, p2):
        # If a randomly generated number is less than 0.5, the offspring1 will inherit the gene corresponding to the current index from p1 and the offspring2 from p2
        if random.random() < 0.5:
            offspring1.append(gene1)
            offspring2.append(gene2)
        # Otherwise, the offspring1 will inherit the gene corresponding to the current index from p2 and the offspring2 from p1
        else:
            offspring1.append(gene2)
            offspring2.append(gene1)

    return offspring1, offspring2