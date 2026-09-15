import cv2
import time
import RPi.GPIO as GPIO
from picamera2 import Picamera2

# ==========================================
# SERVO PIN
# ==========================================

SERVO_PIN = 18       # Physical Pin 12

# ==========================================
# SERVO SETUP
# ==========================================

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo = GPIO.PWM(SERVO_PIN, 50)   # 50 Hz
servo.start(0)


def servo_angle(angle):
    duty = 2.5 + (angle / 18.0)

    servo.ChangeDutyCycle(duty)
    time.sleep(0.4)

    # Stop signal after moving
    servo.ChangeDutyCycle(0)


# ==========================================
# BARRIER POSITIONS
# ==========================================

CLOSED = 0
OPEN = 90

# Start closed
servo_angle(CLOSED)


# ==========================================
# FACE DETECTION
# ==========================================

face_cascade = cv2.CascadeClassifier(
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
)


# ==========================================
# CAMERA SETUP
# ==========================================

picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)

picam2.configure(config)

picam2.start()

time.sleep(2)


print("================================")
print("Face Barrier System Started")
print("Camera is running...")
print("Press Q to stop")
print("================================")


barrier_open = False


# ==========================================
# MAIN LOOP
# ==========================================

try:

    while True:

        # Get REAL live camera frame
        frame = picam2.capture_array()

        # Convert camera image to grayscale
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

            print("Face detected → Barrier OPEN")

            # Draw rectangle around detected face
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
                "FACE DETECTED - OPEN",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            if not barrier_open:

                servo_angle(OPEN)
                barrier_open = True


        # ==================================
        # NO FACE
        # ==================================

        else:

            print("No face → Barrier CLOSED")

            cv2.putText(
                frame,
                "NO FACE - CLOSED",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

            if barrier_open:

                servo_angle(CLOSED)
                barrier_open = False


        # Show live camera
        cv2.imshow("Face Barrier Camera", frame)


        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


        # Small delay
        time.sleep(0.05)


# ==========================================
# STOP
# ==========================================

except KeyboardInterrupt:

    print("Program stopped")


finally:

    servo_angle(CLOSED)

    servo.stop()

    GPIO.cleanup()

    picam2.stop()

    cv2.destroyAllWindows()

    print("System safely stopped")