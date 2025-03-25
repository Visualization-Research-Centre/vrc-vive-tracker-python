import struct
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

    def action_process_data(self):
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