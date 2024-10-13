import random
from copy import deepcopy
from operator import attrgetter
from sdp_data import foods, target_macros
import math

class Individual:
    def __init__(
        self,
        representation= None,
        size=None,
        valid_set=[0,0],
    ):
        # Define a list of probabilities, where the first element will be the probability of having 0 in the representation, and the other
        # will be the probability of generating a random number between 0.1 and 1 (specified in the valid_set list, that is initialized in the sdp file).
        # Below you can see this implemented. We chose to have a valid_set between 0.1 and 1 because we didn't want to include the probability of
        # generating a zero twice.
        probabilities = [0.7, 0.3]

        # If our individual doesn't have a representation, we will generate one
        if representation == None:
            while True:
                self.representation = [round(random.choices([0, round(random.uniform(valid_set[0], valid_set[1]), 1)], probabilities)[0], 1) for _ in range(size)]
                # Then, we check if the created individual satisfies the macros, i.e. the minimum daily recommended intake of the nutrients specified in the
                # target_macros (in sdp_data).
                # We keep generating representations, until the macros are satisfied.
                if self.verify_macros()[0]:
                    break
        else:
            self.representation = representation
        self.fitness = self.get_fitness()

    # Define the fitness function, that will be the price of the diet plan.
    def get_fitness(self):
        price = 0

        # For every food (corresponds to every position in the representation), multiply its quantity, that is given by the factor, that is the element i of the
        # individual's representation, by the price of that food, and multiply it by 0.01, in order to get the price in dollars, since the price we are receiving is in cents.
        # Sum the values obtained for each food, in order to get the overall diet's price.
        for i, food in enumerate(foods.index):
            factor = self.representation[i]
            price += factor * foods.loc[food, 'price'] * 0.01

        return price

    # Define a function that verifies if the target_macros are being satisfied.
    def verify_macros(self):
        valid = True
        # Initialize a dictionary that will contain the names of the nutrients and associated to them the amounts of each one present in the diet plan
        nutrients = {}
        for i, food in enumerate(foods.index):
            factor = self.representation[i] # Corresponds to the amount of each food in one individual
            for nutrient in target_macros.keys():
                if nutrient not in nutrients: # If the nutrient isn't already in the dictionary, we add it and initialize its value to 0
                    nutrients[nutrient] = 0
                # If it already exists, we add to the value it already had the factor multiplied by the price by 0.01 by the amount of the nutrient.
                # By doing so, we are getting the price of the foods for the specified amounts in dollars (as we calculated in the verify_macros()), and then
                # we multiply it by the amount of nutrient, because the amounts of nutrients we have are corresponding to 1 dollar.
                nutrients[nutrient] += factor * foods.loc[food]['price'] * 0.01 * foods.loc[food][nutrient]

        # Now our nutrients dictionary contains the amounts of each nutrient for the current diet plan.
        for nutrient in nutrients.keys():
            # Finally, we do a if condition to check if the target_macros are being achieved
            if nutrients[nutrient] < target_macros[nutrient]:
                # If the amounts of nutrients we have are less than the target_macros, we return valid = False
                valid = False
                break

        # print("Nutrients:", nutrients)

        return valid, nutrients

    def get_representation(self):
        return self.representation

    def __len__(self):
        return len(self.representation)

    def __getitem__(self, position):
        return self.representation[position]

    def __setitem__(self, position, value):
        self.representation[position] = value

    def __repr__(self):
        return f"Individual(size={len(self.representation)}); Fitness: {self.fitness}; Representation: {self.representation}"

