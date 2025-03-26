import os
import time
import struct
import numpy as np
from threading import Lock
from tracker_decoder import TrackerDecoder

def read_recorded_data(file_path):
    recorded_data = []
    with open(file_path, 'r') as file:
        for line in file:
            timestamp_str, byte_data_str = line.strip().split(':', 1)
            timestamp = struct.unpack('<f', bytes.fromhex(timestamp_str))[0]
            byte_data = bytes.fromhex(byte_data_str)
            recorded_data.append((timestamp, byte_data))
    return recorded_data


def extract_position_data(decoded_data):
    position_data_list = []

    decoder = TrackerDecoder()
    for timestamp, byte_data in decoded_data:
        decoder.action_process_data(byte_data)
        position_data = [timestamp]
        for device in decoder.vr_tracker_devices:
            position_data.extend(device['position'])
        position_data_list.append(position_data)

    position_data_array = np.array(position_data_list)
    return position_data_array

# if __name__ == "__main__":
#     # Path to the recorded data file
#     project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recordings'))
#     file_path = os.path.join(project_dir, "t2.txt")
#     recorded_data = read_recorded_data(file_path)

#     # Extract position data
#     position_data_array = extract_position_data(recorded_data)
#     print(position_data_array)
#     print(position_data_array.shape)

if __name__ == "__main__":
    from tracker_decoder import TrackerDecoder
    from tracker_encoder import TrackerEncoder

    # Example usage
    encoder = TrackerEncoder()
    encoder.vr_tracker_devices = [
        {
            'name': '2B9219E9',
            'device_class': 3,
            'battery': 1.0,
            'status': True,
            'is_tracked': True,
            'position': [0.9944025874137878, 3.8844308853149414, 3.5970592498779297],
            'rotation': [-0.8399912714958191, -0.5198175311088562, 0.13195396959781647, 0.08241691440343857]
        },
        {
            'name': 'CB171C57',
            'device_class': 3,
            'battery': 0.78,
            'status': True,
            'is_tracked': True,
            'position': [3.2700154781341553, 1.1561644077301025, -0.5717313885688782],
            'rotation': [0.1816345900297165, -0.6273574829101562, -0.1807340532541275, -0.7353684306144714]
        },
        {
            'name': '4CDFCB8B',
            'device_class': 3,
            'battery': 0.7,
            'status': True,
            'is_tracked': True,
            'position': [0.053106654435396194, 0.7329368591308594, 0.061471227556467056],
            'rotation': [-0.5108284950256348, -0.543066143989563, -0.43412545323371887, 0.5056366324424744]
        }
    ]
    encoded_data = encoder.action_process_data()
    # add timestamp before the encoded data and save it to a binary file
    encoded_data_1 = struct.pack('<f', time.time()) + encoded_data
    project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recordings'))
    file_path = os.path.join(project_dir, "encoder.txt")

    print('\nencoded_data:', encoded_data)

    # create binary string with timestamp the data, new line and again
    encoded_data_2 = encoded_data_1 + b'\n' + encoded_data_1 + b'\n'
    print('\nencoded_data_2:', encoded_data_2)

    with open(file_path, 'wb') as file:
        file.write(encoded_data_2)

    decoder = TrackerDecoder()
    decoder.action_process_data(encoded_data)
    print('\ndecoded_data:', decoder.vr_tracker_devices)

    assert encoder.vr_tracker_devices == decoder.vr_tracker_devices
    print('\nTest passed!')

    encoded_data_string = b'\xae\x08\x072B9219E9\x03d\x01\x01\xeb\x00&?n\x9f{@RQo@\xb91W\xbf\xc9\xc0\x07\xbf\xcdT\xc1=xZj=8992BF03\x03T\x00\x005*M\xc0 B\x05>\n\xbaC\xc0\xc7\x1bq\xbe\xf6Pw\xbf\x1bH\x1d=\xde\x7f\xca=4CDFCB8B\x032\x01\x01=\\\x06\xbf\xc0^\xe1?\x01\xde\xae\xbeu\rD\xbfS\x83\x89=\xe2\xc9\xbf=N\xf4!?3AD07E7B\x04\x00\x01\x01\x99\xd6w@>\xbbl@Dj!\xbf\xe0\xb3{>\xe6\x18%\xbf\x1e\x800>@\xec3?292B164A\x04\x00\x01\x01\xc0\xe4m\xc0X\\s@\xcf\xbe\xc7>\x00)\x80\xbe\x1dH$\xbf\x1d4\x99>l\t)\xbf26D688D6\x04\x00\x01\x01\xefI\xec\xbd\x9c\x02v@\xf4\xe9m@{\xf6\xa3\xbc\xd5\xadq\xbf/m\xa7>9^\x1a\xbd1FA80E86\x04\x00\x01\x01\xd8\xb3R\xbc Gt@\xef\tp\xc0\xe0\xe1\xb7>\xb2\x07-={\t\xee\xbb\x02\xabn?'
    decoder = TrackerDecoder()
    decoder.action_process_data(encoded_data_string)
    decoded_data = decoder.vr_tracker_devices
    print('\ndecoded_data:', decoded_data)