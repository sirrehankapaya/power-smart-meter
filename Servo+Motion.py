import RPi.GPIO as GPIO
import time
from smbus2 import SMBus

# ==========================================
# PIN CONFIGURATION
# ==========================================

PIR_PIN = 27       # Physical Pin 13
SERVO_PIN = 18     # Physical Pin 12

# ==========================================
# LCD CONFIGURATION
# ==========================================

LCD_ADDR = 0x27    # Change to 0x3F if required

bus = SMBus(1)

LCD_CHR = 1
LCD_CMD = 0

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

ENABLE = 0b00000100
BACKLIGHT = 0b00001000


# ==========================================
# LCD FUNCTIONS
# ==========================================

def lcd_toggle_enable(bits):
    time.sleep(0.0005)

    bus.write_byte(LCD_ADDR, bits | ENABLE)

    time.sleep(0.0005)

    bus.write_byte(LCD_ADDR, bits & ~ENABLE)

    time.sleep(0.0005)


def lcd_byte(bits, mode):

    high = mode | (bits & 0xF0) | BACKLIGHT
    low = mode | ((bits << 4) & 0xF0) | BACKLIGHT

    bus.write_byte(LCD_ADDR, high)
    lcd_toggle_enable(high)

    bus.write_byte(LCD_ADDR, low)
    lcd_toggle_enable(low)


def lcd_init():

    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)

    time.sleep(0.005)


def lcd_string(message, line):

    message = message.ljust(16)

    lcd_byte(line, LCD_CMD)

    for character in message:
        lcd_byte(ord(character), LCD_CHR)


# ==========================================
# GPIO SETUP
# ==========================================

GPIO.setmode(GPIO.BCM)

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(SERVO_PIN, GPIO.OUT)


# ==========================================
# SERVO SETUP
# ==========================================

servo = GPIO.PWM(SERVO_PIN, 50)
servo.start(0)


def servo_angle(angle):

    duty = 2.5 + (angle / 18.0)

    servo.ChangeDutyCycle(duty)

    time.sleep(0.5)

    servo.ChangeDutyCycle(0)


# ==========================================
# BARRIER POSITIONS
# ==========================================

CLOSED = 0
OPEN = 90


# ==========================================
# INITIALIZE
# ==========================================

lcd_init()

print("Starting barrier system...")

lcd_string("Barrier System", LCD_LINE_1)
lcd_string("Starting...", LCD_LINE_2)

servo_angle(CLOSED)

time.sleep(2)


# ==========================================
# MAIN LOOP
# ==========================================

try:

    while True:

        # Read ACTUAL PIR sensor
        motion = GPIO.input(PIR_PIN)

        # --------------------------------------
        # MOTION DETECTED
        # --------------------------------------

        if motion == GPIO.HIGH:

            print("Motion: DETECTED")
            print("Barrier: OPEN")

            lcd_string("Motion: DETECTED", LCD_LINE_1)
            lcd_string("Barrier: OPEN", LCD_LINE_2)

            servo_angle(OPEN)

            # Keep checking the REAL PIR
            while GPIO.input(PIR_PIN) == GPIO.HIGH:
                time.sleep(0.1)

            # ----------------------------------
            # MOTION STOPPED
            # ----------------------------------

            print("Motion: NONE")
            print("Barrier: CLOSED")

            lcd_string("Motion: NONE", LCD_LINE_1)
            lcd_string("Barrier: CLOSED", LCD_LINE_2)

            servo_angle(CLOSED)

        else:

            print("Motion: NONE")
            print("Barrier: CLOSED")

            lcd_string("Motion: NONE", LCD_LINE_1)
            lcd_string("Barrier: CLOSED", LCD_LINE_2)

            time.sleep(0.2)


except KeyboardInterrupt:

    print("Program stopped")


finally:

    servo.stop()
    GPIO.cleanup()
    bus.close()