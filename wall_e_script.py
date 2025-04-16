from robots import *
import time
from coppeliasim_zmqremoteapi_client import *
from ImageRecognizer import ImageRecognizer
from wall_e_functions import *

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
search = False

# MAIN CONTROL LOOP
while True:
    detections = img_recognizer.find_objects()
    target = get_largest_block(detections)
    carrying = img_recognizer.check_carrying()
    ImageRecognizer.create_detection_image(detections)

    if robot.get_battery() < 0.15:
        detection = check_detections("charge_station", detections)
        if detection:
            # Move to charge station
            move_to_target(detection, left_motor, right_motor)
            continue
		
    elif carrying == "trash":
        robot.compress()
	
    elif carrying == "plant":
        detection = check_detections("plant_box", detections)
        if detection:
            # Move to plant box
            move_to_target(detection, left_motor, right_motor)
            continue

    elif carrying == "compressed_trash":
        detection = check_detections("trash_box", detections)
        if detection:
            # Move to trash box
            move_to_target(detection, left_motor, right_motor)
            continue

    elif target:
        print("target")
        move_to_target(target, left_motor, right_motor)
        continue

    # searching
    left_motor.run(0.2)
    right_motor.run(-0.2)