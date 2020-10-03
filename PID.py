class PID:
    def __init__(self, Ref = [], Sampling_Time = 0.01, System_Model = None, Kpid = [1, 0, 0], **kwargs):
        
        if 'config' in kwargs: self.config(kwargs['config'])
        else:
            self.set_ref(Ref)
            self.set_sampling_time(Sampling_Time)
            self.set_sys_model(System_Model)
            self.set_params(Kpid)
        self.clear()

    def config(self, options):
        self.set_ref(options['Ref'])
        self.set_sampling_time(options['Sampling_Time'])
        self.set_sys_model(options['System_Model'])
        self.set_params(options['Kpid'])
    
    def apply_control(self, step, initial_res = 0, upper_limit = 10e+10):
        
        IntgSum = 0 # Integral Sum
        last_error = 0
        response = [initial_res]
        for _ in range(1, step):
            last_fb = response[-1]
            error = self.ref - last_fb
            IntgSum += self.dt * (error + last_error) / 2
            P = self.params['p'] * error
            I = self.params['i'] * IntgSum
            D = self.params['d'] * (error - last_error) / self.dt
            u = P + I + D
            last_error = error
            # print('u =>', u)

            try:
                y = self.sys_model(u)
            except:
                print('\n[ERROR]', 'When calculating response', '[OverFlow]', 'occured!', 'Here is the response:\n')
                print(response)
                print('\nLast Control_out is:', u)
                print('\nKpid Parameters', self.get_params(), '\n')
                exit()

            response.append(y)

            if y > upper_limit:
                return {'response': response, 'isLimited': True}
        
        return {'response': response, 'isLimited': False}

    def clear(self):
        self.A = 0
        self.last_err = 0
        self.u = 0

    def run(self, fb, curr_iter):
        e = self.ref[curr_iter] - fb
        self.A += self.dt * (e + self.last_err) / 2
        P = self.params['p'] * e
        I = self.params['i'] * self.A
        D = self.params['d'] * (e - self.last_err) / self.dt
        self.u = P + I + D
        self.last_err = e
        # return self.sys_model(u)

    def get_control_out(self):
        return self.u
    
    def get_response(self):
        return self.sys_model(self.u)

        # print('='*10 + '[ERROR]' + '='*10)
        # print('u:', self.u, 'e:', self.e, 'last_e:', self.last_err, 'iter:', step_id)
    
    
    # Get functions

    def get_ref(self):
        return self.ref

    def get_sampling_time(self):
        return self.dt

    def get_params(self):
        return self.params

    def get_sys_model(self):
        return self.sys_model

    def get_K(self, str_param):
        if str_param in self.params: 
            return self.params[str_param]

    # Set functions

    def set_ref(self, r):
        self.ref = r

    def set_sampling_time(self, t):
        self.dt = t

    def set_params(self, params):
        if type(params) is list:
            self.params = {'p': params[0], 'i': params[1], 'd': params[2]}
        elif type(params) is dict:
            self.params = params
        else:
            self.params = None


    def set_sys_model(self, func):
        self.sys_model = func

    def set_K(self, str_param, value):
        if str_param in self.params:
            self.params[str_param] = value
    
    