import numpy as np
import logging
import threading
import queue


class Visualizer:
    def __init__(self, canvas, root):
        self.canvas = canvas
        self.blobs = []
        self.trackers = []
        self.connection_visualisation = "None"
        self.range_min = -4
        self.range_max = 4
        self.draw_blobs = False
        self.thread = None
        self.running = False
        self.queue = queue.Queue()
        self.radius = 1
        self.visualize = True
        self.root = root
        self.scale = 1 / self.range_max
        
        self.canvas.update_idletasks()
        self.canvas.update()
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()
        
        
    def set_visualize(self, vis):
        self.visualize = vis
        
    def set_connection_visualisation(self, type):
        """Set the visualisation mode."""
        self.connection_visualisation = type
        
    def set_draw_blobs(self, draw_blobs):
        """Set whether to draw blobs or not."""
        self.draw_blobs = draw_blobs
        
    def set_radius(self, radius):
        """Set the radius for the visualizer."""
        self.radius = radius

    def transform_to_polar(self, x, y):
        """Convert Cartesian coordinates to polar coordinates."""
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        return r, theta
    
    def normalize(self, x, y):
        return x * self.scale, y * self.scale
    
    def transform_to_cartesian(self, r, theta):
        
        """Convert polar coordinates to Cartesian coordinates."""
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return x, y
    
    def push_magnitude(self, x, y, magnitude):
        """Push the magnitude to the x and y coordinates."""
        r, theta = self.transform_to_polar(x, y)
        r += magnitude
        x, y = self.transform_to_cartesian(r, theta)
        return x, y
    

    def create_circle(self, canvas, x, y, r, **kwargs): #center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return canvas.create_oval(x0, y0, x1, y1, **kwargs)

    
    def map_to_image_coordinates(self, x, y, width, height, range_min, range_max):
        """Map the x and y coordinates to image coordinates."""
        x = (x - range_min) / (range_max - range_min) * width
        y = height - (y - range_min) / (range_max - range_min) * height
        return x, y
    
    def draw_coordinate_system(self):
        """Draw the coordinate system on the canvas."""
        width = self.width
        height = self.height
        
        # draw a thin lined circle around the perimeter
        self.create_circle(
            self.canvas,
            width / 2,
            height / 2,
            width / 2,
            outline="black",
            width=1,
        )
        
        # draw the coordinate system
        self.canvas.create_line(
            0, height / 2, width, height / 2, fill="black", dash=(2, 2)
        )
        self.canvas.create_line(
            width / 2, 0, width / 2, height, fill="black", dash=(2, 2)
        )
        # draw the center
        self.canvas.create_oval(
            width / 2 - 5,
            height / 2 - 5,
            width / 2 + 5,
            height / 2 + 5,
            fill="black",
            outline="",
        )

    def update_canvas(self, blobs, trackers, radius):
        """blobs and tracker are in the range of [-4, 4]"""
        width = self.width
        height = self.height
        self.canvas.delete("all")
        if self.draw_blobs:
            # draw the blobs
            for blob in blobs:
                x, y = blob[0], blob[1]
                # x, y = self.push_magnitude(x, y, radius)
                # x, y = self.normalize(x, y)
                r = blob[2] * width / 16 * radius
                x, y = self.map_to_image_coordinates(x, y, width, height, self.range_min, self.range_max)
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", outline="")
            connectors = []
        
        self.draw_coordinate_system()
        
        # draw the trackers
        connectors = []
        for tracker in trackers:
            col = "green" if tracker["is_tracked"] else "blue"
            x, y = tracker["position"][0], tracker["position"][2]
            # x, y = self.normalize(x, y)
            # x, y = self.push_magnitude(x, y, radius)
            x, y = self.map_to_image_coordinates(x, y, width, height, self.range_min, self.range_max)
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=col, outline="")
            self.canvas.create_text(
                x, y - 10, text=tracker["name"], fill="black", font=("Arial", 8)
            )
            if tracker["is_tracked"]:
                connectors.append((x, y))

        # draw connections
        if self.connection_visualisation == "all_in_radius":
            self.draw_to_all_in_radius(connectors, radius=radius * width / 8)
        elif self.connection_visualisation == "nearest":
            self.draw_to_nearest_neighbor(connectors)
        elif self.connection_visualisation == "unique":
            self.unique_connection(connectors)
        elif self.connection_visualisation == "unique_w_tracing":
            self.unique_connection_w_tracing(connectors)


    def unique_connection(self, positions):

        x_positions, y_positions = zip(*positions)

        number_trackers = len(x_positions)
        visited = [False] * number_trackers  # Track visited nodes
        current_index = 0  # Start with the first tracker
        visited[current_index] = True
        path = [current_index]  # Store the order of visited nodes

        for _ in range(number_trackers - 1):
            shortest_distance = float("inf")
            closest_index = -1

            for j in range(number_trackers):
                if not visited[j]:  # Only consider unvisited nodes
                    distance = np.sqrt(
                        (x_positions[current_index] - x_positions[j]) ** 2
                        + (y_positions[current_index] - y_positions[j]) ** 2
                    )
                    if distance < shortest_distance:
                        shortest_distance = distance
                        closest_index = j

            # Mark the closest node as visited and draw a line
            visited[closest_index] = True
            path.append(closest_index)
            self.draw_connection(
                x_positions[current_index],
                y_positions[current_index],
                x_positions[closest_index],
                y_positions[closest_index],
            )

            # Move to the next tracker
            current_index = closest_index

    def unique_connection_w_tracing(self, positions):
        # list of start x, y
        start_list = positions
        # list of end x, y
        end_list = positions.copy()[1:]

        # Start with the first point in the start_list
        current_start = start_list[0]
        while end_list:
            shortest_distance = float("inf")
            closest_end = None  # Track the closest end point
            for end in end_list:
                if end == current_start:
                    continue
                # calculate the distance between the two points
                distance = np.sqrt(
                    (current_start[0] - end[0]) ** 2 + (current_start[1] - end[1]) ** 2
                )
                # check if the distance is less than the shortest distance
                if distance < shortest_distance:
                    # update the shortest distance
                    shortest_distance = distance
                    # update the closest end point
                    closest_end = end
            if closest_end:
                # draw a line between the current start and the closest end point
                self.draw_connection(
                    current_start[0], current_start[1], closest_end[0], closest_end[1]
                )
                # remove the closest end point from the list
                end_list.remove(closest_end)
                # update the current start to the closest end point
                current_start = closest_end

    def draw_to_nearest_neighbor(self, positions):
        """Draw lines to the nearest neighbor for each point in the list."""
        for i, start in enumerate(positions):
            nearest_distance = float("inf")
            nearest_index = -1
            for j, end in enumerate(positions):
                if i != j:
                    distance = np.sqrt(
                        (start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2
                    )
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_index = j
            if nearest_index != -1:
                self.draw_connection(
                    start[0],
                    start[1],
                    positions[nearest_index][0],
                    positions[nearest_index][1],
                )

    def draw_to_all_in_radius(self, positions, radius=40):
        """Draw lines to all points within a given radius."""
        for i, start in enumerate(positions):
            for j, end in enumerate(positions):
                if i != j:
                    distance = np.sqrt(
                        (start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2
                    )
                    if distance <= radius:
                        self.draw_connection(start[0], start[1], end[0], end[1])

    def draw_connection(self, x1, y1, x2, y2):
        """Draw a line between two points on the canvas."""
        # Convert the coordinates to the canvas coordinate system
        self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)


    def start(self):
        """Start the visualizer thread."""
        if self.thread is None or not self.thread.is_alive():
            self.running = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
        else:
            logging.warning("Visualizer thread is already running.")
        return True
    
    def stop(self):
        """Stop the visualizer thread."""
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None
        logging.info("Visualizer thread stopped.")
        
    def run(self):
        """Run the visualizer thread."""
        odd = False
        self.draw_coordinate_system()
        while self.running:
            
            data = self.queue.get()
            if data is None:
                continue
            self.blobs, self.trackers = data
            
            odd = not odd
            if odd:
                continue
            
            # Update the canvas with the blobs and trackers
            if self.visualize:
                self.update_canvas(self.blobs, self.trackers, self.radius)
                self.canvas.after(10)
            
    def close(self):
        """Close the visualizer."""
        self.stop()
        logging.info("Visualizer closed.")
        
    def update(self, blobs, trackers):
        """Push data to the visualizer."""
        self.queue.put((blobs, trackers))