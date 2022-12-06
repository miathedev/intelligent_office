import unittest
from unittest.mock import patch
import mock.GPIO as GPIO
from mock.RTC import RTC
from IntelligentOffice import IntelligentOffice
from IntelligentOfficeError import IntelligentOfficeError


class IntelligentOfficeTest(unittest.TestCase):
    def setUp(self):
        self.office = IntelligentOffice()
    """
    Define your test cases here
    """
    pass

    #######################
    #Task 1
    #######################
    @patch("mock.GPIO.input")
    def test_office_worker_detection_true(self, mock_input):
        mock_input.return_value = 1023
        for i in [11, 12, 13, 15]:
            presence = self.office.check_quadrant_occupancy(i)
            self.assertTrue(presence)

    @patch("mock.GPIO.input")
    def test_office_worker_detection_false(self, mock_input):
        mock_input.return_value = 0
        for i in [11, 12, 13, 15]:
            presence = self.office.check_quadrant_occupancy(i)
            self.assertFalse(presence)
    def test_office_worker_detection_throws_on_invalid_pin(self):
        self.assertRaises(IntelligentOfficeError, self.office.check_quadrant_occupancy, 1)

    #######################
    # Task 2
    #######################

    @patch.object(RTC, "get_current_time_string")
    @patch.object(RTC, "get_current_day")
    def test_blinds_manager_on_time_weekday(self, mock_rtc_day, mock_rtc_time):
        for (start_time, stop_time) in [("08:00:00", "20:00:00"), ("10:00:00", "22:00:00")]:
            for weekday in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                mock_rtc_day.return_value = weekday

                #Open
                mock_rtc_time.return_value = start_time

                self.office.manage_blinds_based_on_time()
                self.assertTrue(self.office.blinds_open)

                #Close
                mock_rtc_time.return_value = stop_time

                self.office.manage_blinds_based_on_time()
                self.assertFalse(self.office.blinds_open)

    @patch.object(RTC, "get_current_time_string")
    @patch.object(RTC, "get_current_day")
    def test_blinds_manager_on_time_weekend(self, mock_rtc_day, mock_rtc_time):
        for (start_time, stop_time) in [("08:00:00", "20:00:00"), ("10:00:00", "22:00:00")]:
            for weekday in ["SATURDAY", "SUNDAY"]:
                mock_rtc_day.return_value = weekday

                # Open
                mock_rtc_time.return_value = start_time

                self.office.manage_blinds_based_on_time()
                self.assertFalse(self.office.blinds_open)

                # Close
                mock_rtc_time.return_value = stop_time

                self.office.manage_blinds_based_on_time()
                self.assertFalse(self.office.blinds_open)

    #######################
    # Task 3
    #######################

    #Default off

    @patch("mock.GPIO.input")
    @patch("IntelligentOffice.IntelligentOffice.human_present")
    def test_office_light_management_bright_ambient(self, human_present, mock_input):
        human_present.return_value = True #Should be sufficent to keep test working for Task 4
        #KeepZone: 500 <= val <= 550
        mock_input.side_effect = [550, 500, #KeepZone, default off - is off
            449, #Too dark, light should be lit
            550,
            500,
            551, #Too bright, turn off light
        ]

        #KeepZone, Default light is off
        self.office.manage_light_level()
        self.assertFalse(self.office.light_on)

        #KeepZone
        self.office.manage_light_level()
        self.assertFalse(self.office.light_on)

        #If lux < 449 turn on light, dark ambient
        self.office.manage_light_level()
        self.assertTrue(self.office.light_on)  # Because its dark

        # KeepZone
        self.office.manage_light_level()
        self.assertTrue(self.office.light_on)
        self.office.manage_light_level()
        self.assertTrue(self.office.light_on)


        #Bright ambient
        self.office.manage_light_level()
        self.assertFalse(self.office.light_on)

    #######################
    # Task 4
    #######################

    # Default off

    @patch("mock.GPIO.input")
    @patch("IntelligentOffice.IntelligentOffice.human_present")
    def test_office_light_management_bright_ambient_human_detection(self, human_present, mock_input ):
        human_present.return_value = False  # Should be sufficent to keep test working for Task 4
        # KeepZone: 500 <= val <= 550
        mock_input.side_effect = [1, 1000,  # KeepZone, default off - is off
                                  1, 1000
                                 ]

        #No Human, no light
        self.office.manage_light_level()
        self.assertFalse(self.office.light_on)

        # No Human, no light, but its bright anyways
        self.office.manage_light_level()
        self.assertFalse(self.office.light_on)

        human_present.return_value = True

        # Human, light, its dark
        self.office.manage_light_level()
        self.assertTrue(self.office.light_on)

        # Human, no light, its bright
        self.office.manage_light_level()
        self.assertFalse(self.office.light_on)

    #######################
    # Task 4
    #######################
    @patch("mock.GPIO.input")
    def test_office_air_quality(self, mock_input):
        mock_input.side_effect = [10,#Clean air, no vent needed
                                  801, #Bad air dude!
                                  700,
                                  500,
                                  300, #Disable fan again
                                ]

        self.office.monitor_air_quality()
        self.assertFalse(self.office.fan_switch_on)

        for i in [1,2,3]:
            self.office.monitor_air_quality()
            self.assertTrue(self.office.fan_switch_on)

        self.office.monitor_air_quality()
        self.assertFalse(self.office.fan_switch_on)
