import numpy as np
import logging


class ViveVisualizer:
    def __init__(self, canvas):
        self.canvas = canvas
        self.blobs = []
        self.trackers = []
        self.connection_visualisation = "None"
        
    def set_connection_visualisation(self, type):
        """Set the visualisation mode."""
        self.connection_visualisation = type

    def update_canvas(self, blobs, trackers, radius):
        """blobs and tracker are in the range of [-4, 4]"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.delete("all")
        # draw the blobs
        for blob in blobs:
            x, y = blob[0], blob[1]
            r = blob[2] * width / 16 * radius
            x = (x + 4) / 8 * width
            y = height - (y + 4) / 8 * height
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", outline="")
        connectors = []
        # draw the trackers
        for tracker in trackers:
            x, y = tracker["position"][0], tracker["position"][2]
            x = (x + 4) / 8 * width
            y = height - (y + 4) / 8 * height
            self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill="blue", outline="")
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
            fill="green",
            outline="",
        )

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
