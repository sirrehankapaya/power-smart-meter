import cv2
import time
from picamera2 import Picamera2
from smbus2 import SMBus

# ==========================================
# LCD SETTINGS
# ==========================================

LCD_ADDR = 0x27

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

    for character in message:
        lcd_byte(ord(character), LCD_CHR)


# ==========================================
# FACE DETECTOR
# ==========================================

face_cascade = cv2.CascadeClassifier(
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
)

if face_cascade.empty():
    print("ERROR: Face detector could not be loaded.")
    exit()


# ==========================================
# CAMERA SETUP
# ==========================================

picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={
        "size": (640, 480),
        "format": "RGB888"
    }
)

picam2.configure(config)

picam2.start()

time.sleep(2)


# ==========================================
# LCD START
# ==========================================

lcd_init()

lcd_string("Attendance", LCD_LINE_1)
lcd_string("Starting...", LCD_LINE_2)

time.sleep(2)


print("Camera started")
print("Face detection started")
print("Press Q to stop")


# ==========================================
# MAIN LOOP
# ==========================================

try:

    while True:

        # REAL LIVE CAMERA FRAME
        frame = picam2.capture_array()

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Detect REAL faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )

        # ==================================
        # FACE DETECTED
        # ==================================

        if len(faces) > 0:

            print("Face detected - Attendance Marked")

            lcd_string("Attendance", LCD_LINE_1)
            lcd_string("Marked", LCD_LINE_2)

            # Draw rectangle around face
            for (x, y, w, h) in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            cv2.putText(
                frame,
                "ATTENDANCE MARKED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        # ==================================
        # NO FACE
        # ==================================

        else:

            print("No face detected")

            lcd_string("No Face", LCD_LINE_1)
            lcd_string("Detected", LCD_LINE_2)

            cv2.putText(
                frame,
                "NO FACE DETECTED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )


        # ==================================
        # SHOW LIVE CAMERA
        # ==================================

        cv2.imshow("Attendance Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# ==========================================
# STOP
# ==========================================

except KeyboardInterrupt:

    print("Program stopped")


finally:

    picam2.stop()

    cv2.destroyAllWindows()

    bus.close()

    print("Camera and LCD stopped")