import time
from threading import Lock

class FMRemoteTrackerDecoder:
    def __init__(self):
        self.ignore_tracking_reference = True
        self.offset_local_angle = [0, 0, 0]
        self.offset_global_position = [0, 0, 0]
        self.offset_global_angle = [0, 0, 0]
        self.vr_tracker_devices = []
        self.tracker_visualisers = []
        self.ignored_vive_tracker_names = []
        self.prefab_visualisers = []
        self.detected_visualisers = []
        self.on_register_tracker_event = []  # Placeholder for UnityEvent
        self.label = 2222
        self.show_log = True
        self.prefab_index = 0
        self.current_timestamp = 0
        self._initialised = 0
        self.initialised_lock = Lock()

    @property
    def ignore_tracking_reference(self):
        return self._ignore_tracking_reference

    @ignore_tracking_reference.setter
    def ignore_tracking_reference(self, value):
        self._ignore_tracking_reference = value

    def set_offset_local_angle(self, input_value):
        self.offset_local_angle = input_value

    def set_offset_global_position(self, input_value):
        self.offset_global_position = input_value

    def set_offset_global_angle(self, input_value):
        self.offset_global_angle = input_value

    def update_all_visualisers_offsets(self):
        for visualiser in self.tracker_visualisers:
            visualiser.set_offset_global_position(self.offset_global_position)
            visualiser.set_offset_local_angle(self.offset_local_angle)
            visualiser.set_offset_global_angle(self.offset_global_angle)

    @property
    def vr_tracker_devices_raw(self):
        return self.vr_tracker_devices

    @property
    def vr_tracker_devices(self):
        return [device for device in self.vr_tracker_devices if device.name.lower() not in self.ignored_vive_tracker_names]

    @property
    def tracker_visualisers(self):
        return self.tracker_visualisers

    @property
    def ignored_vive_tracker_names(self):
        return self._ignored_vive_tracker_names

    @ignored_vive_tracker_names.setter
    def ignored_vive_tracker_names(self, value):
        self._ignored_vive_tracker_names = [name.lower() for name in value]

    def action_add_ignore_vive_tracker_name(self, input_tracker_name):
        if input_tracker_name.lower() not in self.ignored_vive_tracker_names:
            self.ignored_vive_tracker_names.append(input_tracker_name.lower())

    def action_remove_all_offset(self):
        self.offset_local_angle = [0, 0, 0]
        self.offset_global_position = [0, 0, 0]
        self.offset_global_angle = [0, 0, 0]

    def action_register_fm_remote_tracker_visualiser(self, input_fm_remote_tracker_visualiser):
        input_fm_remote_tracker_visualiser.set_offset_local_angle(self.offset_local_angle)
        input_fm_remote_tracker_visualiser.set_offset_global_position(self.offset_global_position)
        input_fm_remote_tracker_visualiser.set_offset_global_angle(self.offset_global_angle)

        if input_fm_remote_tracker_visualiser not in self.tracker_visualisers:
            self.tracker_visualisers.append(input_fm_remote_tracker_visualiser)

    def action_unregister_fm_remote_tracker_visualiser(self, input_fm_remote_tracker_visualiser):
        if input_fm_remote_tracker_visualiser in self.tracker_visualisers:
            self.tracker_visualisers.remove(input_fm_remote_tracker_visualiser)

    def action_process_data(self, byte_data):
        if not self.enabled:
            return
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
                    float.from_bytes(byte_data[index + 12:index + 16], 'little'),
                    float.from_bytes(byte_data[index + 16:index + 20], 'little'),
                    float.from_bytes(byte_data[index + 20:index + 24], 'little')
                ]

                rotation = [
                    float.from_bytes(byte_data[index + 24:index + 28], 'little'),
                    float.from_bytes(byte_data[index + 28:index + 32], 'little'),
                    float.from_bytes(byte_data[index + 32:index + 36], 'little'),
                    float.from_bytes(byte_data[index + 36:index + 40], 'little')
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
                        float.from_bytes(byte_data[index + 48:index + 52], 'little'),
                        float.from_bytes(byte_data[index + 52:index + 56], 'little')
                    ]
                    vr_tracker_device['r_axis1'] = [
                        float.from_bytes(byte_data[index + 56:index + 60], 'little'),
                        float.from_bytes(byte_data[index + 60:index + 64], 'little')
                    ]
                    vr_tracker_device['r_axis2'] = [
                        float.from_bytes(byte_data[index + 64:index + 68], 'little'),
                        float.from_bytes(byte_data[index + 68:index + 72], 'little')
                    ]
                    vr_tracker_device['r_axis3'] = [
                        float.from_bytes(byte_data[index + 72:index + 76], 'little'),
                        float.from_bytes(byte_data[index + 76:index + 80], 'little')
                    ]
                    vr_tracker_device['r_axis4'] = [
                        float.from_bytes(byte_data[index + 80:index + 84], 'little'),
                        float.from_bytes(byte_data[index + 84:index + 88], 'little')
                    ]
                    index += 88
                else:
                    index += 40

                for visualiser in self.tracker_visualisers:
                    if visualiser.tracker_name == vr_tracker_device['name']:
                        visualiser.action_process_data(vr_tracker_device)

                can_add_tracker_device = True
                if self.ignore_tracking_reference:
                    if vr_tracker_device['device_class'] == 4:  # TrackingReference
                        can_add_tracker_device = False

                if can_add_tracker_device:
                    vr_tracker_devices.append(vr_tracker_device)

        self.vr_tracker_devices = vr_tracker_devices

        if self.prefab_visualisers:
            if not self.prefab_visualisers:
                if self.show_log:
                    print("[FMETP] missing tracker prefab")
            else:
                while len(self.detected_visualisers) < len(self.vr_tracker_devices):
                    visualiser = self.prefab_visualisers[self.prefab_index]  # Placeholder for Instantiate
                    self.prefab_index += 1
                    if self.prefab_index >= len(self.prefab_visualisers):
                        self.prefab_index = 0

                    tracker_device = self.vr_tracker_devices[len(self.detected_visualisers)]
                    visualiser.name = "visualiser_" + tracker_device['name']
                    visualiser.active = True  # Placeholder for SetActive

                    visualiser.tracker_name = tracker_device['name']
                    visualiser.tracker_id = len(self.detected_visualisers)

                    self.detected_visualisers.append(visualiser)

                    self.on_register_tracker_event.append(tracker_device['name'])  # Placeholder for Invoke

                    if self.ignored_vive_tracker_names:
                        visualiser_name = tracker_device['name'].lower()
                        if visualiser_name in self.ignored_vive_tracker_names:
                            if self.show_log:
                                print("[FMETP] Ignore this tracker: " + visualiser_name)
                            visualiser.active = False  # Placeholder for SetActive

    @property
    def initialised(self):
        with self.initialised_lock:
            return self._initialised == 1

    @initialised.setter
    def initialised(self, value):
        with self.initialised_lock:
            self._initialised = 1 if value else 0

    def start_all(self):
        if self.initialised:
            return
        self.initialised = True

        if self.prefab_visualisers:
            for visualiser in self.prefab_visualisers:
                visualiser.active = False  # Placeholder for SetActive

        tracker_visualisers = []  # Placeholder for FindObjectsOfType
        if tracker_visualisers:
            for visualiser in tracker_visualisers:
                self.action_register_fm_remote_tracker_visualiser(visualiser)

    def stop_all(self):
        self.tracker_visualisers.clear()
        self.tracker_visualisers = []
        self.initialised = False

    def start(self):
        self.start_all()

    def on_enable(self):
        self.start_all()

    def on_disable(self):
        self.stop_all()