import gdown
import os
from ultralytics import YOLO
gdown.download("https://drive.google.com/uc?export=download&id=11pqvlzyayo1ttqDc73J2r8qT2EeSAXz5","best.pt",quiet=False)

#1
import gdown

model_path = "best.pt"
if not os.path.exists(model_path):
    gdown.download("https://drive.google.com/uc?export=download&id=11pqvlzyayo1ttqDc73J2r8qT2EeSAXz5", model_path, quiet=False)
#2
model = YOLO(model_path)