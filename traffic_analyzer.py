import cv2
from ultralytics import YOLO

model = YOLO(r"runs\detect\train\weights\best.pt")

def analyze_traffic(video_path, frame_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"status": "error", "message": "Could not read video frame."}

    print(f"[DEBUG] Frame shape: {frame.shape}")
    cv2.imwrite(frame_path, frame)

    results = model.predict(frame_path, conf=0.25)
    boxes = results[0].boxes

    vehicle_count = len(boxes)
    print(f"[DEBUG] Detected vehicles: {vehicle_count}")

    if vehicle_count == 0:
        level = "Unknown"
        emoji = "⚪"
    elif vehicle_count < 5:
        level = "Low"
        emoji = "🟢"
    elif vehicle_count < 15:
        level = "Medium"
        emoji = "🟡"
    else:
        level = "High"
        emoji = "🔴"

    return {
        "vehicles": vehicle_count,
        "congestion": f"{emoji} Traffic Level: {level} ({vehicle_count} vehicles)"
    }
