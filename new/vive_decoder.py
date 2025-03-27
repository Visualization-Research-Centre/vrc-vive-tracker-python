import time
import struct
from threading import Lock

class ViveDecoder:
    def __init__(self):
        self.ignore_tracking_reference = True
        self.vr_tracker_devices = []
        self.ignored_vive_tracker_names = []
        self.label = 2222
        self.current_timestamp = 0
        self._initialised = 0

    def add_ignore_vive_tracker_name(self, input_tracker_name):
        input_tracker_name_lower = input_tracker_name.lower()
        if input_tracker_name_lower not in self.ignored_vive_tracker_names:
            self.ignored_vive_tracker_names.append(input_tracker_name_lower)

    def parse_byte_data(self, byte_data):
        if len(byte_data) <= 2:
            return

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

        return self.vr_tracker_devices