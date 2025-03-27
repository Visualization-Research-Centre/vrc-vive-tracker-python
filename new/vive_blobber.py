
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

        for i in range(len(positions)):
            if visited[i]:
                continue

            current_blob_positions = []
            index_q = [i]
            visited[i] = True

            while index_q:
                index = index_q.pop(0)
                current_blob_positions.append(positions[index])

                distances = np.linalg.norm(positions - positions[index], axis=1)
                neighbors = np.where((distances <= radius) & ~visited)[0]

                for neighbor in neighbors:
                    visited[neighbor] = True
                    index_q.append(neighbor)

            blob_center = np.mean(current_blob_positions, axis=0)
            blob_weight = len(current_blob_positions)
            blobs.append((tuple(blob_center), blob_weight))

        return blobs
    
    def process_data(self, vr_tracker_data):
        positions = []
        for tracker in vr_tracker_data:
            positions.append(tracker["position"])
        blobs = self.get_blobs(positions, radius)
        return blobs


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    def visualize_blobs(positions, blobs):
        """Visualizes the positions and the generated blobs."""

        if not positions:  # Handle empty input case.
            print("No positions to visualize.")
            return

        x, y = zip(*positions)  # Unpack x and y coordinates
        plt.scatter(x, y, label="Original Positions", s=10, c='blue')  # Plot original positions

        for center, weight in blobs:
            circle = plt.Circle(center, weight, color='red', alpha=0.3, fill=True)  # Blob circle
            plt.gca().add_patch(circle)
            plt.text(center[0], center[1], str(weight), color='black', ha='center', va='center') # Blob weight

        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Position Blobs")
        plt.legend()
        plt.axis('equal')  # Ensure circles appear as circles
        plt.show()



    # Example usage:
    radius = 6
    positions = [(1, 2), (1.5, 2.1), (-5, 6), (5.2, 5.8), (-10, 11), (1, 1), (10.1, 11.2)]
    positions2 = [(1, 2), (1.5, 2.1), (1.8, 1.9), (5, 6), (5.2, 5.8), (10, 11), (1, 1), (10.1, 11.2), (10.3, 11.1)]

    detector = ViveBlobber(radius)

    blobs = detector.get_blobs(positions)
    visualize_blobs(positions, blobs)

    blobs = detector.get_blobs(positions2)
    visualize_blobs(positions2, blobs)
