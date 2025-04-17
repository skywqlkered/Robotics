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
    
def move_to_target(object: dict, left_motor, right_motor, obstacle: dict = False, base_speed: float = 6):
    x,y = object["position"]
    setpoint = 32

    steer = (x - setpoint)/12

    # if obstacle:
    #     if obstacle["name"] not in [object["name"], "charge_station", "plant_box", "trash_box"] and obstacle["position"][0] > 10 and obstacle["position"][0] < 54 and obstacle["position"][1] < 54:
    #         steer -= obstacle["position"][0]/16
    #         print("avoiding", steer)

    left_motor.run(max(min(base_speed + steer, 7), -7))
    right_motor.run(max(min(base_speed - steer, 7), -7))