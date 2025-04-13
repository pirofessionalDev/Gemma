import face_recognition
import cv2
import time

# Load known face
known_image = face_recognition.load_image_file("me.jpg")
known_encoding = face_recognition.face_encodings(known_image)[0]

# Start webcam
video_capture = cv2.VideoCapture(0)

print("[Thursday] Scanning will start in 5 seconds. Look at the camera...")

# Show preview for 5 seconds
start_time = time.time()
while time.time() - start_time < 5:
    ret, frame = video_capture.read()
    if not ret:
        continue
    cv2.putText(frame, "Hold still... Scanning soon!", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.imshow('Thursday | Get Ready', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Actual recognition frame
ret, frame = video_capture.read()
rgb_frame = frame[:, :, ::-1]

# Detect faces
face_locations = face_recognition.face_locations(rgb_frame)
if face_locations:
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        match = face_recognition.compare_faces([known_encoding], face_encoding)

        if match[0]:
            label = "You, sir 💯"
            color = (0, 255, 0)
        else:
            label = "Unknown 🕵️"
            color = (0, 0, 255)

        # Draw box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
else:
    print("[Thursday] No faces detected. Try again.")
    cv2.putText(frame, "No faces detected.", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

cv2.imshow('Thursday | Result', frame)
cv2.waitKey(0)

video_capture.release()
cv2.destroyAllWindows()
