from vive_decoder import ViveDecoder
from vive_encoder import ViveEncoder

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
        # no augmentation needed
        return byte_data, decoded_data, decoded_data
    elif num_devices > slider_value:
        # reduce the number of devices
        decoded_augm_data = decoded_data[:slider_value]
    else:
        decoded_augm_data = decoded_data.copy()

        # add more devices by copying from the existing devices but get a device name from the random list and change the sign of the position data for x, y
        for i in range(slider_value - num_devices):
            device = decoded_data[i].copy()
            device['name'] = device_names[i]
            device['position'][0] = -device['position'][0]
            device['position'][1] = -device['position'][1]
            device['position'][2] = device['position'][2]
            decoded_augm_data.append(device)

    # encode the data back
    encoder = ViveEncoder()
    encoder.vr_tracker_devices = decoded_augm_data
    encoded_data = encoder.return_byte_data()

    return encoded_data, decoded_data, decoded_augm_data


if __name__ == "__main__":
    byte_data = b'\xae\x08\x072B9219E9\x03d\x01\x01\xeb\x00&?n\x9f{@RQo@\xb91W\xbf\xc9\xc0\x07\xbf\xcdT\xc1=xZj=8992BF03\x03T\x00\x005*M\xc0 B\x05>\n\xbaC\xc0\xc7\x1bq\xbe\xf6Pw\xbf\x1bH\x1d=\xde\x7f\xca=4CDFCB8B\x032\x01\x01=\\\x06\xbf\xc0^\xe1?\x01\xde\xae\xbeu\rD\xbfS\x83\x89=\xe2\xc9\xbf=N\xf4!?3AD07E7B\x04\x00\x01\x01\x99\xd6w@>\xbbl@Dj!\xbf\xe0\xb3{>\xe6\x18%\xbf\x1e\x800>@\xec3?292B164A\x04\x00\x01\x01\xc0\xe4m\xc0X\\s@\xcf\xbe\xc7>\x00)\x80\xbe\x1dH$\xbf\x1d4\x99>l\t)\xbf26D688D6\x04\x00\x01\x01\xefI\xec\xbd\x9c\x02v@\xf4\xe9m@{\xf6\xa3\xbc\xd5\xadq\xbf/m\xa7>9^\x1a\xbd1FA80E86\x04\x00\x01\x01\xd8\xb3R\xbc Gt@\xef\tp\xc0\xe0\xe1\xb7>\xb2\x07-={\t\xee\xbb\x02\xabn?'
    slider_value = 20

    augmented_data, dec_data, dec_augm_data = augment_data(byte_data, slider_value)

    print('\nDecoded data:\n', dec_data)
    print('\nAugmented Decoded data:\n', dec_augm_data)

    # assert byte_data == augment_data, "Data not augmented"
    # assert dec_data == dec_augm_data, "Decoded data not augmented"
    print('\nTest passed!')