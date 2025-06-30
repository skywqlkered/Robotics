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

        dt = (self.previous_errors[-1][0] - self.previous_errors[-2][0]) / 1000  # seconds
        derivative = (self.previous_errors[-1][1] - self.previous_errors[-2][1]) / dt
        
        integral = 0
        for i in range(1, len(self.previous_errors)):
            dt = (self.previous_errors[i][0] - self.previous_errors[i-1][0]) / 1000
            integral += self.previous_errors[i][1] * dt


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


def stop():
    left_motor.run(speed=0)
    right_motor.run(speed=0)
    sim.stopSimulation()
    exit(0)

async def main():
    
    global global_reflection
    kp: float = 0.4
    ki: float = 0
    kd: float = 0
    setpoint = 67
    sim.startSimulation()

    start_time = time.time()

    pid_controller = pid(kp, ki, kd, setpoint, 100)
    # motor_pair.pair(motor_pair.PAIR_1, port.E, port.B)

    while True:
        color_sensor._update_image() # Updates the internal image
        reflection = color_sensor.reflection() # Gets the reflection from the image


        correcting_speed = pid_controller.compute_output(reflection)
        print(reflection)
        print(correcting_speed, "\n")

        await asyncio.sleep(0.02)
        
        # max_correction = 20.0 # ignoring out of bounds output
        # correcting_speed = max(-max_correction, min(correcting_speed, max_correction))
        if abs(correcting_speed) < 0.5: # removing jitter
            correcting_speed = 0

        basespeed = 15.0

       
        left_motor.run(speed=basespeed - correcting_speed)
        right_motor.run(speed=basespeed + correcting_speed)


        if time.time() - start_time > 5: 
            if reflection == 0.0:# Stops the simulation if relection is 0 after 5 seconds has past
                stop()


# MAIN CONTROL LOOP

asyncio.run(main())
