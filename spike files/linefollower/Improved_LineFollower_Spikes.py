import runloop
import time

import motor
import color_sensor
from hub import port

class PID:
    def __init__(self, Kp, Ki, Kd, setpoint, integrals_max, filter_constant):
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

        self.integrals = 0
        self.integrals_max = integrals_max

        self.filter_constant = filter_constant
        self.noise_filter = 0
        self.prev_noise_filter = 0

        self.time_start = time.time()

    def compute(self, computed_var):
        time_end = time.time()
        time_difference = time_end - self.time_start
    
        error = self.setpoint - computed_var
        change_error = error - self.prev_error

        self.integrals += error * (time_difference)
        if self.integrals > self.integrals_max:
            self.integrals = self.integrals_max
        elif self.integrals < - self.integrals_max:
            self.integrals = - self.integrals_max

        self.noise_filter = self.noise_filter * self.prev_noise_filter + (1-self.noise_filter) * change_error
        derivative = self.noise_filter / (time_difference)

        P_term = self.Kp * error
        I_term = self.Ki * self.integrals
        D_term = self.Kd * derivative

        output = P_term + I_term + D_term
        
        self.prev_error = error
        self.prev_noise_filter = self.noise_filter

        self.time_start = time_end
        return output

async def main():
    # Set up PID controller
    kp: float = 2
    ki: float = 0.00001
    kd: float = 0.001
    setpoint = 67
    integrals_max = 0 # No clue how big this value should be
    filter_constant = 0.8 # 0 < filter_constant < 1

    pid_controller = PID(kp, ki, kd, setpoint, integrals_max, filter_constant)

    # Set speeds
    base_speed = 250

    while True:
        reflection = color_sensor.reflection(port.D) # Color sensor on port D
        correcting_speed = pid_controller.compute(reflection)

        motor.run(port.A, int(base_speed + correcting_speed)) # Left motor
        motor.run(port.B, int(base_speed - correcting_speed)) # Right motor

runloop.run(main())