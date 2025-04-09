from robots import *
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
from linefollower.PID_controller import PID


client = RemoteAPIClient()
sim = client.require("sim")

# HANDLES FOR ACTUATORS AND SENSORS
left_motor = Motor(sim, DeviceNames.MOTOR_LEFT_LINE, Direction.CLOCKWISE)
right_motor = Motor(sim, DeviceNames.MOTOR_RIGHT_LINE, Direction.CLOCKWISE)
color_sensor = ImageSensor(sim, DeviceNames.IMAGE_SENSOR_LINE)

def is_red_detected(color_sensor):
    """
    Calculates the relative intensity of the red channel compared to
    other channels
    """
    red_ratio_threshold = 1.5
    red, green, blue = color_sensor.rgb()
    print(red, green, blue)
    red_intensity = red / (green + blue)

    return red_intensity > red_ratio_threshold


def is_blue_detected(color_sensor):
    """
    Calculates the relative intensity of the blue channel compared to
    other channels
    """
    blue_ratio_threshold = 1.5
    red, green, blue = color_sensor.rgb()
    blue_intensity = blue / (red + green)

    return blue_intensity > blue_ratio_threshold

def change_motor_PID():
    color_sensor._update_image() # Updates the internal image
    reflection = color_sensor.reflection() # Gets the reflection from the image
    print(f"reflection: {reflection}")
    motorspeed: float = pid.compute(reflection, dt=1.0)
    basespeed: float = 5

    print(f"speed: {motorspeed}")
    left_motor.run(speed=basespeed+motorspeed)
    right_motor.run(speed=basespeed-motorspeed)
    print("------------------------------------")
def follow_line():
    """
    A very simple line follower that should be improved.
    """
    change_motor_PID()



# Starts coppeliasim simulation if not done already
setpoint: float = 60.0
"""backup
kp: float = 0.05
ki: float = 0.001
kd: float = 0.0005
"""
kp: float = 0.14 
ki: float = 0.00001
kd: float = 0.001 # 0.0001 works
pid = PID(Kp=kp, Ki=ki, Kd=kd, setpoint=setpoint)
sim.startSimulation()


# MAIN CONTROL LOOP
while True:
	follow_line()
