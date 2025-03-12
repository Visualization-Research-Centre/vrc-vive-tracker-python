import unittest
from FMRemoteTrackerDecoder import FMRemoteTrackerDecoder

class TestFMRemoteTrackerDecoder(unittest.TestCase):
    def setUp(self):
        self.decoder = FMRemoteTrackerDecoder()

    # ignore_tracking_reference
    def test_ignore_tracking_reference_default(self):
        self.assertTrue(self.decoder.ignore_tracking_reference)

    def test_ignore_tracking_reference_setter(self):
        self.decoder.ignore_tracking_reference = 0
        self.assertFalse(self.decoder.ignore_tracking_reference)
        self.decoder.ignore_tracking_reference = 1
        self.assertTrue(self.decoder.ignore_tracking_reference)
        self.decoder.ignore_tracking_reference = 2
        self.assertTrue(self.decoder.ignore_tracking_reference)
    
    # vr_tracker_devices
    # def test_vr_tracker_devices_default(self):
    #     self.assertEqual(self.decoder.vr_tracker_devices, [])

    # _ignored_vive_tracker_names
    # def test_ignored_vive_tracker_names_default(self):
    #     self.assertEqual(self.decoder.ignored_vive_tracker_names, [])

    # _initialised
    def test_initialised_default(self):
        self.assertEqual(self.decoder._initialised, 0)

    def test_initialised_setter(self):
        self.decoder.initialised = 0
        self.assertFalse(self.decoder._initialised)
        self.decoder.initialised = 1
        self.assertTrue(self.decoder._initialised)
        self.decoder.initialised = 2
        self.assertTrue(self.decoder._initialised)
        
    # initialised_lock
    def test_initialised_lock_default(self):
        self.assertIsNotNone(self.decoder.initialised_lock)




if __name__ == '__main__':
    unittest.main()