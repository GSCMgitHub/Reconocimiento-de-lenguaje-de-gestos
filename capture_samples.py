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

def capture_samples(margin_frame=1, min_cant_frames=5, delay_frames=0, show_video = False):
    '''
    ### CAPTURA DE MUESTRAS PARA UNA PALABRA
    Recibe como parámetro la ubicación de guardado y guarda los frames
    `path` ruta de la carpeta de la palabra \n
    `margin_frame` cantidad de frames que se ignoran al comienzo y al final \n
    `min_cant_frames` cantidad de frames minimos para cada muestra \n
    `delay_frames` cantidad de frames que espera antes de detener la captura después de no detectar manos
    '''

    if not os.path.exists(VIDEO_FILE_INPUT_PATH): #Si no existe el directorio (carpeta de entrada/donde pones los videos), crea uno.
        os.makedirs(VIDEO_FILE_INPUT_PATH)
        print('\nEl directorio donde se encuentran los videos a capturar no existe,')
        print('se ha creado el directorio, pero necesita contener los archivos requeridos.')

        print('\nRecomiendo verificar que no hayan otros directorios faltantes con helpers.py:')
        print('ejecuta el script para verificar que no falten directorios, o crearlos en caso contrario.\n')

    else:
        if os.listdir(VIDEO_FILE_INPUT_PATH): #Si hay archivos...
            while os.path.exists(get_first_file_os(VIDEO_FILE_INPUT_PATH)): #esto se ejecuta hasta que no hayan archivos en "video_file_input"

                video = get_first_file_os(VIDEO_FILE_INPUT_PATH) #Paso 1: Toma 1er video de VIDEO_FILE_INPUT
                print("VIDEO DE ENTRADA ENCONTRADO")
            
                primera_vez = True
                frames = []

                with Holistic() as holistic_model:

                    clip = VideoFileClip(video) # [inicio] Paso 2: Toma los primeros 4 segundos del video 
                    print("VIDEO ESTABLECIDO")  # y lo graba como clip.mp4

                    start_time = 0
                    end_time = 4
                    subclip = clip.subclipped(start_time, end_time)
                    subclip.write_videofile("clip.mp4", codec="libx264") #Nota: SE CREA O SE SOBREESCRIBE
                    print("CLIP CREADO/ARCHIVO SOBREESCRITO") #Paso 2 [fin]

                    print("INICIO DE CAPTURA...")
                    cap = cv2.VideoCapture("clip.mp4")  # Paso 3: Abre clip.mp4
                    primera_vez = True
                    while cap.isOpened():  
                        ret, frame = cap.read() #Paso 4: recorre los fotogramas/frames del clip

                        if primera_vez: #Paso 4.1 > Si es la primera vez:

                            print("Dimensiones de la imágen: ", frame.shape) #Nota: útil para debug

                            #El frame es cortado: solo muestra la palabra representada:
                            crop = frame[800:970, 950:1700] 
                            #Convertir a escala de grises (hace más fácil detectar texto):
                            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                            #Detectar bordes (hace más fácil detectar texto):
                            edges = cv2.Canny(crop, 100, 200)
                            


                            #Ruta del Tesseract establecida 
                            #(INSTALLA TESSERACT Y BUSCA LA RUTA EN TU DISPOSITIVO, Y PEGALA AQUÍ)
                            pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Sebastian.LAPTOP-2A45H7C3\AppData\Local\Programs\Tesseract-OCR\tesseract.exe' 




                            #Convierte el texto detectado en la imágen a string:
                            raw_word_name = pytesseract.image_to_string(edges) 
                            #Lo convierte en minúscula:
                            raw_word_name = raw_word_name.lower() 
                            #Quita texto de relleno (en este caso se usa \n):
                            word_name = raw_word_name[:raw_word_name.find('\n')] 
                            print(word_name) 

                            word_path = os.path.join(ROOT_PATH, FRAME_ACTIONS_PATH, word_name)
                            create_folder(word_path) #Crea una carpeta con el nombre de la palabra

                            primera_vez = False


                        if not ret:  #Paso 4.2 > Si no hay más frames:

                            #print("FIN DE CAPTURA - INICIO DE PROCESAMIENTO")
                            if len(frames) >= min_cant_frames + margin_frame: 
                                #fix_frames += 1
                                #if fix_frames < delay_frames:
                                #    recording = True
                                #    continue
                                frames = frames[: - (margin_frame + delay_frames)] 
                                today = datetime.now().strftime('%y%m%d%H%M%S%f')
                                output_folder = os.path.join(word_path, f"sample_{today}")
                                create_folder(output_folder) #Paso 4.2.3: crea carpeta de muestras, con la fecha en su nombre
                                save_frames(frames, output_folder) #Paso 4.2.4: guarda los frames dentro de esa carpeta
 
                            #print("CAPTURA PROCESADA CON ÉXITO")

                            clip.close()  #Paso 4.2.5:
                            cap.release() #Cerrar el archivo y la captura
                            

                            continue

                        frames.append(np.asarray(frame))
                        
                        if(show_video): #Paso opcional: Mostrar la captura en una ventana aparte
                            image = frame.copy()
                            cv2.putText(image, 'Capturando...', FONT_POS, FONT, FONT_SIZE, (255, 50, 0))
                            results = mediapipe_detection(frame, holistic_model)                 
                            draw_keypoints(image, results)
                            cv2.imshow(f'Toma de muestras para "{os.path.basename(word_path)}"', image)

                        if cv2.waitKey(10) & 0xFF == ord('q'):
                            break

                    if (show_video): 
                        cv2.destroyAllWindows()

                    #Paso 5: Elimina el primer archivo de video_file_input que encontró (para seguir con el siguiente).
                    os.remove(get_first_file_os(VIDEO_FILE_INPUT_PATH)) 
        else:
            print('\nEl directorio (VIDEO_FILE_INPUT_PATH) está vacío. No hay nada que capturar.')
            print('Pon archivos en el directorio manualmente, o extraelos del sitio web (webscrap_samples.py).\n')

if __name__ == "__main__": 
    capture_samples()