class Population:
    def __init__(self, size, optim, **kwargs):
        self.individuals = []
        self.size = size
        self.optim = optim
        self.best_sol = None
        self.best_sol_per_gen = []
        self.best_sol_macros = []
        for _ in range(size):
            self.individuals.append(
                Individual(
                    size=kwargs["sol_size"],
                    valid_set=kwargs["valid_set"],
                )
            )

    # Define again the verify_macros function to be applied to the individuals inside the Population class
    def verify_macros(self, representation):
            valid = True
            nutrients = {}
            for i, food in enumerate(foods.index):
                factor = representation[i]
                for nutrient in target_macros.keys():
                    if nutrient not in nutrients:
                        nutrients[nutrient] = 0
                    nutrients[nutrient] += factor * foods.loc[food]['price'] * 0.01 * foods.loc[food][nutrient]

            for nutrient in nutrients.keys():
                if nutrients[nutrient] < target_macros[nutrient]:
                    valid = False
                    break

            return valid, nutrients

    # Define the euclidean_distance function to calculate the Euclidean distance between individuals, to implement Fitness Sharing
    def euclidean_distance(self, individual1, individual2):
        if len(individual1) != len(individual2):
            raise ValueError("The two solutions must have the same length.")

        squared_diff_sum = sum((a - b) ** 2 for a, b in zip(individual1, individual2))
        distance = math.sqrt(squared_diff_sum)

        return distance

    # Define the normalize_distances function, that will normalize the distances between individuals to be between 0 and 1
    def normalize_distances(self, distances):
        max_distance = max(distances)
        min_distance = min(distances)

        # If the max_distance is the same as the min_distance, the sharing coefficient would become infinite, meaning that all individuals are considered
        # part of the same niche. If that happens, we will consider to skip applying the Fitness Sharing method. Therefore, giving normalized_distances
        # the value of 1, the sharing coefficient will be also 1 (we define it later), which will not affect the fitness of the individual in question.
        if max_distance == min_distance:
            normalized_distances = 1
        else:
            normalized_distances = [(d - min_distance) / (max_distance - min_distance) for d in distances]
        return normalized_distances

    def evolve(self, gens, replacement, select, crossover, mutate, xo_p, mut_p, elitism, fitness_sharing):
        self.best_sol_per_gen = []
        self.best_sol_macros = []
        for i in range(gens):
            # Create a list that will store the individuals belonging to the new population
            new_pop = []

            # If Elitism is applied, we will store a copy of the best individual inside the variable elite, depending on the type of problem
            if elitism:
                if self.optim == "max":
                    elite = deepcopy(max(self.individuals, key = attrgetter("fitness")))
                elif self.optim == "min":
                    elite = deepcopy(min(self.individuals, key= attrgetter("fitness")))

            ### Fitness Sharing
            if fitness_sharing:
                for i in self.individuals:
                    # Create an empty list that will store the distances between the individual i and all the others
                    distances = []

                    # Calculate the Euclidean distance between all individuals and save it in the distances list
                    for j in self.individuals:
                        if i != j: # Ensures that we are calculating the distances between 2 different individuals
                            distance = self.euclidean_distance(i, j) # Using the euclidean_distance function, calculate the distance between the 2 individuals in question
                            distances.append(distance) # and add this distance to the list distances

                    # Normalize the distances between 0 and 1 using the normalize_distances function
                    normalized_distances = self.normalize_distances(distances)

                    # Calculate the Sharing Coefficient, that is the sum of all the distances normalized
                    if normalized_distances == 1: # This is the case where the max_distance == min_distance, and so we will skip doing Fitness Sharing. Later the fitness of the individual will
                        # be divided by the sharing_coefficient. Thus, since we are giving it the value of 1, its fitness will remain the same.
                        sharing_coefficient = 1
                    else:
                        sharing_coefficient = sum(normalized_distances)
                    # Finally, the fitness of the individual i is divided by the sharing_coefficient
                    i.fitness = i.fitness / sharing_coefficient

            # The next step is to populate the new population. Thus, while the size of new_pop is less than the size of the desired population, we will perform th enext steps
            while len(new_pop) < self.size:
                # Select, from the population we have, 2 individuals that will be the parents
                parent1, parent2 = select(self), select(self)
                # If replacement is False, we don't want to select the same individual for both parents
                if replacement == False:
                    # Thus, we do a while that, while the parents are the same, will select a new individual for parent2
                    while parent2 == parent1:
                        parent2 = select(self)

                # Do a copy of both parents
                parent1_ = deepcopy(parent1)
                parent2_ = deepcopy(parent2)

                # Initialize a counter to 0 that will count how many times the algorithm tries to create offsprings that do not reach the macros.
                # If this counter gets to 20, the offsprings will simply become the same as their parents.
                counter = 0
                while True:
                    # Crossover will happen with the probability of xo_p (and if the counter is less than 20)
                    if random.random() < xo_p and counter < 20:
                        offspring1, offspring2 = crossover(parent1, parent2)
                    else: # If the random number generated is higher than the probability of doing crossover, this won't happen and the offsprings will be equal to the parents
                        offspring1, offspring2 = parent1_, parent2_

                    # Mutation will happen with the probability of mut_p (and if the counter is less than 20)
                    if random.random() < mut_p and counter < 20:
                        offspring1 = mutate(offspring1)
                    if random.random() < mut_p and counter < 20:
                        offspring2 = mutate(offspring2)

                    # Verify if the offsprings generated verify the macros. If so, this while will stop, otherwise, it will enter again the loop
                    # and other offsprings will be created. Additionally, if the counter is equal or higher than 20, the while loop will also stop.
                    # If we didn't add this constraint, the algorithm could be stuck here, trying to create new offsprings that satisfied the macros.
                    if (self.verify_macros(offspring1)[0] and self.verify_macros(offspring2)[0]) or counter >= 20:
                        break

                    counter += 1
                    if counter%5 == 0:
                        print(counter)

                # If the offspring is in the form of a list, which corresponds to its representation, we will append to the new_pop an instance of the class Individual,
                # which creates a new individual
                if isinstance(offspring1, list):
                    new_pop.append(Individual(representation=offspring1))
                else: # If the offspring is not in the form of a list, it is because it is already an instance of the Individual class, thus we just add it to the new population
                    new_pop.append(offspring1)

                # This if condition exists because if we have an odd number of offsprings, it may happen that only one offspring can enter the population, otherwise we would
                # have a higher number of individuals in it than what we intend to. Thus, only if the size of the new_pop is lower than the size that we want, the offspring2 will be added to
                # the new population
                if len(new_pop) < self.size:
                    if isinstance(offspring2, list):
                        new_pop.append(Individual(representation=offspring2))
                    else:
                        new_pop.append(offspring2)
            # If we are applying Elitism, the variable worst will save the worst individual in the population, depending on the type of optimization problem
            if elitism:
                if self.optim == "max":
                    worst = min(new_pop, key=attrgetter("fitness"))
                elif self.optim == "min":
                    worst = max(new_pop, key=attrgetter("fitness"))
                # Then, we will remove from new_pop the worst individual and add to it the best one (called elite)
                new_pop.pop(new_pop.index(worst))
                new_pop.append(elite)

            # Assign to the individuals the individuals inside the new_pop
            self.individuals = new_pop

            # Define the best solution and print it, depending on the type of optimization problem
            if self.optim == "max":
                self.best_sol = {max(self.individuals, key=attrgetter("fitness"))}
            elif self.optim == "min":
                self.best_sol = {min(self.individuals, key=attrgetter("fitness"))}
            else:
                raise Exception("No optimization specified (min or max).")

            print(f'Best individual: { self.best_sol }')

            self.best_sol = self.best_sol.pop()
            self.best_sol_per_gen.append(self.best_sol.get_fitness()) # gets the best fitness from each generation

        self.best_fitness = {min(self.best_sol_per_gen)} # gets the best fitness from all generations
        self.best_sol_macros = self.best_sol.verify_macros()[1] # gets the amounts of nutrients of the best solution from all generations

    def get_best_representation(self):
        return self.best_sol.get_representation()

    def get_best_sol_per_gen(self):
        return self.best_sol_per_gen

    def get_best_sol(self):
        return self.best_sol

    def __len__(self):
        return len(self.individuals)

    def __getitem__(self, position):
        return self.individuals[position]
