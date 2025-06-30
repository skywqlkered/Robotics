from robots import *
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import time
import asyncio

client = RemoteAPIClient()
sim = client.require("sim")

# HANDLES FOR ACTUATORS AND SENSORS
left_motor = Motor(sim, DeviceNames.MOTOR_LEFT_LINE, Direction.CLOCKWISE)
right_motor = Motor(sim, DeviceNames.MOTOR_RIGHT_LINE, Direction.CLOCKWISE)
color_sensor = ImageSensor(sim, DeviceNames.IMAGE_SENSOR_LINE)


class pid():
    def __init__(self, kp, ki, kd, setpoint, deque_len):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint

        # Number of previous errors to keep for integral and derivative calculations
        self.deque_len = deque_len
        # Initialize with the first error as 0 at current time
        self.previous_errors = [(time.time_ns()/1000000, 0)]

    def compute_output(self, current_value):
        """
        Computes the PID output based on the current value and the setpoint.

        This function keeps track of the previous errors and the time at which they were recorded.
        This information is used to calculate the integral and derivative terms of the PID output.

        Args:
            current_value (float): The current value of the sensor measurement

        Returns:
            float: The PID output
        """
        error = current_value - self.setpoint
        # Append the current time and error to the deque
        self.previous_errors.append((time.time_ns()/1000000, error))
        if len(self.previous_errors) > self.deque_len:
            self.previous_errors.pop(0)

        dt = (self.previous_errors[-1][0] -
                self.previous_errors[-2][0]) / 1000  # seconds
        derivative = (self.previous_errors[-1]
                        [1] - self.previous_errors[-2][1]) / dt

        integral = 0
        for i in range(1, len(self.previous_errors)):
            dt = (self.previous_errors[i][0] -
                    self.previous_errors[i-1][0]) / 1000
            integral += self.previous_errors[i][1] * dt

        P_term = error * self.kp
        I_term = integral * self.ki
        D_term = derivative * self.kd

        return P_term + I_term + D_term

def stop(): 
    """
    Stops the robot and the simulation
    """
    
    left_motor.run(speed=0)
    right_motor.run(speed=0)
    sim.stopSimulation()
    exit(0)


async def main():

    """
    Main function of the script. It sets up the PID controller and sets the
    robot's motors to move according to the PID controller's output. The
    PID controller tries to keep the robot's reflection reading at a setpoint
    of 67.

    The function runs an infinite loop, updating the PID controller's input
    and output every 20 milliseconds. The function also checks if 5 seconds
    have passed since the start of the simulation and if the reflection reading
    is 0, in which case it stops the simulation.
    """
    kp: float = 0.4
    ki: float = 0
    kd: float = 0
    setpoint = 67
    sim.startSimulation()

    start_time = time.time()

    pid_controller = pid(kp, ki, kd, setpoint, 100)
    # motor_pair.pair(motor_pair.PAIR_1, port.E, port.B)

    while True:
        color_sensor._update_image()  # Updates the internal image
        reflection = color_sensor.reflection()  # Gets the reflection from the image

        correcting_speed = pid_controller.compute_output(reflection) 

        print(reflection)
        print(correcting_speed, "\n")

        await asyncio.sleep(0.02) # Prevents NAN errors

        if abs(correcting_speed) < 0.5:  # removes jitter by ignoring small corrections
            correcting_speed = 0

        basespeed = 15.0

        left_motor.run(speed=basespeed - correcting_speed) # allows the robot to turn left or right based on the reflection
        right_motor.run(speed=basespeed + correcting_speed) # If the reflection is low, the robot turns right, if high, it turns left

        if time.time() - start_time > 5:
            if reflection == 0.0:  # Stops the simulation if relection is 0 after 5 seconds has past
                stop()


asyncio.run(main())
