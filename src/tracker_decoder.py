import os
import time
import struct
from threading import Lock

class FMRemoteTrackerDecoder:
    def __init__(self):
        self.ignore_tracking_reference = True 
        self.vr_tracker_devices = []
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
        return self.vr_tracker_devices

    @property
    def vr_tracker_devices(self):
        return [device for device in self.vr_tracker_devices if device['name'].lower() not in self.ignored_vive_tracker_names]

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
            self._initialised = bool(value)

    def action_process_data(self, byte_data):
        if len(byte_data) <= 2:
            return

        # print how many bytes we have
        label = int.from_bytes(byte_data[:2], 'little')
        if label != self.label:
            return

        vr_tracker_devices_count = byte_data[2]
        vr_tracker_devices = []
        index = 3

        if vr_tracker_devices_count > 0:
            self.current_timestamp = time.time()
            for _ in range(vr_tracker_devices_count):
                tracker_name = byte_data[index:index+8].decode('utf-8')
                device_class = byte_data[index + 8]
                battery = byte_data[index + 9] / 100.0
                status = byte_data[index + 10] == 1
                is_tracked = byte_data[index + 11] == 1

                position = [
                    struct.unpack('<f', byte_data[index + 12:index + 16])[0],
                    struct.unpack('<f', byte_data[index + 16:index + 20])[0],
                    struct.unpack('<f', byte_data[index + 20:index + 24])[0]
                ]
                print(f"Position: {position}")
                rotation = [
                    struct.unpack('<f', byte_data[index + 24:index + 28])[0],
                    struct.unpack('<f', byte_data[index + 28:index + 32])[0],
                    struct.unpack('<f', byte_data[index + 32:index + 36])[0],
                    struct.unpack('<f', byte_data[index + 36:index + 40])[0]
                ]

                vr_tracker_device = {
                    'name': tracker_name,
                    'device_class': device_class,
                    'battery': battery,
                    'status': status,
                    'is_tracked': is_tracked,
                    'position': position,
                    'rotation': rotation
                }

                if device_class == 2:
                    vr_tracker_device['ul_button_pressed'] = int.from_bytes(byte_data[index + 40:index + 48], 'little')
                    vr_tracker_device['r_axis0'] = [
                        struct.unpack('<f', byte_data[index + 48:index + 52])[0],
                        struct.unpack('<f', byte_data[index + 52:index + 56])[0]
                    ]
                    vr_tracker_device['r_axis1'] = [
                        struct.unpack('<f', byte_data[index + 56:index + 60])[0],
                        struct.unpack('<f', byte_data[index + 60:index + 64])[0]
                    ]
                    vr_tracker_device['r_axis2'] = [
                        struct.unpack('<f', byte_data[index + 64:index + 68])[0],
                        struct.unpack('<f', byte_data[index + 68:index + 72])[0]
                    ]
                    vr_tracker_device['r_axis3'] = [
                        struct.unpack('<f', byte_data[index + 72:index + 76])[0],
                        struct.unpack('<f', byte_data[index + 76:index + 80])[0]
                    ]
                    vr_tracker_device['r_axis4'] = [
                        struct.unpack('<f', byte_data[index + 80:index + 84])[0],
                        struct.unpack('<f', byte_data[index + 84:index + 88])[0]
                    ]
                    index += 88
                else:
                    index += 40

                can_add_tracker_device = True
                if self.ignore_tracking_reference:
                    if vr_tracker_device['device_class'] == 4:  # TrackingReference
                        can_add_tracker_device = False

                if can_add_tracker_device:
                    vr_tracker_devices.append(vr_tracker_device)

        self.vr_tracker_devices = vr_tracker_devices

    def start_all(self):
        if self.initialised:
            return
        self.initialised = True

    def stop_all(self):
        self.initialised = False

    def start(self):
        self.start_all()

    def on_enable(self):
        self.start_all()

    def on_disable(self):
        self.stop_all()

    def read_recorded_data(self, file_path):
        recorded_data = []
        with open(file_path, 'r') as file:
            for line in file:
                timestamp_str, byte_data_str = line.strip().split(': ', 1)
                timestamp = float(timestamp_str)
                byte_data = eval(byte_data_str)  # Convert the byte string back to bytes
                recorded_data.append((timestamp, byte_data))
        return recorded_data

if __name__ == "__main__":
    decoder = FMRemoteTrackerDecoder()
    project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recordings'))
    file_path = project_dir + "/Untitled2.txt"
    recorded_data = decoder.read_recorded_data(file_path)
    for timestamp, byte_data in recorded_data:
        print(f"Timestamp: {timestamp}, Byte Data: {byte_data}")
    # decode the byte data
    for timestamp, byte_data in recorded_data:
        decoder.action_process_data(byte_data)
        print(f"Timestamp: {timestamp}, VR Tracker Devices: {decoder.vr_tracker_devices}")