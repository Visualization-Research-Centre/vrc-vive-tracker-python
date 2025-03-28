import struct

class ViveEncoder:
    def __init__(self):
        self.vive_trackers = []
        self.blobs = []
        self.label = 2222
    
    def return_byte_data(self):
        # Create byte data
        byte_data = bytearray()
        
        # Add label
        byte_data.extend(self.label.to_bytes(2, 'little'))
        
        print('length of byte_data:', len(byte_data))
        # Add number of devices
        # num_devices = len(self.vive_trackers)
        # byte_data.extend(num_devices.to_bytes(1, 'little'))
        byte_data.append(len(self.vive_trackers))
        # print('length of byte_data:', len(byte_data))
        # print('byte_data:', byte_data)

        # Add device data
        for device in self.vive_trackers:
            byte_data.extend(device['name'].encode('utf-8'))
            byte_data.append(device['device_class'])
            byte_data.append(int(device['battery'] * 100))
            byte_data.append(1 if device['status'] else 0)
            byte_data.append(1 if device['is_tracked'] else 0)

            for pos in device['position']:
                byte_data.extend(struct.pack('<f', pos))
            for rot in device['rotation']:
                byte_data.extend(struct.pack('<f', rot))

            if device['device_class'] == 2:
                byte_data.extend(device['ul_button_pressed'].to_bytes(8, 'little'))
                for axis in range(5):
                    byte_data.extend(struct.pack('<f', device[f'r_axis{axis}'][0]))
                    byte_data.extend(struct.pack('<f', device[f'r_axis{axis}'][1]))

        # Add number of blobs
        byte_data.append(len(self.blobs))

        # Add blob data
        for blob in self.blobs:
            byte_data.extend(blob['name'].encode('utf-8'))

            for pos in blob['position']:
                byte_data.extend(struct.pack('<f', pos))
            byte_data.extend(struct.pack('<f', blob['weight']))

        return bytes(byte_data)