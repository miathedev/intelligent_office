import time

from IntelligentOfficeError import IntelligentOfficeError
import mock.GPIO as GPIO
from mock.RTC import RTC


class IntelligentOffice:
    # Pin number definition
    # Infrared Sensor.
    # 0V ----> Nothing detected
    # >0V ---> Something is present
    INFRARED_PIN_1 = 11
    INFRARED_PIN_2 = 12
    INFRARED_PIN_3 = 13
    INFRARED_PIN_4 = 15
    RTC_PIN = 16
    SERVO_PIN = 18
    PHOTO_PIN = 22  # photoresistor
    LED_PIN = 29
    CO2_PIN = 31
    FAN_PIN = 32

    LUX_MIN = 500
    LUX_MAX = 550

    SERVO_DUTY_CYCLE_BLINDS_OPEN = (180 / 18) + 2
    SERVO_DUTY_CYCLE_BLINDS_CLOSED = 0 + 2

    def __init__(self):
        """
        Constructor
        """
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.INFRARED_PIN_1, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN_2, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN_3, GPIO.IN)
        GPIO.setup(self.INFRARED_PIN_4, GPIO.IN)
        GPIO.setup(self.PHOTO_PIN, GPIO.IN)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        GPIO.setup(self.CO2_PIN, GPIO.IN)
        GPIO.setup(self.FAN_PIN, GPIO.OUT)

        self.rtc = RTC(self.RTC_PIN)
        self.pwm = GPIO.PWM(self.SERVO_PIN, 50)
        self.pwm.start(0)

        self.blinds_open = False
        self.light_on = False
        self.fan_switch_on = False

    def check_quadrant_occupancy(self, pin: int) -> bool:
        """
        Checks whether one of the infrared distance sensor on the ceiling detects something in front of it.
        :param pin: The data pin of the sensor that is being checked (e.g., INFRARED_PIN1).
        :return: True if the infrared sensor detects something, False otherwise.
        """
        if pin not in [11, 12, 13, 15]:
            raise IntelligentOfficeError("Invalid pin/quadrant")

        return GPIO.input(pin) > 0

    def human_present(self):
        for pin in [11,12,13,15]:
            if GPIO.input(pin):
                return True
        return False

    def set_blinds(self, do_open):
        if not self.blinds_open and do_open:
            self.blinds_open = True
            self.change_servo_angle(self.SERVO_DUTY_CYCLE_BLINDS_OPEN)
        if self.blinds_open and not do_open:
            self.blinds_open = False
            self.change_servo_angle(self.SERVO_DUTY_CYCLE_BLINDS_CLOSED)



    def manage_blinds_based_on_time(self) -> None:
        """
        Uses the RTC and servo motor to open/close the blinds based on current time and day.
        The system fully opens the blinds at 8:00 and fully closes them at 20:00
        each day except for Saturday and Sunday.
        """
        current_time = time.strptime(RTC.get_current_time_string(), '%H:%M:%S')
        weekday = RTC.get_current_day()

        if 8 <= current_time.tm_hour < 20 and weekday not in ["SATURDAY", "SUNDAY"]:
            self.set_blinds(True)
        else:
            self.set_blinds(False)


    def set_light(self, set_light):
        if set_light and not self.light_on:
            self.light_on = True
            GPIO.output(self.LED_PIN, True)
        elif not set_light and self.light_on:
            self.light_on = False
            GPIO.output(self.LED_PIN, False)

    def manage_light_level(self) -> None:
        """
        Tries to maintain the actual light level inside the office, measure by the photoresitor,
        between LUX_MIN and LUX_MAX.
        If the actual light level is lower than LUX_MIN the system turns on the smart light bulb.
        On the other hand, if the actual light level is greater than LUX_MAX, the system turns off the smart light bulb.

        Furthermore, When the last worker leaves the office (i.e., the office is now vacant), the intelligent office system 
        stops regulating the light level in the office and then turns off the smart light bulb. 
        When the first worker goes back into the office, the system resumes regulating the light level
        """

        #If no human detect, shut down regulation and disable light
        if not self.human_present():
            self.set_light(False)
            return

        lux = GPIO.input(self.PHOTO_PIN)
        if self.LUX_MIN <= lux <= self.LUX_MAX:
            print("Keep state")
            #Keep State
        else:
            if lux < self.LUX_MIN:
                self.set_light(True)
                print("Light ON")
            elif lux > self.LUX_MAX:
                print("Light OFF")
                self.set_light(False)



    def monitor_air_quality(self) -> None:
        """
        Use the carbon dioxide sensor to monitor the level of CO2 in the office.
        If the amount of detected CO2 is greater than or equal to 800 PPM, the system turns on the
        switch of the exhaust fan until the amount of CO2 is lower than 500 PPM.
        """
        air_ppm = GPIO.input(self.CO2_PIN)
        if air_ppm > 800 and not self.fan_switch_on:
            self.fan_switch_on = True

        if air_ppm < 500 and self.fan_switch_on:
            self.fan_switch_on = False
    def change_servo_angle(self, duty_cycle: float) -> None:
        """
        Changes the servo motor's angle by passing to it the corresponding PWM duty cycle signal
        :param duty_cycle: the length of the duty cycle
        """
        GPIO.output(self.SERVO_PIN, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(1)
        GPIO.output(self.SERVO_PIN, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)
