import math
import copy

class ViveAugmentor:
    def __init__(self):
        self.fake_tracker_names = [
            '2B9219F0', 
            'CB171D68', 
            '4CDFCB9B', 
            '2B9219F1', 
            'CB171D69', 
            '4CDFCB9C', 
            '2B9219F2',
            'CB171D60', 
            '4CDFCB9D', 
            '2B9219F3', 
            'CB171D61', 
            '4CDFCB9E', 
            '2B9219F4', 
            'CB171D62', 
            '4CDFCB9F', 
            '2B9219F5', 
            'CB171D63', 
            '4CDFCB9G', 
            '2B9219F6', 
            'CB171D64'
            ]

    def augment(self, decoded_data, slider_value):
        # process data
        num_devices = len(decoded_data)
        # print('num_devices:', num_devices)

        if num_devices == slider_value:
            # No augmentation needed
            return decoded_data
        elif num_devices > slider_value:
            # Reduce the number of devices
            decoded_augm_data = decoded_data[:slider_value]
        else:
            decoded_augm_data = decoded_data.copy()

            # Add more devices by rotating x, y values in a circle
            for i in range(slider_value - num_devices):
                device = copy.deepcopy(decoded_data[i % num_devices])  # Use modulo to cycle through existing devices
                device['name'] = self.fake_tracker_names[i]  # Assign a unique name from the list

                # Get the original x, y values
                x, y = device['position'][0], device['position'][1]

                # Calculate a unique rotation angle based on the augmentation index
                angle = (2 * math.pi / (slider_value - num_devices)) * (i + 1)  # Shift by 1 to avoid zero angle
                # Rotate the x, y values
                new_x = x * math.cos(angle) - y * math.sin(angle)
                new_y = x * math.sin(angle) + y * math.cos(angle)

                # Ensure the values stay within the range of -4 to 4
                new_x = (new_x % 8) - 4 if new_x > 4 or new_x < -4 else new_x
                new_y = (new_y % 8) - 4 if new_y > 4 or new_y < -4 else new_y

                # assert new_x != x or new_y != y, "Augmented device has the same position as the original device"

                # Update the device's position
                device['position'][0] = new_x
                device['position'][1] = new_y

                # Append the augmented device to the list
                decoded_augm_data.append(device)

        return decoded_augm_data