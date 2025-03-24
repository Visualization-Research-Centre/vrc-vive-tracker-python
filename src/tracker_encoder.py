import os
import time
import struct
import numpy as np
from threading import Lock

class TrackerEncoder:
    def __init__(self):
        self._ignore_tracking_reference = True
        self._vr_tracker_devices = []
        self._ignored_vive_tracker_names = []
        self.label = 2222
        self.current_timestamp = 0
        self._initialised = 0
        self.initialised_lock = Lock()

    @property
    def ignore_tracking_reference(self):
        return self._ignore_tracking_reference

    @ignore_tracking_reference.setter
    def ignore_tracking_reference(self, value):
        self._ignore_tracking_reference = bool(value)

    @property
    def vr_tracker_devices_raw(self):
        return self._vr_tracker_devices

    @property
    def vr_tracker_devices(self):
        return [device for device in self._vr_tracker_devices if device['name'].lower() not in self.ignored_vive_tracker_names]

    @vr_tracker_devices.setter
    def vr_tracker_devices(self, value):
        if value is not None:
            self._vr_tracker_devices = value
        else:
            self._vr_tracker_devices = []

    @property
    def ignored_vive_tracker_names(self):
        return self._ignored_vive_tracker_names

    @ignored_vive_tracker_names.setter
    def ignored_vive_tracker_names(self, value):
        self._ignored_vive_tracker_names = [name.lower() for name in value]

    def action_add_ignore_vive_tracker_name(self, input_tracker_name):
        if input_tracker_name.lower() not in self.ignored_vive_tracker_names:
            self.ignored_vive_tracker_names.append(input_tracker_name.lower())

    @property
    def initialised(self):
        with self.initialised_lock:
            return self._initialised == 1

    @initialised.setter
    def initialised(self, value):
        with self.initialised_lock:
            self._initialised = 1 if value else 0

    def action_encode_data(self):
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

    def start_all(self):
        if self.initialised:
            return
        self.initialised = True

    def stop_all(self):
        self.initialised = False

if __name__ == "__main__":
    from tracker_decoder import TrackerDecoder

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
    encoded_data = encoder.action_encode_data()
    print('\nencoded_data:', encoded_data)

    decoder = TrackerDecoder()
    decoder.action_process_data(encoded_data)
    print('\ndecoded_data:', decoder.vr_tracker_devices)