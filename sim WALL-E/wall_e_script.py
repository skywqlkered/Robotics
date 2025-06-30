import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robots import *  # noqa: F403

import time
from coppeliasim_zmqremoteapi_client import *
from ImageRecognizer import ImageRecognizer
from wall_e_functions import *

# Set up the client
client = RemoteAPIClient()
sim = client.require("sim")

# Handles for actuators and sensors
robot = Robot_OS(sim, DeviceNames.ROBOT_OS)

top_image_sensor = ImageSensor(sim, DeviceNames.TOP_IMAGE_SENSOR_OS)
small_image_sensor = ImageSensor(sim, DeviceNames.SMALL_IMAGE_SENSOR_OS)

left_motor = Motor(sim, DeviceNames.MOTOR_LEFT_OS, Direction.CLOCKWISE)
right_motor = Motor(sim, DeviceNames.MOTOR_RIGHT_OS, Direction.CLOCKWISE)

# Create instance of ImageRecognizer class
img_recognizer = ImageRecognizer(top_image_sensor, small_image_sensor)

# Starts coppeliasim simulation if not done already
sim.startSimulation()

# Give CoppeliaSim time to initialize
time.sleep(0.5)
search = False

# MAIN CONTROL LOOP
while True:
    # Get camera sensor detections
    detections = img_recognizer.find_objects()
    target = get_largest_block(detections)
    carrying = img_recognizer.check_carrying()

    # Visualize the camera detections
    ImageRecognizer.create_detection_image(detections)

    # 1. Battery monitoring and recharge (Highest Priority)
    # If the robot has less than 15% battery
    if robot.get_battery() < 0.15:
        detection = check_detections("charge_station", detections)
        if detection:
            # Move to charge station
            move_to_target(detection, left_motor, right_motor, detections[0])
            continue
	
    # 2. Trash Compression
    elif carrying == "trash":
        robot.compress()
	
    # 3. Interact with object (plant)
    elif carrying == "plant":
        detection = check_detections("plant_box", detections)
        if detection:
            # Move to plant box
            move_to_target(detection, left_motor, right_motor, detections[0])
            continue

    # 3. Interact with object (compressed_trash)
    elif carrying == "compressed_trash":
        detection = check_detections("trash_box", detections)
        if detection:
            # Move to trash box
            move_to_target(detection, left_motor, right_motor, detections[0])
            continue

    # 4. Drive towards object in the distance
    elif target:
        move_to_target(target, left_motor, right_motor, detections[0])
        continue

    # 5. Avoid deposit box
    if img_recognizer.check_carrying(threshold=0.6) in ["trash_box", "plant_box"]:
        # Drive backwards if near deposit box
        left_motor.run(-3.0)
        right_motor.run(-3.4)
    
    # 6. Search for object (Lowest Priority)
    else:
        left_motor.run(1.5)
        right_motor.run(-1.5)