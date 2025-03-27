import time
import struct
import numpy as np

from vive_decoder import ViveDecoder    
from vive_encoder import ViveEncoder

if __name__ == "__main__":

    # Example usage
    data = [
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

    # encode the data
    encoder = ViveEncoder()
    encoder.vr_tracker_devices = data
    encoded_data = encoder.return_byte_data()
    
    # add timestamp before the encoded data
    encoded_data_time = struct.pack('<f', time.time()) + encoded_data

    # save the encoded data to a file
    # project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recordings'))
    # file_path = os.path.join(project_dir, "encoder.txt")
    # # create binary string with timestamp the data, new line and again
    # encoded_data_2 = encoded_data_time + b'\n' + encoded_data_time + b'\n'
    # print('\nencoded_data_2:', encoded_data_2)
    # with open(file_path, 'wb') as file:
    #     file.write(encoded_data_2)

    # decode the data
    decoder = ViveDecoder()
    decoder.parse_byte_data(encoded_data)
    decoded_data = decoder.vr_tracker_devices
    print('\ndecoded_data:', decoded_data)

    assert encoder.vr_tracker_devices == decoded_data
    assert decoder.vr_tracker_devices == data
    print('\nTest passed!')

    # encode the decoded data again and compare with the original encoded data
    encoder.vr_tracker_devices = decoder.vr_tracker_devices
    encoded_data_2 = encoder.return_byte_data()
    assert encoded_data == encoded_data_2
    print('\nTest passed!')

    encoded_data_string = b'\xae\x08\x072B9219E9\x03d\x01\x01\xeb\x00&?n\x9f{@RQo@\xb91W\xbf\xc9\xc0\x07\xbf\xcdT\xc1=xZj=8992BF03\x03T\x00\x005*M\xc0 B\x05>\n\xbaC\xc0\xc7\x1bq\xbe\xf6Pw\xbf\x1bH\x1d=\xde\x7f\xca=4CDFCB8B\x032\x01\x01=\\\x06\xbf\xc0^\xe1?\x01\xde\xae\xbeu\rD\xbfS\x83\x89=\xe2\xc9\xbf=N\xf4!?3AD07E7B\x04\x00\x01\x01\x99\xd6w@>\xbbl@Dj!\xbf\xe0\xb3{>\xe6\x18%\xbf\x1e\x800>@\xec3?292B164A\x04\x00\x01\x01\xc0\xe4m\xc0X\\s@\xcf\xbe\xc7>\x00)\x80\xbe\x1dH$\xbf\x1d4\x99>l\t)\xbf26D688D6\x04\x00\x01\x01\xefI\xec\xbd\x9c\x02v@\xf4\xe9m@{\xf6\xa3\xbc\xd5\xadq\xbf/m\xa7>9^\x1a\xbd1FA80E86\x04\x00\x01\x01\xd8\xb3R\xbc Gt@\xef\tp\xc0\xe0\xe1\xb7>\xb2\x07-={\t\xee\xbb\x02\xabn?'
    decoder = ViveDecoder()
    decoder.parse_byte_data(encoded_data_string)
    decoded_data = decoder.vr_tracker_devices
    print('\ndecoded_data:', decoded_data)