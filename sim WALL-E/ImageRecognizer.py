import cv2
import numpy as np
import math

class ImageRecognizer:

    # HSV color ranges for different objects
    # The ranges are defined in the format (lower_bound, upper_bound)
    color_ranges = {
        "plant": [((36, 100, 70), (85, 255, 255))],
        "trash": [((5, 80, 30), (24, 255, 180))],
        "compressed_trash": [((0, 0, 0), (180, 255, 69))],
        "trash_box": [
                      ((0, 140, 100), (4, 255, 255)),      # Lower red part (H: 0-4)
                      ((173, 120, 80), (180, 255, 255))   # Upper red part (H: 173-180)
                     ],
        "charge_station": [((25, 100, 100), (35, 255, 255))],
        "plant_box": [((90, 100, 70), (125, 255, 255))]
    }

    
    # Colors dictionary for visualization (BGR format for OpenCV)
    _colors = {
        'plant': (0, 255, 76),             # Green BGR
        'trash': (0, 76, 178),             # Brown BGR
        'compressed_trash': (0, 0, 0),     # Black BGR
        'trash_box': (0, 0, 217),          # Red BGR
        'charge_station': (0, 255, 255),   # Yellow BGR
        'plant_box': (240, 188, 0),        # Blue BGR
    }
    _background_bgr = (255, 255, 255)      # White BGR
    _outline_bgr = (0, 0, 0)               # Black BGR

    def __init__(self, top_image_sensor, small_image_sensor):
        self.top_image_sensor = top_image_sensor
        self.small_image_sensor = small_image_sensor
        self.update_images()

    def update_images(self):
        """
        Updates the images from the sensors.
        Images are RGB format.
        """
        self.top_image_sensor._update_image()
        self.small_image_sensor._update_image()
        self.top_image = self.top_image_sensor.get_image()[3:] # Exclude the first 3 lines (sky)
        self.small_image = self.small_image_sensor.get_image()
    
    def find_objects(self, update=True, detection_threshold=5, exclude_sky = True, use_top_img = True) -> str:
        """
        Find all objects in the top image.

        Args:
            update (bool): If True, updates the images from the sensors.
            detection_threshold (int): Minimum area of the object to be detected.
            exclude_sky (bool): If True, excludes the sky from detection (largest black area).
            use_top_img (bool): If True, uses the top image for detection, otherwise uses the small image.

        Returns:
            list[dict]: A list of dictionaries, with names as keys and a tuple of: size (area) and a tuple of: x and y coordinate of the center), sorted by area in the image, None if none
        """
        if update: self.update_images()

        if use_top_img:
            # Use the top image for detection
            image = self.top_image
        else:
            # Use the small image for detection
            image = self.small_image

        # Return empty list if no image is available
        if image is None:
            print("Warning: Top image is not available.")
            return None
        
        # Convert the image to HSV color space
        hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

        # Initialize a list to store found objects
        objects_found = []
        for object_name, color_range in self.color_ranges.items():

            # Create a mask for the current color range
            mask = cv2.inRange(hsv_image, color_range[0][0], color_range[0][1])
            if object_name == "trash_box":
                mask += cv2.inRange(hsv_image, color_range[1][0], color_range[1][1])

            # Find contours of the masked image
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=4)
            for label in range(1, num_labels):
                area = stats[label, cv2.CC_STAT_AREA]
                # Filter contours based on area
                if area > detection_threshold:
                    # Calculate the center of the contour
                    cx, cy = centroids[label]
                    objects_found.append({
                        "name": object_name,
                        "size": int(area),
                        "position": (int(cx), int(cy))
                    })

        # Sort the found objects by size in descending order
        objects_found = sorted(objects_found, key=lambda x: x["size"], reverse=True)

        # Exclude the largest black area (sky) if specified
        if exclude_sky:
            objects = []
            for obj in objects_found:
                # Don't keep sky
                if obj["name"] == "compressed_trash" and not (obj["position"][1] > 18 and obj["size"] < 500):
                    continue
                # Don't keep roof
                elif obj["name"] == "trash" and obj["position"][1] < 5:
                    continue
                # Keep the rest
                else:
                    objects.append(obj)
            return objects
        else:
            return objects_found
    
    def check_carrying(self, threshold = 0.9, black_threshold = 0.65, update=True):
        """
        Checks if the robot is carrying an object.
        Checks if the object is more than a certain threshold of the small image size.
        If the object is detected, it returns the name of the object.

        Args:
            threshold (float): The threshold for the color detection. The amount of the screen that is within range.
            update (bool): If True, updates the images from the sensors.

        Returns:
            str: object name of the object detected. None if no object is detected.
        """
        try:
            # Get the detections from the top image and objects from the small image
            detections = self.find_objects(update=False, exclude_sky=True)
            objects = self.find_objects(update=update, use_top_img=False, detection_threshold=0, exclude_sky=False)
            
            # If the biggest object's surface area is larger than the threshold, return the name of the object
            if objects[0]["size"] >= threshold * 64 * 64:
                return objects[0]["name"]
            
            # If the biggest object is compressed trash and its surface area is larger than the black threshold, return its name
            elif (objects[0]["size"] >= black_threshold * 64 * 64 or objects[0]["position"][0] > 38 or objects[0]["position"][0] < 26) and objects[0]["name"] == "compressed_trash" and objects[0]["position"][1] > 26 and objects[0]["position"][1] < 38:
                return objects[0]["name"]
            
            # If any object is compressed trash and its position is below a certain threshold in the top image, return its name
            for detection in detections:
                if detection["name"] == "compressed_trash" and detection["position"][1] > 52:
                    return "compressed_trash"
        except:
            return None

    @classmethod
    def create_detection_image(cls, detections, img_size: int = 8):
        """
        OpenCV image creation for detection visualization.
        
        Args:
            detections (list[dict]): List of detected objects with their properties.
            img_size (int): Size of the image in pixels.
        """

        # Create a blank image with the specified background color
        img = np.full((64*img_size, 64*img_size, 3), cls._background_bgr, dtype=np.uint8)

        # Draw each detection on the image
        for det in detections:
            name = det['name']
            size = det['size']*img_size
            pos = det['position']
            center = (int(pos[0]*img_size), int(pos[1]*img_size))
            radius = max(1, int(math.sqrt(size)))
            fill_bgr = cls._colors[name] # Direct BGR lookup

            cv2.circle(img, center, radius, fill_bgr, -1)
            cv2.circle(img, center, radius, cls._outline_bgr, 1)

        # Show the image with detections, without blocking the thread
        cv2.imshow("Detection Image", img)
        cv2.waitKey(1)
