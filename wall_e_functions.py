def check_detections(object: str, detections: list):
    """
    Check if a specific object is in the list of detections.
    
    Args:
        object (str): The name of the object to check for.
        detections (list): A list of detections, where each detection is a dictionary with a "name" key."
    Returns:
        dict or bool: The detection dictionary if the object is found, otherwise False.
    """
    for detection in detections:
        if detection["name"] == object:
            return detection
    return False

def get_largest_block(detections: list):
    """
    Get the largest block from a list of detections.
    
    Args:
        detections (list): A list of detections, where each detection is a dictionary with a "name" and "size" key.
    Returns:
        dict or bool: The largest block detection dictionary if found, otherwise False.
    """
    for detection in detections:
        if detection["name"] in ["plant", "trash", "compressed_trash"]:
            return detection
    return False
    
def move_to_target(object: dict, left_motor, right_motor, obstacle: dict = False, base_speed: float = 4):
    """
    Move towards a target object by adjusting the speed of the motors based on the object's position.
    
    Args:
        object (dict): The target object with a "position" key containing its coordinates.
        left_motor: The left motor object to control.
        right_motor: The right motor object to control.
        obstacle (dict, optional): An obstacle object with a "position" key to avoid.
        base_speed (float, optional): The base speed for the motors. Defaults to 4.
    """

    # Get the x and y position of the object
    x,y = object["position"]

    # Setpoint is the center of the image (64x64 image)
    setpoint = 32

    # Calculate the steering value based on the error from the setpoint
    steer = (x - setpoint)/16

    # Old logic for obstacle avoidance (commented out)
    # if obstacle:
    #     if obstacle["name"] not in [object["name"], "charge_station", "plant_box", "trash_box"] and obstacle["position"][0] > 10 and obstacle["position"][0] < 54 and obstacle["position"][1] < 54:
    #         steer -= obstacle["position"][0]/16
    #         print("avoiding", steer)

    # Run the motors with the calculated speed and steering adjustment
    left_motor.run(max(min(base_speed + steer, 5), -5))
    right_motor.run(max(min(base_speed - steer, 5), -5))