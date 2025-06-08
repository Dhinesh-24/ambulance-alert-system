import cv2
import os

video_path = "static/traffic.mp4"
frame_path = "static/frame_test.jpg"

cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()

if ret:
    os.makedirs("static", exist_ok=True)  # Ensure static folder exists
    cv2.imwrite(frame_path, frame)
    print(f"[✅] Saved frame to: {frame_path}")
else:
    print("[❌] Failed to read from video")

cap.release()
