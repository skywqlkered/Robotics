# Robotics
this is the robot

# Wall-E subsumption

Hierarchy:
1. search (rotate until object found)
2. battery (if below threshold, go to yellow)
3. interact with object (if green: go to blue, if brown: compact, if black: move to red)
    local green = {76, 255, 0}
    local brown = {178, 76, 0}
    local black = {0, 0, 0}