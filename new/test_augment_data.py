import matplotlib.pyplot as plt

from augment_data import augment_data
from vive_decoder import ViveDecoder
from vive_encoder import ViveEncoder

def visualize_devices(decoded_data):
    """
    Visualize the x, y, z positions of devices in a 3D plot and label them with their names.

    :param decoded_data: List of device dictionaries with 'position' and 'name' keys.
    """
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    for device in decoded_data:
        x, y, z = device['position']
        name = device['name']
        ax.scatter(x, y, z, label=name)
        ax.text(x, y, z, name, fontsize=8)

    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_zlabel('Z Position')
    ax.set_title('Device Positions')
    ax.legend(loc='upper left', fontsize='small', bbox_to_anchor=(1.05, 1))

    plt.show()


if __name__ == "__main__":
    byte_data = b'\xae\x08\x072B9219E9\x03d\x01\x01\xeb\x00&?n\x9f{@RQo@\xb91W\xbf\xc9\xc0\x07\xbf\xcdT\xc1=xZj=8992BF03\x03T\x00\x005*M\xc0 B\x05>\n\xbaC\xc0\xc7\x1bq\xbe\xf6Pw\xbf\x1bH\x1d=\xde\x7f\xca=4CDFCB8B\x032\x01\x01=\\\x06\xbf\xc0^\xe1?\x01\xde\xae\xbeu\rD\xbfS\x83\x89=\xe2\xc9\xbf=N\xf4!?3AD07E7B\x04\x00\x01\x01\x99\xd6w@>\xbbl@Dj!\xbf\xe0\xb3{>\xe6\x18%\xbf\x1e\x800>@\xec3?292B164A\x04\x00\x01\x01\xc0\xe4m\xc0X\\s@\xcf\xbe\xc7>\x00)\x80\xbe\x1dH$\xbf\x1d4\x99>l\t)\xbf26D688D6\x04\x00\x01\x01\xefI\xec\xbd\x9c\x02v@\xf4\xe9m@{\xf6\xa3\xbc\xd5\xadq\xbf/m\xa7>9^\x1a\xbd1FA80E86\x04\x00\x01\x01\xd8\xb3R\xbc Gt@\xef\tp\xc0\xe0\xe1\xb7>\xb2\x07-={\t\xee\xbb\x02\xabn?'

    # decode data
    decoder = ViveDecoder()
    decoder.parse_byte_data(byte_data)
    decoded_data = decoder.vr_tracker_devices
    num_devices = len(decoded_data)
    print('num_devices:', num_devices)

    # =============================================================================
    # test 1, no augmentation
    slider_value = num_devices

    augmented_data = augment_data(decoded_data, slider_value)
    visualize_devices(augmented_data)

    assert decoded_data == augmented_data, "Data is not equal to augmented_data"

    # =============================================================================
    # test 2, reduce the number of devices
    slider_value = num_devices - 1

    augmented_data = augment_data(decoded_data, slider_value)
    visualize_devices(augmented_data)
    
    assert len(augmented_data) == slider_value, "Number of devices is not equal to slider_value"

    # =============================================================================
    # test 3, add more devices
    slider_value = num_devices + 19

    augmented_data = augment_data(decoded_data, slider_value)
    visualize_devices(augmented_data)

    assert len(augmented_data) == slider_value, "Number of devices is not equal to slider_value"