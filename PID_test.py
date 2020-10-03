import gym
from numpy import clip
from sklearn.metrics import mean_squared_error
from PID import *

class Test(PID):
    def __init__(self, configs, _step, _target, _minmax, environment):
        super().__init__(config=configs)
        self.step = _step
        self.env_name = environment
        self.target = _target
        self.minmax = _minmax
        

    def eval(self, res):
        return mean_squared_error(self.target, res)

    def test(self, episode = 10, mssg = ''):
        print('\n', 'PID Performance test starting...', mssg)
        self.mse = {'all': [], 'average': 0}
        self.torques = [] 
        env = gym.make(self.env_name)
        print()
        for e in range(episode):
            self.clear()
            _ = env.reset()
            self.response = []
            cout_sat = []
            print('episode #:', e, 'showing.')
            for i in range(self.step):
                env.render()
                th, _ = env.state
                self.response.append(th)
                self.run(th, i)
                cout_sat.append(clip(self.u, -4, 4))
                action = [self.u]
                _, _, _, _ = env.step(action)
            self.mse['all'].append(self.eval(self.response))
            self.torques.append(cout_sat)
        self.mse['average'] = sum(self.mse['all']) / episode
        env.close()

    def get_all_mse(self):
        return self.mse['all']

    def get_average(self):
        return self.mse['average']

    def get_torq(self):
        return self.torques