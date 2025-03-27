import struct

class ViveEncoder:
    def __init__(self):
        self._vr_tracker_devices = []
        self._ignored_vive_tracker_names = []
        self.label = 2222

    @property
    def vr_tracker_devices(self):
        return [
            device for device in self._vr_tracker_devices
            if device['name'].lower() not in self._ignored_vive_tracker_names
        ]

    @vr_tracker_devices.setter
    def vr_tracker_devices(self, value):
        self._vr_tracker_devices = value or []

    @property
    def ignored_vive_tracker_names(self):
        return self._ignored_vive_tracker_names

    @ignored_vive_tracker_names.setter
    def ignored_vive_tracker_names(self, value):
        self._ignored_vive_tracker_names = [name.lower() for name in value]

    def action_add_ignore_vive_tracker_name(self, input_tracker_name):
        name = input_tracker_name.lower()
        if name not in self._ignored_vive_tracker_names:
            self._ignored_vive_tracker_names.append(name)

    def return_byte_data(self):
        byte_data = bytearray()
        byte_data.extend(self.label.to_bytes(2, 'little'))
        byte_data.append(len(self._vr_tracker_devices))

        for device in self._vr_tracker_devices:
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

        return bytes(byte_data)