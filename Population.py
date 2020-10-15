import random
from math import floor
from sklearn.metrics import mean_squared_error as mse
from Chromosome import Chromosome

# def mapping(input_value, in1, in2, out1, out2): # standart map(haritalama) fonksiyonu
#     return (input_value - in1) * (out2 - out1) / (in2 - in1) + out1

class Population:
    def __init__(self, size = 100, mutation_rate = 0.01, target = None, params_range = None, max_generation = 200, **kwargs):
        self.generation = 0
        self.local_best = None
        self.global_best = None
        self.averages = []
        
        if 'config' in kwargs: self.config(kwargs['config'])
        else:
            options = {
                'population_size': size,
                'mutation_rate': mutation_rate,
                'target_response': target,
                'parameters_range': params_range,
                'max_generation': max_generation
            }
            self.config(options)

        self.init()


    def config(self, dic): # dic -> dictionary
        self.hypers = { # hyper parameters
            'population_size': dic['size'],
            'mutation_rate': dic['mutation_rate'],
            'target_response': dic['target'],
            'parameters_range': dic['params_range'],
            'count': dic['count'],
            'max_generation': dic['max_generation']
            # 'iteration': dic['iteration']
        }
    
    def init(self):
        _range = self.hypers['parameters_range']
        self.population = []
        for _ in range(self.hypers['population_size']):
            self.population.append(Chromosome(params_range=_range, _count=self.hypers['count']))

    def randomize_local_best(self):
        rand = random.randint(0, self.hypers['population_size']-1)
        self.local_best = self.population[rand]

    def randomize_global_best(self):
        rand = random.randint(0, self.hypers['population_size']-1)
        self.global_best = self.population[rand]
    
    def calc_fitness(self, chromosome_response):
        return 1/mse(self.hypers['target_response'], chromosome_response)

    def natural_selection(self):
        self.mating_pool = []

        for chromosome in self.population:
            f = chromosome.get_fitness()
            n =  (f/self.get_local_best_fitness())*100
            for _ in range(floor(n)):
                self.mating_pool.append(chromosome)

    def generate(self):
        pool_size = len(self.mating_pool) - 1
        # self.population[0] = self.get_local_best()
        for i in range(self.hypers['population_size']):
            a = random.randint(0, pool_size)
            b = random.randint(0, pool_size) 
            partner1 = self.mating_pool[a]
            partner2 = self.mating_pool[b]
            child = partner1.crossover(partner2)
            child.mutate(self.hypers['mutation_rate'])
            self.population[i] = child
        self.generation += 1

    # def reborn(self, chromosome_id, with_worst_fitness = True, *args):
    #     self.population[chromosome_id] = Chromosome(self.hypers['parameters_range'])
    #     if with_worst_fitness: self.population[chromosome_id].set_fitness(0)
    #     else: self.population[chromosome_id].set_fitness(args[0])

    def clear_genscore(self):
        self.generation_score = 0

    def update_genscore(self, fitness):
        self.generation_score += fitness / self.hypers['population_size']

    def update_averages(self):
        self.averages.append(self.generation_score)

    # Get functions

    def get_averages(self):
        return self.averages

    def get_all(self):
        return self.population

    def get_generation(self):
        return self.generation

    def get_local_best(self):
        return self.local_best
    
    def get_local_best_fitness(self):
        return self.local_best.get_fitness()

    def get_global_best(self):
        return self.global_best
    
    def get_global_best_fitness(self):
        return self.global_best.get_fitness()

    def get_count(self):
        return self.hypers['count']

    def get_max_generation(self):
        return self.hypers['max_generation']
    
    # Set & Append functions

    def set_local_best(self, chromosome):
        self.local_best = chromosome

    def set_global_best(self, chromosome):
        self.global_best = chromosome

    # Query functions
    def is_finished(self):
        if self.generation is self.hypers['max_generation']:
            return True
        return False


