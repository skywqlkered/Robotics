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
    
def move_to_target(object: dict, left_motor, right_motor, obstacle: dict = False, base_speed: float = 4):
    x,y = object["position"]
    setpoint = 32

    steer = (x - setpoint)/16

    # Er moet een check voor wat hij vast heeft en dit moet weg!
    if obstacle:
        if obstacle["name"] != object["name"] and obstacle["position"][0] > 10 and obstacle["position"][0] < 54 and obstacle["position"][1] < 54:
            steer -= obstacle["position"][0]/16

    left_motor.run(max(min(base_speed + steer, 5), -5))
    right_motor.run(max(min(base_speed - steer, 5), -5))