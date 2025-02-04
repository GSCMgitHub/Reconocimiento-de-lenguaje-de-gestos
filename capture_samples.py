import os
import cv2
import numpy as np
import pytesseract
from mediapipe.python.solutions.holistic import Holistic
from helpers import create_folder, draw_keypoints, mediapipe_detection, save_frames, there_hand
from constants import FONT, FONT_POS, FONT_SIZE, FRAME_ACTIONS_PATH, ROOT_PATH, VIDEO_FILE_INPUT_PATH
from datetime import datetime
from moviepy import VideoFileClip

def get_first_file_os(path):
    files = os.listdir(path)
    if files:
        return os.path.join(path, files[0])
    return None

def capture_samples(margin_frame=1, min_cant_frames=5, delay_frames=0):
    '''
    ### CAPTURA DE MUESTRAS PARA UNA PALABRA
    Recibe como parámetro la ubicación de guardado y guarda los frames
    `path` ruta de la carpeta de la palabra \n
    `margin_frame` cantidad de frames que se ignoran al comienzo y al final \n
    `min_cant_frames` cantidad de frames minimos para cada muestra \n
    `delay_frames` cantidad de frames que espera antes de detener la captura después de no detectar manos
    '''
    while os.path.exists(get_first_file_os(VIDEO_FILE_INPUT_PATH)): #esto se ejecuta mientras hasta que no hayan archivos en "video_file_input"

        video = get_first_file_os(VIDEO_FILE_INPUT_PATH) 
        print("VIDEO DE INPUT ENCONTRADO")
    
        primera_vez = True
        count_frame = 0
        frames = []
        fix_frames = 0
        recording = False

        with Holistic() as holistic_model:

            clip = VideoFileClip(video)
            print("VIDEO ESTABLECIDO")

            start_time = 0
            end_time = 4
            subclip = clip.subclipped(start_time, end_time)
            subclip.write_videofile("clip.mp4", codec="libx264") #SE CREA O SE SOBREESCRIBE
            print("CLIP CREADO/ARCHIVO SOBREESCRITO")

            print("INICIO DE CAPTURA...")
            cap = cv2.VideoCapture("clip.mp4") 
            primera_vez = True
            while cap.isOpened():
                ret, frame = cap.read()

                if primera_vez:
                    print("Dimensiones de la imágen: ", frame.shape) #útil para debug

                    #El frame es cortado: solo muestra la palabra representada
                    crop = frame[700:870, 950:1700] 

                    # Convertir a escala de grises (hace más fácil detectar texto)
                    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                    
                    # Detectar bordes (hace más fácil detectar texto)
                    edges = cv2.Canny(crop, 100, 200)
                    
                    #Ruta del Tesseract establecida
                    pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Sebas\AppData\Local\Programs\Tesseract-OCR\tesseract.exe' 



                    #Convierte el texto detectado en la imágen a string
                    raw_word_name = pytesseract.image_to_string(edges) 

                    #Lo convierte en minúscula
                    raw_word_name = raw_word_name.lower() 

                    #Quita texto de relleno (en este caso se usa \n)
                    word_name = raw_word_name[:raw_word_name.find('\n')] 
                    print(word_name) 

                    word_path = os.path.join(ROOT_PATH, FRAME_ACTIONS_PATH, word_name)
                    create_folder(word_path)

                    primera_vez = False


                if not ret:
                    print("FIN DE CAPTURA - INICIO DE PROCESAMIENTO")

                    if len(frames) >= min_cant_frames + margin_frame:
                        fix_frames += 1
                        if fix_frames < delay_frames:
                            recording = True
                            continue
                        frames = frames[: - (margin_frame + delay_frames)]
                        today = datetime.now().strftime('%y%m%d%H%M%S%f')
                        output_folder = os.path.join(word_path, f"sample_{today}")
                        create_folder(output_folder)
                        save_frames(frames, output_folder)

                    print("CAPTURA PROCESADA CON ÉXITO")

                    clip.close()
                    os.remove(video)

                    continue

                image = frame.copy()
                results = mediapipe_detection(frame, holistic_model)
                
                if there_hand(results) or recording:
                    recording = False
                    count_frame += 1
                    if count_frame > margin_frame:
                        cv2.putText(image, 'Capturando...', FONT_POS, FONT, FONT_SIZE, (255, 50, 0))
                        frames.append(np.asarray(frame))
                else:
                    if len(frames) >= min_cant_frames + margin_frame:
                        fix_frames += 1
                        if fix_frames < delay_frames:
                            recording = True
                            continue
                        frames = frames[: - (margin_frame + delay_frames)]
                        today = datetime.now().strftime('%y%m%d%H%M%S%f')
                        output_folder = os.path.join(word_path, f"sample_{today}")
                        create_folder(output_folder)
                        save_frames(frames, output_folder)
                    
                    recording, fix_frames = False, 0
                    frames, count_frame = [], 0
                    cv2.putText(image, 'Listo para capturar...', FONT_POS, FONT, FONT_SIZE, (0,220, 100))
                
                draw_keypoints(image, results)
                cv2.imshow(f'Toma de muestras para "{os.path.basename(word_path)}"', image)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

            cv2.destroyAllWindows()

if __name__ == "__main__": 
    capture_samples()