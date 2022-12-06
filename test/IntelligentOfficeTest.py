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

