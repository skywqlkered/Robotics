from robots import *
import time
from coppeliasim_zmqremoteapi_client import *
from ImageRecognizer import ImageRecognizer

client = RemoteAPIClient()
sim = client.require("sim")

# HANDLES FOR ACTUATORS AND SENSORS
robot = Robot_OS(sim, DeviceNames.ROBOT_OS)

top_image_sensor = ImageSensor(sim, DeviceNames.TOP_IMAGE_SENSOR_OS)
small_image_sensor = ImageSensor(sim, DeviceNames.SMALL_IMAGE_SENSOR_OS)

left_motor = Motor(sim, DeviceNames.MOTOR_LEFT_OS, Direction.CLOCKWISE)
right_motor = Motor(sim, DeviceNames.MOTOR_RIGHT_OS, Direction.CLOCKWISE)

img_recognizer = ImageRecognizer(top_image_sensor, small_image_sensor)

# Starts coppeliasim simulation if not done already
sim.startSimulation()

time.sleep(0.5)

# MAIN CONTROL LOOP
while True:
	# print(robot.get_battery())
	left_motor.run(0.2)
	right_motor.run(0.1)
	detections = img_recognizer.find_objects()
	ImageRecognizer.create_detection_image(detections)
	if img_recognizer.check_carrying() == 'trash':
		robot.compress()
		print("Compressed trash")