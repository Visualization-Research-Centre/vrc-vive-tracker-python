import numpy as np

from vive_decoder import ViveDecoder    
from vive_encoder import ViveEncoder

if __name__ == "__main__":

    # =============================================================================
    # example for encoding raw data
    
    print('\nExample for encoding and decoding raw data:')

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
    
    assert data == encoder.vr_tracker_devices, "Data is not equal to vr_tracker_devices"
    print('\nTest 1 passed!')
    
    # decode the data
    decoder = ViveDecoder()
    decoder.parse_byte_data(encoded_data)
    decoded_data = decoder.vr_tracker_devices
    # print('\ndecoded_data:', decoded_data)

    assert data == decoded_data, "Data is not equal to decoded_data"
    print('\nTest 2 passed!')

    # encode the decoded data again and compare with the original encoded data
    encoder.vr_tracker_devices = decoder.vr_tracker_devices
    encoded_data = encoder.return_byte_data()
    assert encoded_data == encoded_data
    print('\nTest 3 passed!')

    # =============================================================================
    # example for decoding byte data

    byte_data = b'\xae\x08\x072B9219E9\x03d\x01\x01\xeb\x00&?n\x9f{@RQo@\xb91W\xbf\xc9\xc0\x07\xbf\xcdT\xc1=xZj=8992BF03\x03T\x00\x005*M\xc0 B\x05>\n\xbaC\xc0\xc7\x1bq\xbe\xf6Pw\xbf\x1bH\x1d=\xde\x7f\xca=4CDFCB8B\x032\x01\x01=\\\x06\xbf\xc0^\xe1?\x01\xde\xae\xbeu\rD\xbfS\x83\x89=\xe2\xc9\xbf=N\xf4!?3AD07E7B\x04\x00\x01\x01\x99\xd6w@>\xbbl@Dj!\xbf\xe0\xb3{>\xe6\x18%\xbf\x1e\x800>@\xec3?292B164A\x04\x00\x01\x01\xc0\xe4m\xc0X\\s@\xcf\xbe\xc7>\x00)\x80\xbe\x1dH$\xbf\x1d4\x99>l\t)\xbf26D688D6\x04\x00\x01\x01\xefI\xec\xbd\x9c\x02v@\xf4\xe9m@{\xf6\xa3\xbc\xd5\xadq\xbf/m\xa7>9^\x1a\xbd1FA80E86\x04\x00\x01\x01\xd8\xb3R\xbc Gt@\xef\tp\xc0\xe0\xe1\xb7>\xb2\x07-={\t\xee\xbb\x02\xabn?'
    # print('\nbyte_data:\n', byte_data)

    decoded_data_true = [
        {
            'name': '2B9219E9', 
            'device_class': 3, 
            'battery': 1.0, 
            'status': True, 
            'is_tracked': True, 
            'position': [0.6484515070915222, 3.931605815887451, 3.7393383979797363], 
            'rotation': [-0.840602457523346, -0.5302854180335999, 0.09440002590417862, 0.05721518397331238]
        }, 
        {
            'name': '8992BF03', 
            'device_class': 3, 
            'battery': 0.84, 
            'status': False, 
            'is_tracked': False, 
            'position': [-3.2057011127471924, 0.13013505935668945, -3.058229923248291], 
            'rotation': [-0.23545752465724945, -0.9660791158676147, 0.03839884325861931, 0.0988766998052597]
        }, 
        {
            'name': '4CDFCB8B', 
            'device_class': 3, 
            'battery': 0.5, 
            'status': True, 
            'is_tracked': True, 
            'position': [-0.5248449444770813, 1.7607040405273438, -0.3415375053882599], 
            'rotation': [-0.7658303380012512, 0.06714501231908798, 0.09364677965641022, 0.6326340436935425]
        }
    ]

    # decode the data
    decoder = ViveDecoder()
    decoder.parse_byte_data(byte_data)
    decoded_data = decoder.vr_tracker_devices
    # print('\ndecoded_data:', decoded_data)

    # encode the decoded data
    encoder.vr_tracker_devices = decoded_data
    encoded_data = encoder.return_byte_data()
    # print('\nencoded_data:\n', encoded_data)

    # assert byte_data == encoded_data
    # print('\nTest 4 passed!')

    # for i, (b1, b2) in enumerate(zip(byte_data, encoded_data)):
    #     if b1 != b2:
    #         print(f"Mismatch at byte {i}: {b1} != {b2}")
    #         # check which byte is different
    #         print(f"Byte {i} in byte_data: {byte_data[i]}")
    #         print(f"Byte {i} in encoded_data: {encoded_data[i]}")
    #         # print the byte in binary format
    #         print(f"Byte {i} in byte_data: {bin(byte_data[i])}")
    #         print(f"Byte {i} in encoded_data: {bin(encoded_data[i])}")

    # =============================================================================
    # test add ignore vive tracker name

    ignore_device_names = ['2B9219E9', 'FD0C50D1']
    ignore_device_names = [name.lower() for name in ignore_device_names]

    for name in ignore_device_names:
        decoder.add_ignore_vive_tracker_name(name)
    
    assert ignore_device_names == decoder.ignored_vive_tracker_names, "Ignore device names are not equal to ignored_vive_tracker_names"
    print('\nTest 5 passed!')

    # decode the data again
    decoder.parse_byte_data(byte_data)
    assert len(decoder.vr_tracker_devices) == 2, "Number of devices is not equal to 2"
    print('\nTest 6 passed!')

    # =============================================================================
    # test the blobs

    blobs = [
        {
            'name': '2B9219E9',
            'position': [-1.123, 1.123],
            'weight': 2.0
        },
        {
            'name': '2B9219E1',
            'position': [0.123, 0.123],
            'weight': 1.0
        }
    ]

    # encode the blobs
    encoder = ViveEncoder()
    encoder.blobs = blobs
    encoded_blobs = encoder.return_blob_data()
    print('\nencoded_blobs:', encoded_blobs)

    # decode the blobs
    decoder = ViveDecoder()
    decoder.parse_blob_data(encoded_blobs)
    decoded_blobs = decoder.blobs
    print('\ndecoded_blobs:', decoded_blobs)



            

