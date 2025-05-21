import numpy as np
reflect_list = []
with open ("reflectiondata.txt", "r") as f:
    for x in f.read().split(","):
        if "." in x and x != "0.0":
            reflect_list.append(float(x))

print(max(reflect_list))
print(min(reflect_list))
print(np.mean([max(reflect_list), min(reflect_list)]))