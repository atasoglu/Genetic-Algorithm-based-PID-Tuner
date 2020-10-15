from random import random

class Genes:
    def __init__(self, params_range):
        self.Kp = None
        self.Ki = None
        self.Kd = None
        self.range = params_range
        self.randomize_parameters()

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
        return random() * (_range[1] - _range[0]) + _range[0]

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