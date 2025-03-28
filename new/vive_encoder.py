import struct

class ViveEncoder:
    def __init__(self):
        self._vive_trackers = []
        self._ignored_vive_tracker_names = []
        self._blobs = []
        self.label = 2222

    def set_vive_trackers(self, vive_trackers):
        self._vive_trackers = vive_trackers or []

    def get_vive_trackers(self):
        return [
            device for device in self._vive_trackers
            if device['name'].lower() not in self._ignored_vive_tracker_names
        ]

    def set_ignored_vive_tracker_names(self, vive_tracker_names_list):
        self._ignored_vive_tracker_names = [name.lower() for name in vive_tracker_names_list]

    def add_ignored_vive_tracker_name(self, vive_tracker_name):
        name = vive_tracker_name.lower()
        if name not in self._ignored_vive_tracker_names:
            self._ignored_vive_tracker_names.append(name)

    def get_ignored_vive_trackers(self):
        return self._ignored_vive_tracker_names

    def set_blobs(self, blobs):
        self._blobs = blobs or []

    def get_blobs(self):
        return self._blobs
    
    def return_byte_data(self):
        # Create byte data
        byte_data = bytearray()
        
        # Add label
        byte_data.extend(self.label.to_bytes(2, 'little'))
        
        # Add number of devices
        byte_data.append(len(self._vive_trackers))

        # Add device data
        for device in self._vive_trackers:
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
        byte_data.append(len(self._blobs))

        # Add blob data
        for blob in self._blobs:
            byte_data.extend(blob['name'].encode('utf-8'))

            for pos in blob['position']:
                byte_data.extend(struct.pack('<f', pos))
            byte_data.extend(struct.pack('<f', blob['weight']))

        return bytes(byte_data)