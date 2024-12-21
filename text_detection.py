import cv2
import numpy as np
from mediapipe.python.solutions.holistic import Holistic
from moviepy import VideoFileClip
import pytesseract

# Cargar el video
cap = cv2.VideoCapture('cropped_video.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convertir a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplicar filtro de suavizado
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detectar bordes
    edges = cv2.Canny(gray, 100, 200)
    
    # Detectar texto (OCR)
    text = pytesseract.image_to_string(edges)
    
    print(text)

cap.release()
cv2.destroyAllWindows()
