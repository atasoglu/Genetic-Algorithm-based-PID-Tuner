import random
from math import floor
from sklearn.metrics import mean_squared_error as mse

class Genes:
    def __init__(self, params_range):
        self.Kp = None
        self.Ki = None
        self.Kd = None
        self.range = params_range

    def randomize_parameters(self):
        rand_params = []
        for i in range(self.get_length()):
            rand_params.append(self.get_random_value(self.range[i]))
        self.set_parameters(rand_params)

    def randomize_this(self, param_id):
        rand_value = self.get_random_value(self.range[param_id]) 
        self.set_parameter(param_id, rand_value)
    
    # Get functions

    def get_random_value(self, _range):
        return random.random() * (_range[1] - _range[0]) + _range[0]

    def get_parameters(self):
        return [self.Kp, self.Ki, self.Kd]

    def get_range(self):
        return self.range

    def get_length(self):
        return len(self.get_parameters())

    # Set functions
    def set_parameter(self, i, val):
        if i == 0: self.Kp = val
        elif i == 1: self.Ki = val
        elif i == 2: self.Kd = val

    def set_parameters(self, arr):
        self.Kp = arr[0]
        self.Ki = arr[1]
        self.Kd = arr[2]

class Chromosome:
    def __init__(self, params_range, _count = 5, start_with_random = True):
        self.response = None
        self.torque = None
        self.fitness = {'all': [], 'final': 0}
        self.count = _count
        self.genes = Genes(params_range)
        if start_with_random: self.genes.randomize_parameters()

    def crossover(self, partner):
        _range = self.genes.get_range()

        child = Chromosome(params_range= _range, start_with_random=False)
        partner1 = self.genes.get_parameters()
        partner2 = partner.genes.get_parameters()

        genes_len = self.genes.get_length()
        
        mid_point = random.randint(0, genes_len)
        
        for i in range(genes_len):
            if i < mid_point:
                child.genes.set_parameter(i, partner1[i])
            else:
                child.genes.set_parameter(i, partner2[i])
        
        return child

    def mutate(self, mutation_rate):
        for i in range(self.genes.get_length()):
            if random.random() < mutation_rate:
                self.genes.randomize_this(i)

    def calc_final_fitness(self):
        average = sum(self.fitness['all'])/self.count
        self.fitness['final'] = average

    # Get functions
    def get_fitness(self):
        # print(self.fitness)
        return self.fitness['final']

    def get_response(self):
        return self.response
    
    def get_torque(self):
        return self.torque

    def get_count(self):
        return self.count

    def get_genes(self):
        return self.genes

    def get_params(self):
        return self.genes.get_parameters()

    # Set & Append & Clear functions

    def add_fitness(self, f):
        # print(self.fitness, f)
        self.fitness['all'].append(f)

    def set_fitness(self, f):
        self.fitness['final'] = f
    
    def set_response(self, res):
        self.response = res

    def set_torque(self, torq):
        self.torque = torq

    def set_count(self, val):
        self.count = val



def mapping(input_value, in1, in2, out1, out2): # standart map(haritalama) fonksiyonu
    return (input_value - in1) * (out2 - out1) / (in2 - in1) + out1

