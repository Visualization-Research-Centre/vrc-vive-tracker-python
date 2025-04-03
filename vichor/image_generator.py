import numpy as np
import os
import matplotlib.pyplot as plt

class ImageGenerator:
    def __init__(self):
        self.dataset_path = os.path.join(os.path.dirname(__file__), 'data')
        self.image_format = 'png'
        self.image_size = (28, 28)
        self.image_count = 0
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
        

    def generate_image(self, tracker_data, save_image=False):
        def normalize(x, y):
            old_min = self.position_range[0]
            old_max = self.position_range[1]
            new_min = 0
            new_max = self.image_size[0]

            # Normalize x, y to the image range
            x = int(new_min + ((new_max - new_min) / (old_max - old_min)) * (x - old_min))
            y = int(new_min + ((new_max - new_min) / (old_max - old_min)) * (y - old_min))

            # check if the position is within the image range
            if x < 0 or x >= self.image_size[0] or y < 0 or y >= self.image_size[1]:
                raise ValueError(f"Position ({x}, {y}) is out of image range.")
            
            return x, y
        
        def unique_connection(x_positions, y_positions):
            number_trackers = len(x_positions)
            visited = [False] * number_trackers  # Track visited nodes
            current_index = 0  # Start with the first tracker
            visited[current_index] = True
            path = [current_index]  # Store the order of visited nodes

            for _ in range(number_trackers - 1):
                shortest_distance = float('inf')
                closest_index = -1

                for j in range(number_trackers):
                    if not visited[j]:  # Only consider unvisited nodes
                        distance = np.sqrt((x_positions[current_index] - x_positions[j]) ** 2 +
                                        (y_positions[current_index] - y_positions[j]) ** 2)
                        if distance < shortest_distance:
                            shortest_distance = distance
                            closest_index = j

                # Mark the closest node as visited and draw a line
                visited[closest_index] = True
                path.append(closest_index)
                draw_line(image, x_positions[current_index], y_positions[current_index],
                        x_positions[closest_index], y_positions[closest_index])

                # Move to the next tracker
                current_index = closest_index

            return image_orig, image
        
        def unique_connection_w_tracing(x_positions, y_positions):
            # list of start x, y
            start_list = list(zip(x_positions, y_positions))
            # list of end x, y
            end_list = list(zip(x_positions[1:], y_positions[1:]))
            
            # Start with the first point in the start_list
            current_start = start_list[0]
            while end_list:
                shortest_distance = float('inf')
                closest_end = None  # Track the closest end point
                for end in end_list:
                    if end == current_start:
                        continue
                    # calculate the distance between the two points
                    distance = np.sqrt((current_start[0] - end[0]) ** 2 + (current_start[1] - end[1]) ** 2)
                    # check if the distance is less than the shortest distance
                    if distance < shortest_distance:
                        # update the shortest distance
                        shortest_distance = distance
                        # update the closest end point
                        closest_end = end
                if closest_end:
                    # draw a line between the current start and the closest end point
                    draw_line(image, current_start[0], current_start[1], closest_end[0], closest_end[1])
                    # remove the closest end point from the list
                    end_list.remove(closest_end)
                    # update the current start to the closest end point
                    current_start = closest_end

            return image_orig, image

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
            x, y = normalize(x, y)

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
        # alg 1
        image_orig, image = unique_connection(x_positions, y_positions)

        # alg 2
        image_orig, image = unique_connection_w_tracing(x_positions, y_positions)

        # save the image
        if save_image:
            plt.imsave(image_path, image, cmap='gray')   
            plt.imsave(image_path_orig, image_orig, cmap='gray')    
            print(f"Image saved at {image_path}")   
        
        # return the image
        return image_orig, image
        


