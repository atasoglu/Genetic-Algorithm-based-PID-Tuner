
import matplotlib.pyplot as plt
import numpy as np
class Pendulum:
    def __init__(self, mass, length, fric, gravity = 9.81, _dt = 0.05):
        """Units:
            mass: kg,
            length: m,
            fric(tion): Nms
            gravity = N
            dt: s
        """
        self.m = mass
        self.l = length
        self.b = fric
        self.g = gravity
        self.j = self.m * (self.l**2) / 3
        self.dt = _dt
        self.state = None # theta, thetdot

    def reset(self, state = None, **kwargs):
        if state is None:
            upper = np.pi/4 if not 'upper' in kwargs else kwargs['upper']
            self.state = {
                'th': np.random.uniform(low=-upper, high=upper),
                'thdot': 0
            }
        if type(state) is list:
            self.state = {
                'th': state[0],
                'thdot': state[1]
            }

    # def angle_normalize(self, angle):
    #     return ((np.pi + angle) % np.pi) -np.pi

    def apply(self, u):
        last = self.state
        thddot = (u - self.b * last['thdot'] - 0.5 * self.m * self.g * self.l * np.sin(last['th']))
        thdot = last['thdot'] + thddot * self.dt / self.j
        th = last['th'] + thdot * self.dt
        self.reset([th, thdot])

    def get(self, state=None):
        if state == None: return [*self.state.values()]
        if str.lower(state) in self.state.keys(): 
            return self.state[str.lower(state)]



"""pend = Pendulum(mass=1, length=1, fric=0.1)
pend.reset(state=[np.pi/2, 0])

iteration = 1000

angp = [pend.get('th')]
angv = [pend.get('thdot')]

for i in range(1, iteration):
    pend.apply(0)
    th, thdot = pend.get()
    angp.append(th)
    angv.append(thdot)

plt.grid()
plt.plot(angp, 'r-', label='açısal konum (rad)')
plt.plot(angv, 'b--', label='açısal hız (rad/s)')
# plt.title('ang. deplacement')
plt.xlabel('İterasyon (#)')
plt.legend()
plt.tight_layout()
plt.show()
"""


