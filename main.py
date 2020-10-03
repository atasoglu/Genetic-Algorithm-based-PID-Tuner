import gym
import matplotlib.pyplot as plt
from math import floor, pi, sin
from datetime import datetime
from time import time as Time
from PID import PID
from PID_test import Test
from ga import *

simulation_time =  10 # s
dt = 0.05
iteration = floor(simulation_time/dt)
time = [i*dt for i in range(iteration)]

# params for sine input
A = -pi/4 # amplitude
w = pi/2 # freq

Control_Params = {
    # 'Ref': [A*sin(w*i) for i in time], # for sine input (rad)
    'Ref': [pi for i in time], # (rad)
    'Simulation_Time': simulation_time, # s
    'Sampling_Time': dt, # s
    'System_Model': None,
    'Kpid': None
}

 # plot(time, ?)
# target = [Control_Params['Ref'] for _ in range(iteration)] # plot(time, target_response)
target = Control_Params['Ref']


Hyper_Params = {
    'size': 20,
    'mutation_rate': 0.05, # %
    'target': target,
    'params_range': [[0, 20], [0, 10], [0, 10]], # [P, I, D]
    'count': 10,
    'iteration': iteration,
    'max_generation': 10
}

population = Population(config=Hyper_Params)
pid = PID(config=Control_Params)

env = gym.make('Pendulum-v0')

population.randomize_global_best()
population.randomize_global_worst()

each_local_bests = []

for i in range(population.get_max_generation()):

    print('Generation #:', population.get_generation())

    population.randomize_local_best()
    population.clear_total_fitness()

    for j, chromosome in enumerate(population.get_all()):

        Kpid = chromosome.get_genes().get_parameters()
        pid.set_params(Kpid)

        temp_best_fitness = 0
        
        # ayni parametrelerle [count] kadar dene
        for k in range(chromosome.get_count()):

            pid.clear()
            observation = env.reset()
            response = []
            torque = []

            for curr in range(iteration):
                # env.render()
                feedback, thdot = env.state
                response.append(feedback)
                pid.run(feedback, curr)
                action = [pid.get_control_out()]
                observation, reward, done, info = env.step(action)
                # if done:
                    # print('res', len(response), 'targ', len(target))
                    # break

            temp_fitness = population.calc_fitness(response, episodes=4)
            chromosome.add_fitness(temp_fitness)

            if temp_fitness >= temp_best_fitness:
                temp_best_fitness = temp_fitness
                chromosome.set_response(response)
                chromosome.set_torque(torque)

        chromosome.calc_final_fitness()
        population.append_to_average(chromosome.get_fitness())

        if chromosome.get_fitness() < population.get_global_worst_fitness():
            population.set_global_worst(chromosome)
        
        elif chromosome.get_fitness() > population.get_local_best_fitness():
            population.set_local_best(chromosome)
            each_local_bests.append(chromosome.get_response())

            if chromosome.get_fitness() > population.get_global_best_fitness():
                population.set_global_best(chromosome)
    
    population.calc_average_of_generation()
    try:
        population.natural_selection()
    except MemoryError:
        print('gbest-fit', population.get_global_best_fitness())
        for chromosome in population.get_all():
            print(chromosome.get_fitness())
        exit()
    population.generate()


    print('\tBest-fitness:', population.get_local_best_fitness())
    # print('\t', 'Params:', population.get_local_best().get_params())

env.close()


print('\n', 'Global Best (f):', population.get_global_best_fitness())
print('Params:', population.get_global_best().get_params())
print('\n', 'Global Worst (f):', population.get_global_worst_fitness())
print('Params:', population.get_global_worst().get_params())
        


test = Test(Control_Params, iteration, target, env.max_torque, 'Pendulum-v0')

test.set_params(population.get_global_worst().get_params())
test.test(Hyper_Params['count'], mssg = '[Global Worst]')

test.set_params(population.get_global_best().get_params())
test.test(Hyper_Params['count'], mssg = '[Global Best]')

all_mse = test.get_all_mse()

# Hyper_Params['target'] = str(round(A, 5)) + '*sin(' + str(round(w, 5)) + '*t)' # for sine input
Hyper_Params['target'] = str(round(-pi, 5)) + ' rad'
Control_Params['Ref'] = Hyper_Params['target']

Records = 5*'=' + ' Results ' + 5*'=' + '\n'
Records = Records + 'Control Parameters:' + '\n' + str(Control_Params) + '\n'
Records = Records + 'Hyper Parameters:' + '\n' + str(Hyper_Params) + '\n'
Records = Records + 'System: Pendulum-v0\n'
Records = Records + 'G-Best-Fitness: ' + str(population.get_global_best_fitness()) + ' (1/mse)\n'
Records = Records + 'G-Best-Params: ' + str(population.get_global_best().get_params()) + '\n'
Records = Records + 'G-Worst-Fitness: ' + str(population.get_global_worst_fitness()) + ' (1/mse)\n'
Records = Records + 'G-Worst-Paramas: ' + str(population.get_global_worst().get_params()) + ' \n'
# Records = Records + 'List Of Test Results(mse): ' + str(all_mse) + '\n'

now = datetime.strftime(datetime.fromtimestamp(Time()), '%d%m%Y_%H%M%S')
f = open(now + '_result.txt', 'w')
f.write(Records) 

print('\nPlotting...')

fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(nrows = 2, ncols=2, figsize=(12, 7))

ax0.set_title('Averages of All Generations')
ax0.set_xlabel('Generation (#)')
ax0.set_ylabel('Average (1/mse)')
ax0.plot(population.get_final_average(), 'g')

ax1.set_title('Averages of Global Best')
ax1.set_xlabel('Episode (#)')
ax1.set_ylabel('Average (mse)')
ax1.plot(all_mse, '-o')

ax2.grid()
ax2.set_title('All local bests response')
ax2.set_xlabel('Iteration')
ax2.set_ylabel('Ang. Position (rad)')
ax2.plot(target, 'r', label='reference', linewidth = 2.5)
for r in each_local_bests:
    ax2.plot(r, '--')
ax2.legend()

ax3.grid()
ax3.set_title('Control outs for Global Best')
ax3.set_xlabel('Iteration')
ax3.set_ylabel('Torque (Nm)')
for torq in test.get_torq():
    ax3.plot(torq, '-')

plt.tight_layout()
plt.show()
