import time
import board
import adafruit_dht
from smbus2 import SMBus

# =========================
# LCD SETTINGS
# =========================

LCD_ADDR = 0x27
bus = SMBus(1)

LCD_CHR = 1
LCD_CMD = 0

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

ENABLE = 0b00000100
BACKLIGHT = 0b00001000


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

    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# =========================
# DHT11 SETUP
# =========================

dht = adafruit_dht.DHT11(board.D17)


# =========================
# START LCD
# =========================

lcd_init()

lcd_string("DHT11 Sensor", LCD_LINE_1)
lcd_string("Starting...", LCD_LINE_2)

time.sleep(2)


# =========================
# MAIN LOOP
# =========================

try:
    while True:

        try:
            temperature = dht.temperature
            humidity = dht.humidity

            print("Temperature:", temperature, "C")
            print("Humidity:", humidity, "%")

            lcd_string("Temp: {} C".format(temperature), LCD_LINE_1)
            lcd_string("Humidity: {}%".format(humidity), LCD_LINE_2)

        except RuntimeError as e:
            # DHT11 occasionally gives a temporary reading error
            print("DHT11 reading error:", e)

        time.sleep(2)

except KeyboardInterrupt:
    print("Program stopped.")

finally:
    dht.exit()
    bus.close()