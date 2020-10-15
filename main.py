import numpy as np
import matplotlib.pyplot as plt
from Population import Population
from PID import PID
from Pendulum import Pendulum

# Control Parameters
Ref_Angle = np.deg2rad(180) # radian
Freq = 20 # Hz
Samp_Time = 1/Freq # second
Sim_Time = 10 # second
Iteration = Sim_Time * Freq
Configs_PID = {
    'Ref': [Ref_Angle for i in range(Iteration)],
    'Simulation_Time': Sim_Time,
    'Sampling_Time': Samp_Time,
    'System_Model': None,
    'Kpid': [None, None, None]
}
Configs_GA = {
    'size': 100,
    'mutation_rate': 0.05,
    'target': Configs_PID['Ref'],
    'params_range': [[0, 50], [0, 10], [0, 10]], # [P, I, D]
    'count': 10,
    'iteration': Iteration,
    'max_generation': 50
}

pendulum = Pendulum(mass=2, length=1, fric=0.15)
pid = PID(config=Configs_PID)
genetics = Population(config=Configs_GA)

max_torque = 10 # Nm

genetics.randomize_global_best()

while not genetics.is_finished():
    
    print('Generation #:', genetics.get_generation())

    genetics.randomize_local_best()
    genetics.clear_genscore()

    for j, chromosome in enumerate(genetics.get_all()):

        Kpid = chromosome.get_params()
        pid.set_params(Kpid)
        
        for c in range(chromosome.get_count()):

            pid.clear()
            pendulum.reset(upper=np.pi/4)
            response = []

            for k in range(Iteration):
                th = pendulum.get('th')
                response.append(th)
                pid.run(th, k)
                cout = pid.get_control_out()
                cout = np.clip(cout, -max_torque, max_torque)
                pendulum.apply(cout)
            
            temp_fitness = genetics.calc_fitness(response)
            chromosome.add_fitness(temp_fitness)

        genetics.update_genscore(chromosome.get_fitness())
        
        if chromosome.get_fitness() > genetics.get_local_best_fitness():
            genetics.set_local_best(chromosome)

            if chromosome.get_fitness() > genetics.get_global_best_fitness():
                genetics.set_global_best(chromosome)

    genetics.update_averages()
    genetics.natural_selection()
    genetics.generate()

    print('\tLocal-fitness:', genetics.get_local_best_fitness())
    print('\tGlob-fitness:', genetics.get_global_best_fitness())
    print('\tLocal-Params:', genetics.get_local_best().get_params())
    print('\tGlob-Params:', genetics.get_global_best().get_params())
    # print('\t', 'Params:', population.get_local_best().get_params())

print('\n', 'Global Best (f):', genetics.get_global_best_fitness())
print('Params:', genetics.get_global_best().get_params())

plt.plot(genetics.get_averages(), 'g', label='ort. uygunluk')
plt.xlabel('nesil (#)')
plt.ylabel('ortalama kare hatası (1/mse)')
plt.legend()
plt.show()

# [18.00667972608962, 5.713339768642279, 9.769403341954444]