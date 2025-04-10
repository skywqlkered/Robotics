import cv2

class ImageRecognizer:
    brown_range = []
    green_range = []
    yellow_range = []
    red_range = []
    black_range = []
    blue_range = []

    color_map = {'trash': brown_range, 'compressed_trash': black_range, 'plant': green_range, 'charge_station': yellow_range, 'plant_box': blue_range, 'trash_box': red_range}

    def __init__(self, top_image_sensor, small_image_sensor):
        self.top_image_sensor = top_image_sensor
        self.small_image_sensor = small_image_sensor
        self.top_image = None
        self.small_image = None

    def update_images(self):
        self.top_image_sensor._update_image()
        self.small_image_sensor._update_image()
        self.top_image = self.top_image_sensor.get_image()
        self.small_image - self.small_image_sensor.get_image()
    
    def get_object_position(self, object: str) -> float:
        """"
        Finds the position of a specified object in the screen, if present.
        Updates both images.

        Returns:
            float: The position of the object on the x-axis, normalized (from -1.0 to 1.0), None if not present
        """
        self.update_images()
        pass

    def find_objects(self) -> str:
        """
        Find all objects in the top image.
        Updates both images.

        Returns:
            list[str]: A list of object names, sorted by area in the image, None if none
        """
        self.update_images()
        return
    
    def check_carrying(self):
        """
        Checks the color of the center pixel of the small sensor.

        Returns:
            str: object name of the object detected.
        """