class Population:
    def __init__(self, size = 100, mutation_rate = 0.01, target = None, params_range = None, max_generation = 200, **kwargs):
        self.generation = 0
        self.local_best = None
        self.global_best = None
        self.global_worst = None
        # self.global_id = {
        #     'population': 0
        # }
        self.Worst_Fitness = 0

        self.average = []
        
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
            'max_generation': dic['max_generation'],
            'iteration': dic['iteration']
        }
    
    def init(self):
        _range = self.hypers['parameters_range']
        self.population = []
        for _ in range(self.hypers['population_size']):
            self.population.append(Chromosome(params_range=_range, _count=self.hypers['count']))

    def randomize_local_best(self):
        rand = random.randint(0, self.hypers['population_size']-1)
        self.local_best = self.population[rand]
        # self.local_best.set_fitness(self.Worst_Fitness)

    def randomize_global_best(self):
        rand = random.randint(0, self.hypers['population_size']-1)
        self.global_best = self.population[rand]
        # self.global_best.set_fitness(self.Worst_Fitness)

    def randomize_global_worst(self):
        rand = random.randint(0, self.hypers['population_size']-1)
        self.global_worst = self.population[rand]
    
    def calc_fitness(self, chromosome_response, episodes = 4):
        return 1/mse(self.hypers['target_response'], chromosome_response)
        """
        i = floor(self.hypers['iteration']/episodes)
        total_mse = 0
        for j, epi in enumerate(range(episodes)):
            From, To = i*j, i*(j+1)
            chromo = chromosome_response[From:To]
            target = self.hypers['target_response'][From:To]
            total_mse += 1/mse(chromo, target)
        return total_mse/episodes
        """

    def clear_total_fitness(self):
        self.total_fitness = 0

    def calc_average_of_generation(self):
        self.average.append(self.get_generation_average())

    def natural_selection(self):
        self.mating_pool = []

        for chromosome in self.population:
            f = chromosome.get_fitness()
            from_worst = self.Worst_Fitness 
            to_best = self.local_best.get_fitness()

            try:
                fitness = mapping(f, from_worst, to_best, 0, 1)
            except ZeroDivisionError:
                fitness = 0.01
            # try:
            n = floor(fitness * 100)
            # except ValueError:
            #     exit()
            try:
                for _ in range(n):
                    self.mating_pool.append(chromosome)
            except:
                # print('Guess who is back?')
                # print(len(self.mating_pool))
                raise MemoryError
                # exit()
            # print('n', n, 'f', f, 'from_worst', from_worst, 'to_best', to_best)

    
    def generate(self):
        try:
            pool_size = len(self.mating_pool) - 1
            self.population[0] = self.get_local_best()
            for i in range(1, self.hypers['population_size']):
                a = random.randint(0, pool_size)
                b = random.randint(0, pool_size) 
                partner1 = self.mating_pool[a]
                partner2 = self.mating_pool[b]
                child = partner1.crossover(partner2)
                child.mutate(self.hypers['mutation_rate'])
                self.population[i] = child
            self.generation += 1
        except:
            print(len(self.mating_pool))
            print('\ntype:', type(pool_size), 'val', pool_size)
            exit()

    def reborn(self, chromosome_id, with_worst_fitness = True, *args):
        self.population[chromosome_id] = Chromosome(self.hypers['parameters_range'])
        if with_worst_fitness: self.population[chromosome_id].set_fitness(self.Worst_Fitness)
        else: self.population[chromosome_id].set_fitness(args[0])

    # Get functions
    def get_all(self):
        return self.population

    def get_generation(self):
        return self.generation

    def get_worst_fitness(self):
        return self.Worst_Fitness

    def get_local_best(self):
        return self.local_best
    
    def get_local_best_fitness(self):
        return self.local_best.get_fitness()

    # def get_local_worst(self):
    #     return self.local_worst

    def get_global_best(self):
        return self.global_best
    
    def get_global_best_fitness(self):
        return self.global_best.get_fitness()

    def get_global_worst(self):
        return self.global_worst

    def get_global_worst_fitness(self):
        return self.global_worst.get_fitness()

    def get_count(self):
        return self.hypers['count']

    def get_max_generation(self):
        return self.hypers['max_generation']

    def get_generation_average(self):
        return self.total_fitness/self.hypers['population_size']

    def get_final_average(self):
        # return sum(self.average)/self.hypers['max_generation']
        return self.average
    
    # Set & Append functions

    def append_to_average(self, f):
        self.total_fitness += f

    def set_worst_fitness(self, f):
        self.Worst_Fitness = f

    def set_local_best(self, chromosome):
        self.local_best = chromosome

    # def set_local_worst(self, chromosome):
    #     self.local_worst = chromosome

    def set_global_best(self, chromosome):
        self.global_best = chromosome

    def set_global_worst(self, chromosome):
        self.global_worst = chromosome

    # Query functions
    def is_finished(self):
        if self.generation is self.hypers['max_generation']:
            return True
        return False


