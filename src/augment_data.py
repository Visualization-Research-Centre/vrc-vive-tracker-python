import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from vive_decoder import ViveDecoder
from vive_encoder import ViveEncoder
import copy

# create a fake list of device names for augmentation
device_names = ['2B9219F0', 
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

def augment_data(byte_data, slider_value):

    # Decode and encode data
    decoder = ViveDecoder()
    decoder.parse_byte_data(byte_data)
    decoded_data = decoder.vr_tracker_devices

    # process data
    num_devices = len(decoded_data)
    print('num_devices:', num_devices)

    if num_devices == slider_value:
        # No augmentation needed
        return byte_data, decoded_data, decoded_data
    elif num_devices > slider_value:
        # Reduce the number of devices
        decoded_augm_data = decoded_data[:slider_value]
    else:
        decoded_augm_data = decoded_data.copy()

        # Add more devices by rotating x, y values in a circle
        for i in range(slider_value - num_devices):
            device = copy.deepcopy(decoded_data[i % num_devices])  # Use modulo to cycle through existing devices
            device['name'] = device_names[i]  # Assign a unique name from the list

            # Get the original x, y values
            x, y = device['position'][0], device['position'][1]
            print('x, y:', x, y)
            # Calculate a unique rotation angle based on the augmentation index
            angle = (2 * math.pi / (slider_value - num_devices)) * (i + 1)  # Shift by 1 to avoid zero angle
            # Rotate the x, y values
            new_x = x * math.cos(angle) - y * math.sin(angle)
            new_y = x * math.sin(angle) + y * math.cos(angle)

            # Ensure the values stay within the range of -4 to 4
            new_x = (new_x % 8) - 4 if new_x > 4 or new_x < -4 else new_x
            new_y = (new_y % 8) - 4 if new_y > 4 or new_y < -4 else new_y

            assert new_x != x or new_y != y, "Augmented device has the same position as the original device"

            # Update the device's position
            device['position'][0] = new_x
            device['position'][1] = new_y

            # Append the augmented device to the list
            decoded_augm_data.append(device)

    # encode the data back
    encoder = ViveEncoder()
    encoder.vr_tracker_devices = decoded_augm_data
    encoded_data = encoder.return_byte_data()

    return encoded_data, decoded_data, decoded_augm_data


def visualize_devices(decoded_data, decoded_augm_data):
    """
    Visualize the x, y, z positions of devices in a 3D plot and label them with their names.

    :param decoded_data: List of device dictionaries with 'position' and 'name' keys.
    """
    fig = plt.figure(figsize=(12, 6))

    # Original data subplot
    ax1 = fig.add_subplot(121, projection='3d')
    for device in decoded_data:
        x, y, z = device['position']
        name = device['name']
        ax1.scatter(x, y, z, label=name)
        ax1.text(x, y, z, name, fontsize=8)
    ax1.set_xlabel('X Position')
    ax1.set_ylabel('Y Position')
    ax1.set_zlabel('Z Position')
    ax1.set_title('Original Device Positions')
    ax1.legend(loc='upper left', fontsize='small', bbox_to_anchor=(1.05, 1))

    # Augmented data subplot
    ax2 = fig.add_subplot(122, projection='3d')
    for device in decoded_augm_data:
        x, y, z = device['position']
        name = device['name']
        ax2.scatter(x, y, z, label=(name, x, y, z))
        ax2.text(x, y, z, name, fontsize=8)
    ax2.set_xlabel('X Position')
    ax2.set_ylabel('Y Position')
    ax2.set_zlabel('Z Position')
    ax2.set_title('Augmented Device Positions')
    ax2.legend(loc='upper left', fontsize='small', bbox_to_anchor=(1.05, 1))

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    byte_data = b'\xae\x08\x072B9219E9\x03d\x01\x01\xeb\x00&?n\x9f{@RQo@\xb91W\xbf\xc9\xc0\x07\xbf\xcdT\xc1=xZj=8992BF03\x03T\x00\x005*M\xc0 B\x05>\n\xbaC\xc0\xc7\x1bq\xbe\xf6Pw\xbf\x1bH\x1d=\xde\x7f\xca=4CDFCB8B\x032\x01\x01=\\\x06\xbf\xc0^\xe1?\x01\xde\xae\xbeu\rD\xbfS\x83\x89=\xe2\xc9\xbf=N\xf4!?3AD07E7B\x04\x00\x01\x01\x99\xd6w@>\xbbl@Dj!\xbf\xe0\xb3{>\xe6\x18%\xbf\x1e\x800>@\xec3?292B164A\x04\x00\x01\x01\xc0\xe4m\xc0X\\s@\xcf\xbe\xc7>\x00)\x80\xbe\x1dH$\xbf\x1d4\x99>l\t)\xbf26D688D6\x04\x00\x01\x01\xefI\xec\xbd\x9c\x02v@\xf4\xe9m@{\xf6\xa3\xbc\xd5\xadq\xbf/m\xa7>9^\x1a\xbd1FA80E86\x04\x00\x01\x01\xd8\xb3R\xbc Gt@\xef\tp\xc0\xe0\xe1\xb7>\xb2\x07-={\t\xee\xbb\x02\xabn?'
    slider_value = 20

    augmented_data, dec_data, dec_augm_data = augment_data(byte_data, slider_value)

    visualize_devices(dec_data, dec_augm_data)
