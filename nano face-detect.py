import cv2
from picamera2 import Picamera2
import time

# Start the Raspberry Pi camera
picam2 = Picamera2()

config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)

picam2.configure(config)
picam2.start()

# Give the camera a moment to start
time.sleep(2)

# Load OpenCV's built-in face detector
face_cascade = cv2.CascadeClassifier(
    "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
)



print("Camera started...")
print("Looking for faces. Press Q to quit.")

last_detection = False

while True:
    # Capture image
    frame = picam2.capture_array()

    # Convert image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )

    if len(faces) > 0:
        if not last_detection:
            print("FACE DETECTED!")

        last_detection = True

        # Draw rectangle around each detected face
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
                "Face detected",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

    else:
        last_detection = False

    # Show camera image
    cv2.imshow("Raspberry Pi Face Detection", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

picam2.stop()
cv2.destroyAllWindows()

print("Program stopped.")
                                        