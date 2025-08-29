import random


class Genome:
    def __init__(self, genome_length, gene_pool):
        self.genome = []                    # Represents all genes as a list
        self.genome_length = genome_length  # Genome size (how many genes it has)
        self.gene_pool = gene_pool          # List of possible genes
        self.score = 0                      # Genome score (calculated in the fitness function)

    # Public
    def get_random_gene(self):
        return random.choice(self.gene_pool)

    def get_other_random_gene(self, index):        
        gene_pool = self.gene_pool.copy()
        gene_pool.remove(self.genome[index])
        return random.choice(gene_pool)

    def get_genome(self):
        return self.genome
    
    def get_score(self):
        return self.score

    def set_gene(self, index, gene):
        self.genome[index] = gene

    def set_genome(self, genome):
        self.genome = genome

    def set_random_genome(self):
        self.genome = []
        for i in range(self.genome_length):
            self.genome.append(self.get_random_gene())

    def set_score(self, score):
        self.score = max(0, score)


class GeneticAlgorithm:
    def __init__(self, genome_length, gene_pool, population_size, max_generations, fitness):
        self.genome_length = genome_length  # Genome size of each individual
        self.gene_pool = gene_pool          # List of possible genes
        self.population_size = population_size # Population size of each generation
        self.max_generations = max_generations # Number of generations (stopping criterion)
        self.fitness = fitness                 # "Pointer" to the fitness function to use
        
        self.crossover_points = [int(1.0 / 2.0 * self.genome_length)] # Crossover points (default 1 point in the middle)
        self.mutation_probability = 1.0 / 100.0                       # Mutation probability (default 1%)

        self.population = [] # The individuals for each generation
        self.total_score = 0 # The total score for the current generation
        self.parents = []    # The parents for the current selection
        self.child = None    # The current generated child

        self.best_score = 0     # Keep track of the best score accross generations
        self.best_genome = None # Keep track of the best genome accross generations

    # Private
    def _selection(self):
        parent_1_index = None
        parent_2_index = None

        # When total score is 0, choose two parents randomly
        if self.total_score == 0:
            self.parents = random.sample(self.population, 2)
            return

        # Select first parent
        cumulative = 0
        rnd = random.uniform(0, self.total_score)

        for i in range(self.population_size):
            genome = self.population[i]
            cumulative += genome.get_score()
            if rnd <= cumulative:
                parent_1_index = i
                break
        
        # Select second parent (can be the same as the first one)
        cumulative = 0
        rnd = random.uniform(0, self.total_score)

        for i in range(self.population_size):
            genome = self.population[i]
            cumulative += genome.get_score()
            if rnd <= cumulative:
                parent_2_index = i
                break
        
        parent_1_genome = self.population[parent_1_index]
        parent_2_genome = self.population[parent_2_index]

        self.parents = [parent_1_genome, parent_2_genome]
    
    def _crossover(self):
        child_genome = []

        is_current_parent_1 = True
        parent_1_genome = self.parents[0].get_genome()
        parent_2_genome = self.parents[1].get_genome()

        # Copy to points
        i = 0
        for p in range(len(self.crossover_points)):
            crossover_point = self.crossover_points[p]

            while i < crossover_point:
                gene = parent_1_genome[i]
                if not is_current_parent_1:
                    gene = parent_2_genome[i]                
                
                child_genome.append(gene)
                i += 1
            
            is_current_parent_1 = not is_current_parent_1

        # Copy the remaining genes (from last point)
        while len(child_genome) < self.genome_length:
            gene = parent_1_genome[i]
            if not is_current_parent_1:
                gene = parent_2_genome[i]

            child_genome.append(gene)
            i += 1

        self.child = Genome(self.genome_length, self.gene_pool)
        self.child.set_genome(child_genome)

    def _mutation(self):
        for i in range(self.genome_length):
            if random.random() < self.mutation_probability:
                rnd_gene = self.child.get_other_random_gene(i)
                self.child.set_gene(i, rnd_gene)

    # Public
    def get_best_genome(self):
        return self.best_genome

    def set_crossover_points(self, crossover_points):
        crossover_points.sort()

        if len(crossover_points) == 0:
            raise Exception("At least one crossover point is needed")

        for point in crossover_points:
            if point < 0 or point > self.genome_length:
                raise Exception("All crossover points must be in the boundaries")

        self.crossover_points = crossover_points

    def set_mutation_probability(self, mutation_probability):
        if mutation_probability < 0 or mutation_probability > 1:
            raise Exception("Mutation probability must be between 0 and 1")
        
        self.mutation_probability = mutation_probability

    def run(self):
        self.best_score = 0
        self.best_genome = None

        # Init population
        self.population = []
        self.total_score = 0

        for i in range(self.population_size):
            genome = Genome(self.genome_length, self.gene_pool)
            genome.set_random_genome()          
            score = self.fitness(genome)
            genome.set_score(score)
            self.population.append(genome)
            self.total_score += score

        # Create generations
        for g in range(self.max_generations):
            
            # Create children
            new_population = []
            new_total_score = 0
            
            for i in range(self.population_size):        
                self._selection()
                self._crossover()
                self._mutation()
                score = self.fitness(self.child)
                self.child.set_score(score)
                new_population.append(self.child)
                new_total_score += score

                # Keep best genome
                if score >= self.best_score:
                    self.best_score = score
                    self.best_genome = self.child
            
            # Set population
            self.population = new_population
            self.total_score = new_total_score