from robots import *
import time
from coppeliasim_zmqremoteapi_client import *
import matplotlib.pyplot as plt

client = RemoteAPIClient()
sim = client.require("sim")

# HANDLES FOR ACTUATORS AND SENSORS
robot = Robot_OS(sim, DeviceNames.ROBOT_OS)

top_image_sensor = ImageSensor(sim, DeviceNames.TOP_IMAGE_SENSOR_OS)
small_image_sensor = ImageSensor(sim, DeviceNames.SMALL_IMAGE_SENSOR_OS)

left_motor = Motor(sim, DeviceNames.MOTOR_LEFT_OS, Direction.CLOCKWISE)
right_motor = Motor(sim, DeviceNames.MOTOR_RIGHT_OS, Direction.CLOCKWISE)

# HELPER FUNCTION
def show_image(image):
    plt.imshow(image)
    plt.show()

# Starts coppeliasim simulation if not done already
sim.startSimulation()

time.sleep(0.5)

# MAIN CONTROL LOOP
while True:
	# print(robot.get_battery())
	left_motor.run(5)
	right_motor.run(4)
	robot.compress()
	# print(small_image_sensor.rgb())
	# print(top_image_sensor.rgb())
	# print(robot.get_sonar_sensor())
	# print(robot.get_bumper_sensor())
	small_image_sensor._update_image()
	image = small_image_sensor.get_image()
	show_image(image)
	print(image)
	# show_image(image)