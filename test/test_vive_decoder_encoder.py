import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.vive_decoder import ViveDecoder    
from src.vive_encoder import ViveEncoder

if __name__ == "__main__":

    # =============================================================================
    # example for encoding raw data
    
    print('\nExample for encoding and decoding raw data:')

    vive_trackers = [
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
    encoder.vive_trackers = vive_trackers
    encoded_data = encoder.encode()
    
    assert vive_trackers == encoder.vive_trackers, "Data is not equal to vr_tracker_devices"
    print('\nTest 1 passed!')
    print(encoder.blobs)
    print(encoder.vive_trackers)
    # decode the data
    decoder = ViveDecoder()
    decoder.decode(encoded_data)
    decoded_data = decoder.vive_trackers
    print('\ndecoded_data:', decoded_data)

    assert vive_trackers == decoded_data, "Data is not equal to decoded_data"
    print('\nTest 2 passed!')

    # encode the decoded data again and compare with the original encoded data
    encoder.vive_trackers = decoded_data 
    assert encoded_data == encoder.encode()
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
    decoder.decode(byte_data)
    decoded_data = decoder.vive_trackers

    # encode the decoded data 2x
    encoder.vive_trackers = decoded_data
    encoded_data = encoder.encode()

    # decode again
    decoder.decode(encoded_data)
    decoded_data = decoder.vive_trackers

    encoder.vive_trackers = decoded_data
    encoded_data_2 = encoder.encode()

    assert encoded_data == encoded_data_2, "Encoded data is not equal to encoded_data_2"
    print('\nTest 4 passed!')

    # =============================================================================
    # test add ignore vive tracker name

    ignore_device_names = ['2B9219E9', 'FD0C50D1']

    decoder.ignored_vive_tracker_names = ignore_device_names
    assert ignore_device_names == decoder.ignored_vive_tracker_names, "Ignore device names are not equal to ignored_vive_tracker_names"
    print('\nTest 5 passed!')

    # decode the data again
    decoder.decode(byte_data)
    assert len(decoder.vive_trackers) == 2, "Number of devices is not equal to 2"
    print('\nTest 6 passed!')

    # =============================================================================
    # test the blobs

    vive_trackers_w_blobs = [
        {
            'name': '2B9219E9', 
            'device_class': 3, 
            'status': True, 
            'is_tracked': True, 
            'position': [0.6484515070915222, 3.931605815887451, 3.7393383979797363], 
            'rotation': [-0.840602457523346, -0.5302854180335999, 0.09440002590417862, 0.05721518397331238],
            'blob_id': 0.0
        }, 
        {
            'name': '8992BF03', 
            'device_class': 3, 
            'status': False, 
            'is_tracked': False, 
            'position': [-3.2057011127471924, 0.13013505935668945, -3.058229923248291], 
            'rotation': [-0.23545752465724945, -0.9660791158676147, 0.03839884325861931, 0.0988766998052597],
            'blob_id': 1.0
        }, 
        {
            'name': '4CDFCB8B', 
            'device_class': 3, 
            'status': True, 
            'is_tracked': True, 
            'position': [-0.5248449444770813, 1.7607040405273438, -0.3415375053882599], 
            'rotation': [-0.7658303380012512, 0.06714501231908798, 0.09364677965641022, 0.6326340436935425],
            'blob_id': 2.0
        }
    ]

    blobs = [
        {
            'position': [-1.1230000257492065, 1.1230000257492065],
            'weight': 2.0
        },
        {
            'position': [0.12300000339746475, 0.12300000339746475],
            'weight': 1.0
        },
        {
            'position': [1.1230000257492065, 1.1230000257492065],
            'weight': 3.0
        }
    ]

    # encode the blobs
    encoder = ViveEncoder()
    encoder.blobs = blobs
    encoded_data = encoder.encode()

    # decode the blobs
    decoder = ViveDecoder()
    decoder.decode(encoded_data)
    decoded_trackers = decoder.vive_trackers
    decoded_blobs = decoder.blobs

    print('\ndecoded_blobs:\n', decoded_blobs)
    assert decoded_trackers == [], "Decoded trackers are not equal to vive_trackers"
    assert decoded_blobs == blobs, "Decoded blobs are not equal to blobs"

    # add trackers and blobs
    encoder.vive_trackers = vive_trackers_w_blobs
    encoded_data = encoder.encode()

    decoder = ViveDecoder()
    decoder.decode(encoded_data)
    decoded_trackers = decoder.vive_trackers
    decoded_blobs = decoder.blobs

    # encode again
    encoder.vive_trackers = decoded_trackers
    encoder.blobs = decoded_blobs
    encoded_data = encoder.encode()

    # decode again
    decoder = ViveDecoder()
    decoder.decode(encoded_data)
    decoded_trackers_2 = decoder.vive_trackers
    decoded_blobs_2 = decoder.blobs

    print('\ndecoded_trackers:\n', decoded_trackers)
    print('\nvive_trackers_w_blobs:\n', decoded_trackers_2)
    assert decoded_trackers == decoded_blobs_2, "Decoded trackers are not equal to vive_trackers"
    print('\nTest 7 passed!')
    assert decoded_blobs == decoded_blobs_2, "Decoded blobs are not equal to blobs"
    print('\nTest 8 passed!')


            

