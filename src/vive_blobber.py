
import numpy as np


class ViveBlobber:
    def __init__(self, radius=1):
        self.radius = radius

    def get_blobs(self, positions):
        """
        Combines positions into blobs based on a specified radius.

        Args:
            positions: A list of tuples or lists representing (x, y) coordinates.
            radius: The radius used to determine if positions belong to the same blob.

        Returns:
            A list of tuples, where each tuple represents a blob and contains:
                - (x, y) coordinates of the blob's center.
                - The weight of the blob (number of positions within the blob).
        """

        if not positions:
            return []

        positions = np.array(positions)  # Convert to NumPy array for efficient calculations

        blobs = []
        visited = np.zeros(len(positions), dtype=bool)
        blob_indices = [-1] * len(positions)  # Initialize blob indices for each position

        for i in range(len(positions)):
            if visited[i]:
                continue

            current_blob_positions = []
            index_q = [i]
            visited[i] = True
            blob_id = len(blobs)  # Assign a new blob ID

            while index_q:
                index = index_q.pop(0)
                current_blob_positions.append(positions[index])
                blob_indices[index] = blob_id  # Assign the blob ID to this position

                distances = np.linalg.norm(positions - positions[index], axis=1)
                neighbors = np.where((distances <= self.radius) & ~visited)[0]

                for neighbor in neighbors:
                    visited[neighbor] = True
                    index_q.append(neighbor)

            blob_center = np.mean(current_blob_positions, axis=0).astype(np.float32)
            blob_weight = len(current_blob_positions)
            blobs.append((blob_center[0], blob_center[1], blob_weight))

        return blobs, blob_indices
    
    def process_data(self, vr_tracker_data):
        """
        Processes tracker data to assign blob IDs to each tracker.

        Args:
            vr_tracker_data: A list of dictionaries representing tracker devices.

        Returns:
            A list of blobs and the updated tracker data with blob IDs.
        """
        positions = []
        for tracker in vr_tracker_data:
            positions.append(tracker["position"][:2])  # Use only x, y for blob detection

        # Get blobs and blob indices
        blobs, blob_indices = self.get_blobs(positions)

        # Add blob_id to each tracker
        for tracker, blob_id in zip(vr_tracker_data, blob_indices):
            tracker["blob_id"] = blob_id

        return blobs, vr_tracker_data


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    def visualize_blobs(vr_tracker_data, blobs):
        """Visualizes the tracker devices and the generated blobs."""

        if not vr_tracker_data:  # Handle empty input case.
            print("No tracker data to visualize.")
            return

        # Extract positions and tracker names
        positions = [tracker["position"][:2] for tracker in vr_tracker_data]
        tracker_names = [tracker["name"] for tracker in vr_tracker_data]

        x, y = zip(*positions)  # Unpack x and y coordinates
        plt.scatter(x, y, label="Trackers", s=10, c='blue')  # Plot tracker positions

        # Annotate each tracker with its name
        for (x_coord, y_coord, name) in zip(x, y, tracker_names):
            plt.text(x_coord, y_coord, name, fontsize=8, color='black', ha='right', va='bottom')

        # Plot blobs
        for center, weight in blobs:
            circle = plt.Circle(center, weight, color='red', alpha=0.3, fill=True)  # Blob circle
            plt.gca().add_patch(circle)
            plt.text(center[0], center[1], str(weight), color='black', ha='center', va='center') # Blob weight

        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Tracker Devices and Blobs")
        plt.legend()
        plt.axis('equal')  # Ensure circles appear as circles
        plt.show()



    # example 1
    radius = 6
    positions = [(1, 2), (1.5, 2.1), (-5, 6), (5.2, 5.8), (-10, 11), (1, 1), (10.1, 11.2)]

    vive_trackers = [
        {
            'name': f'Tracker_{i}',
            'blob_id': -1,
            'position': [x, y, 0.0]
        }
        for i, (x, y) in enumerate(positions)
    ]

    detector = ViveBlobber(radius)

    blobs, vr_tracker_data = detector.process_data(vive_trackers)
    visualize_blobs(vive_trackers, blobs)

    # example 2
    radius = 3  
    positions = [(1, 2), (1.5, 2.1), (1.8, 1.9), (5, 6), (5.2, 5.8), (10, 11), (1, 1), (10.1, 11.2), (10.3, 11.1)]
    
    vive_trackers = [
        {
            'name': f'Tracker_{i}',
            'blob_id': -1,
            'position': [x, y, 0.0]
        }
        for i, (x, y) in enumerate(positions)
    ]

    detector = ViveBlobber(radius)
    blobs, vr_tracker_data = detector.process_data(vive_trackers)
    visualize_blobs(vive_trackers, blobs)
