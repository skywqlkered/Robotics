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

        self.deque_len = deque_len
        self.previous_errors = [(time.time_ns()/1000000, 0)]

    def compute_output(self, current_value):
        error = current_value - self.setpoint
        self.previous_errors.append((time.time_ns()/1000000,error))            
        if len(self.previous_errors) > self.deque_len:
            self.previous_errors.pop(0) 

        dt = (self.previous_errors[-1][0] - self.previous_errors[-2][0])
        derivative = (self.previous_errors[-1][1] - self.previous_errors[-2][1]) / dt
        
        integral = 0
        first_time = self.previous_errors[0][0]
        for datapoint_index in range(1,len(self.previous_errors)):
            integral += (self.previous_errors[datapoint_index][0]-first_time) * self.previous_errors[datapoint_index][1]
            first_time = self.previous_errors[datapoint_index][0]

        P_term = error * self.kp
        I_term = integral * self.ki
        D_term = derivative * self.kd

        return P_term + I_term + D_term

# def change_motor_PID():
#     color_sensor._update_image() # Updates the internal image
#     reflection = color_sensor.reflection() # Gets the reflection from the image
#     print(f"reflection: {reflection}")
#     motorspeed: float = pid.compute(reflection, dt=1.0)
#     basespeed: float = 5

#     print(f"speed: {motorspeed}")
#     left_motor.run(speed=basespeed+motorspeed)
#     right_motor.run(speed=basespeed-motorspeed)
#     print("------------------------------------")
# def follow_line():
#     """
#     A very simple line follower that should be improved.
#     """
#     change_motor_PID()

def main():
    global global_reflection
    kp: float = 1.5
    ki: float = 0
    kd: float = 0
    setpoint = 48
    
    sim.startSimulation()

    pid_controller = pid(kp, ki, kd, setpoint, 100)
    # motor_pair.pair(motor_pair.PAIR_1, port.E, port.B)

    while True:
        color_sensor._update_image() # Updates the internal image
        reflection = color_sensor.reflection() # Gets the reflection from the image
        correcting_speed = pid_controller.compute_output(reflection)
        print(reflection)
        print(correcting_speed, "\n")


        basespeed = 15
        left_motor.run(speed=basespeed-correcting_speed)
        right_motor.run(speed=basespeed+correcting_speed)

        # if reflection == 0.0:
        #     exit(404)


# MAIN CONTROL LOOP

main()
