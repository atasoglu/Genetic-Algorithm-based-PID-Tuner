from Genes import Genes
from random import random, randint

class Chromosome:
    def __init__(self, params_range, _count = 10):
        self.fitness = 0
        self.count = _count
        self.genes = Genes(params_range)
        # self.genes.randomize_parameters()

    def crossover(self, partner):
        _range = self.genes.get_range()
        
        child = Chromosome(params_range=_range)
        partner1 = self.genes.get_parameters()
        partner2 = partner.genes.get_parameters()

        genes_len = self.genes.get_length()
        
        mid_point = randint(0, genes_len)
        
        for i in range(genes_len):
            if i < mid_point:
                child.genes.set_parameter(i, partner1[i])
            else:
                child.genes.set_parameter(i, partner2[i])
        
        return child

    def mutate(self, mutation_rate):
        for i in range(self.genes.get_length()):
            if random() < mutation_rate:
                self.genes.randomize_this(i)      

    # Get functions
    def get_fitness(self):
        # print(self.fitness)
        return self.fitness

    def get_count(self):
        return self.count

    def get_genes(self):
        return self.genes

    def get_params(self):
        return self.genes.get_parameters()

    # Set & Append & Clear functions

    def add_fitness(self, f):
        self.fitness += f / self.count

    def set_fitness(self, f):
        self.fitness = f

    def set_count(self, val):
        self.count = val