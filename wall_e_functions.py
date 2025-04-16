def check_detections(object: str, detections: list):
    for detection in detections:
        if detection["name"] == object:
            return detection
    return False

def get_largest_block(detections: list):
    for detection in detections:
        if detection["name"] in ["plant", "trash", "compressed_trash"]:
            return detection
    return False
    
def move_to_target(object: str, left_motor, right_motor, base_speed: float = 1):
    x,y = object["position"]
    setpoint = 32

    steer = (x - setpoint)/16

    left_motor.run(max(min(base_speed + steer, 2), -2))
    right_motor.run(max(min(base_speed - steer, 2), -2))