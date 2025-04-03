import os
import numpy as np
from matplotlib import pyplot as plt

class ImageGenerator:
    def __init__(self):
        self.dataset_path = os.path.join(os.path.dirname(__file__), 'data')
        self.image_size = (28, 28)
        self.image_count = 0
        self.image_format = 'png'
        self.position_range = (-4, 4)

    def set_dataset_path(self, dataset_path):
        try:
            if not os.path.exists(dataset_path):
                os.makedirs(dataset_path)
            if not os.path.isdir(dataset_path):
                raise ValueError(f"{dataset_path} is not a directory.")
            self.dataset_path = dataset_path
        except Exception as e:
            raise ValueError(f"Failed to set dataset path: {e}")

    def generate_image(self, tracker_data):
        def draw_line(image, x1, y1, x2, y2, value=255):
            # Bresenham's Line Algorithm
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            sx = 1 if x1 < x2 else -1
            sy = 1 if y1 < y2 else -1
            err = dx - dy

            while True:
                # Set the pixel value
                if 0 <= x1 < image.shape[0] and 0 <= y1 < image.shape[1]:
                    image[x1, y1] = value

                # Break if the end point is reached
                if x1 == x2 and y1 == y2:
                    break

                e2 = 2 * err
                if e2 > -dy:
                    err -= dy
                    x1 += sx
                if e2 < dx:
                    err += dx
                    y1 += sy

        # create image with black background and white pixels for the position
        image = np.zeros((self.image_size[0], self.image_size[1]), dtype=np.uint8)
        image_orig = np.zeros((self.image_size[0], self.image_size[1]), dtype=np.uint8)
        # create the image path
        image_path = os.path.join(self.dataset_path, f"{self.image_count}.{self.image_format}")
        image_path_orig = os.path.join(self.dataset_path, f"{self.image_count}_orig.{self.image_format}")
        self.image_count += 1

        # save the x, y positions of the trackers for later use
        x_positions = []
        y_positions = []

        for tracker in tracker_data:
            # name = tracker['name']
            x = tracker['position'][0]
            y = tracker['position'][2]

            # normalize x, y to the image range 
            old_min = self.position_range[0]
            old_max = self.position_range[1]
            new_min = 0
            new_max = self.image_size[0]
            # formula output = new_min + ((new_max - new_min) / (old_max - old_min)) * (input - old_min)
            x = int(new_min + ((new_max - new_min) / (old_max - old_min)) * (x - old_min))
            y = int(new_min + ((new_max - new_min) / (old_max - old_min)) * (y - old_min))

            # x = int((x - self.position_range[0]) / (self.position_range[1] - self.position_range[0]) * self.image_size[0])
            # y = int((y - self.position_range[0]) / (self.position_range[1] - self.position_range[0]) * self.image_size[1])
            # check if the position is within the image range
            if x < 0 or x >= self.image_size[0] or y < 0 or y >= self.image_size[1]:
                raise ValueError(f"Position ({x}, {y}) is out of image range.")

            image[x, y] = 255
            image_orig[x, y] = 255
            x_positions.append(x)
            y_positions.append(y)
            # # create a white pixel at the position and a radius around it
            # radius = 0
            # for i in range(-radius, radius + 1):
            #     for j in range(-radius, radius + 1):
            #         if i**2 + j**2 <= radius**2:
            #             if 0 <= x + i < self.image_size[0] and 0 <= y + j < self.image_size[1]:
            #                 image[x + i, y + j] = 255

        # compute the distances between the trackers
        # is_visited = np.zeros(len(tracker_data), dtype=bool)
        # Ensure each pixel is connected to its nearest neighbor and visited once
        visited = [False] * len(tracker_data)  # Track visited nodes
        current_index = 0  # Start with the first tracker
        visited[current_index] = True
        path = [current_index]  # Store the order of visited nodes

        for _ in range(len(tracker_data) - 1):
            shortest_distance = float('inf')
            closest_index = -1

            for j in range(len(tracker_data)):
                if not visited[j]:  # Only consider unvisited nodes
                    distance = np.sqrt((x_positions[current_index] - x_positions[j]) ** 2 +
                                    (y_positions[current_index] - y_positions[j]) ** 2)
                    if distance < shortest_distance:
                        shortest_distance = distance
                        closest_index = j

            # Mark the closest node as visited and draw a line
            visited[closest_index] = True
            path.append(closest_index)
            print(f"Drawing line between ({x_positions[current_index]}, {y_positions[current_index]}) and "
                f"({x_positions[closest_index]}, {y_positions[closest_index]})")
            print(f"Distance: {shortest_distance}")
            draw_line(image, x_positions[current_index], y_positions[current_index],
                    x_positions[closest_index], y_positions[closest_index])

            # Move to the next tracker
            current_index = closest_index

        # Close the loop by connecting the last tracker to the first tracker
        # draw_line(image, x_positions[path[-1]], y_positions[path[-1]],
                # x_positions[path[0]], y_positions[path[0]])
        print(f"Drawing line between ({x_positions[path[-1]]}, {y_positions[path[-1]]}) and "
            f"({x_positions[path[0]]}, {y_positions[path[0]]})")
                # draw a line between the last and the first tracker
                # draw_line(image, x_positions[-1], y_positions[-1], x_positions[0], y_positions[0])
        

        # save the image as a png file
        plt.imsave(image_path, image, cmap='gray')   
        plt.imsave(image_path_orig, image_orig, cmap='gray')         
        # print the image path
        print(f"Image saved at {image_path}")

        # return the image
        return image_orig, image




