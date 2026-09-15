import RPi.GPIO as GPIO
import time
from smbus2 import SMBus

# ==========================================
# PIN CONFIGURATION
# ==========================================

LDR_PIN = 22       # Physical Pin 15
RELAY_PIN = 23     # Physical Pin 16

# ==========================================
# LCD CONFIGURATION
# ==========================================

LCD_ADDR = 0x27    # Change to 0x3F if needed

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

    message = message[:16].ljust(16)

    lcd_byte(line, LCD_CMD)

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# ==========================================
# GPIO SETUP
# ==========================================

GPIO.setmode(GPIO.BCM)

GPIO.setup(LDR_PIN, GPIO.IN)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Start relay OFF
GPIO.output(RELAY_PIN, GPIO.LOW)


# ==========================================
# LCD START
# ==========================================

lcd_init()

lcd_string("Automatic Light", LCD_LINE_1)
lcd_string("Starting...", LCD_LINE_2)

time.sleep(2)


# ==========================================
# MAIN LOOP
# ==========================================

try:

    while True:

        # REAL LIVE LDR OUTPUT
        ldr = GPIO.input(LDR_PIN)

        # ==================================
        # DARK
        # ==================================

        if ldr == GPIO.HIGH:

            print("LDR: DARK")
            print("Relay: ON")

            GPIO.output(RELAY_PIN, GPIO.HIGH)

            lcd_string("Light: DARK", LCD_LINE_1)
            lcd_string("Relay: ON", LCD_LINE_2)


        # ==================================
        # BRIGHT
        # ==================================

        else:

            print("LDR: BRIGHT")
            print("Relay: OFF")

            GPIO.output(RELAY_PIN, GPIO.LOW)

            lcd_string("Light: BRIGHT", LCD_LINE_1)
            lcd_string("Relay: OFF", LCD_LINE_2)


        # Continuous live checking
        time.sleep(0.2)


except KeyboardInterrupt:

    print("Program stopped")


finally:

    GPIO.output(RELAY_PIN, GPIO.LOW)

    GPIO.cleanup()

    bus.close()