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