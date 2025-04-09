class PID:
    def __init__(self, Kp, Ki, Kd, setpoint):
        """
        Initializes PID controller.

        Args: 
            Kp (float): Proportional gain
            Ki (float): Integral gain
            Kd (float): Derivative gain
            setpoint (float): Desired setpoint
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
    
        self.prev_error = 0
        self.D_term = 0
        self.I_term = 0


    def compute(self, computed_var, dt):
        error = self.setpoint - computed_var
        self.I_term += error * dt
        
        self.D_term = (error - self.prev_error) / dt
        output = self.Kp * error + self.Ki * self.I_term + self.Kd * self.D_term
        
        self.prev_error = error

        return output
