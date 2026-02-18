import json
import os
import cv2

import mediapipe.python as mp

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

FACEMESH_CONTOURS = mp_holistic.FACEMESH_CONTOURS
POSE_CONNECTIONS = mp_holistic.POSE_CONNECTIONS
HAND_CONNECTIONS = mp_holistic.HAND_CONNECTIONS

import numpy as np
import pandas as pd
from typing import NamedTuple
from constants import *

import sys

# GENERAL
def mediapipe_detection(image, model):
    '''
    ### DETECCIÓN DE KEYPOINTS CON MEDIAPIPE
    A partir de una imagen y un modelo de mediapipe, retorna los resultados de la detección de keypoints. \n
    La imagen se convierte a RGB y se marca como no escribible para mejorar el rendimiento. \n
    Se procesan los keypoints con el modelo de mediapipe y se retornan los resultados.
    '''
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    return results

def create_folder(path):
    '''
    ### CREAR CARPETA SI NO EXISTE
    Si ya existe, no hace nada.
    '''
    if not os.path.exists(path):
        os.makedirs(path)

def there_hand(results: NamedTuple) -> bool:
    '''
    #### "¿ACASO HAY MANO DETECTADA?"
    Retorna `True` si se detecta al menos una mano (izquierda o derecha), o `False` si no se detecta ninguna mano.
    '''
    return results.left_hand_landmarks or results.right_hand_landmarks

def get_word_ids(path):
    '''
    ### OBTENER IDS DE PALABRAS DESDE JSON
    Lee el archivo JSON y retorna la lista de ids de palabras.
    #### Estructura del JSON:
        {
            "words_ids": [
                "1-LETRA_A",
                "2-LETRA_B",
                ...
            ]
        }
    '''
    with open(path, 'r') as json_file:
        data = json.load(json_file)
        return data['words_ids']

# CAPTURE SAMPLES
def draw_keypoints(image, results):
    '''
    ### DIBUJAR KEYPOINTS EN LA IMAGEN
    Dibuja los keypoints de la cara, pose y manos en la imagen. \n
    Se utilizan diferentes colores y grosores para cada parte.
    '''
    mp_drawing.draw_landmarks(
        image,
        results.face_landmarks,
        FACEMESH_CONTOURS,
        mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
        mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1),
    )
    # Draw pose connections
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
        mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2),
    )
    # Draw left hand connections
    mp_drawing.draw_landmarks(
        image,
        results.left_hand_landmarks,
        HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
        mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2),
    )
    # Draw right hand connections
    mp_drawing.draw_landmarks(
        image,
        results.right_hand_landmarks,
        HAND_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
        mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2),
    )

def save_frames(frames, output_folder):
    '''
    ### GUARDAR FRAMES EN CARPETA
     Guarda los frames en la carpeta de salida, con formato `1.jpg`, `2.jpg`, etc. \n
     Si la carpeta no existe, la crea.
    '''
    create_folder(output_folder)
    for num_frame, frame in enumerate(frames):
        frame_path = os.path.join(output_folder, f"{num_frame + 1}.jpg")
        cv2.imwrite(frame_path, cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA))

# CREATE KEYPOINTS
def extract_keypoints(results):
    '''
    ### EXTRAER KEYPOINTS DE RESULTADOS DE MEDIAPIPE
    A partir de los resultados de mediapipe, extrae los keypoints de pose, cara y manos. \n
    Si no se detecta alguna parte, se rellena con ceros.
    '''
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, face, lh, rh])

def get_keypoints(model, sample_path):
    '''
    ### OBTENER KEYPOINTS DE LA MUESTRA
    Retorna la secuencia de keypoints de la muestra
    '''
    kp_seq = np.array([])
    for img_name in os.listdir(sample_path):
        img_path = os.path.join(sample_path, img_name)
        frame = cv2.imread(img_path)
        results = mediapipe_detection(frame, model)
        kp_frame = extract_keypoints(results)
        kp_seq = np.concatenate([kp_seq, [kp_frame]] if kp_seq.size > 0 else [[kp_frame]])
    return kp_seq

def insert_keypoints_sequence(df, n_sample:int, kp_seq):
    '''
    ### INSERTA LOS KEYPOINTS DE LA MUESTRA AL DATAFRAME
    Retorna el mismo DataFrame pero con los keypoints de la muestra agregados
    '''
    for frame, keypoints in enumerate(kp_seq):
        data = {'sample': n_sample, 'frame': frame + 1, 'keypoints': [keypoints]}
        df_keypoints = pd.DataFrame(data)
        df = pd.concat([df, df_keypoints])
    
    return df

# TRAINING MODEL
def get_sequences_and_labels(words_id):
    '''
    ### OBTENER SECUENCIAS Y ETIQUETAS
    Lee los archivos de keypoints de cada palabra y retorna las secuencias de keypoints y sus etiquetas correspondientes
    '''
    sequences, labels = [], []
    
    for word_index, word_id in enumerate(words_id):
        print(word_index, word_id, enumerate(words_id))
        hdf_path = os.path.join(KEYPOINTS_PATH, f"{word_id}.h5")
        data = pd.read_hdf(hdf_path, key='data')
        for _, df_sample in data.groupby('sample'):
            seq_keypoints = [fila['keypoints'] for _, fila in df_sample.iterrows()]
            sequences.append(seq_keypoints)
            labels.append(word_index)
                    
    return sequences, labels

# Creación de directorios (en caso de que no existan)
def create_directories():
    '''
    ### CREACIÓN DE DIRECTORIOS
    Si falta algún directorio / *path*, lo crea. \n
    Si ya existen todos, se informa con `print('...')`.
    '''
    creation_amount = 0
    print('\nCreando directorios...\n')

    if not os.path.exists(VIDEO_FILE_INPUT_PATH): 
        os.makedirs(VIDEO_FILE_INPUT_PATH)
        print('Se creó un nuevo directorio: ', VIDEO_FILE_INPUT_PATH, '\n')
        creation_amount += 1

    if not os.path.exists(FRAME_ACTIONS_PATH): 
        os.makedirs(FRAME_ACTIONS_PATH)
        print('Se creó un nuevo directorio: ', FRAME_ACTIONS_PATH, '\n')
        creation_amount += 1
    
    if not os.path.exists(DATA_PATH): 
        os.makedirs(DATA_PATH)
        print('Se creó un nuevo directorio: ', DATA_PATH, '\n')
        creation_amount += 1
    
    if not os.path.exists(DATA_JSON_PATH): 
        os.makedirs(DATA_JSON_PATH)
        print('Se creó un nuevo directorio: ', DATA_JSON_PATH, '\n')
        creation_amount += 1
    
    if not os.path.exists(MODEL_FOLDER_PATH): 
        os.makedirs(MODEL_FOLDER_PATH)
        print('Se creó un nuevo directorio: ', MODEL_FOLDER_PATH, '\n')
        creation_amount += 1

    if not os.path.exists(MODEL_PATH): 
        os.makedirs(MODEL_PATH)
        print('Se creó un nuevo directorio: ', MODEL_PATH, '\n')
        creation_amount += 1
    
    if not os.path.exists(KEYPOINTS_PATH): 
        os.makedirs(KEYPOINTS_PATH)
        print('Se creó un nuevo directorio: ', KEYPOINTS_PATH, '\n')
        creation_amount += 1
    
    if not os.path.exists(WORDS_JSON_PATH): 
        os.makedirs(WORDS_JSON_PATH)
        print('Se creó un nuevo directorio: ', WORDS_JSON_PATH, '\n')
        creation_amount += 1
    
    if not os.path.exists(DICT_JSON_PATH): 
        os.makedirs(DICT_JSON_PATH)
        print('Se creó un nuevo directorio: ', DICT_JSON_PATH, '\n')
        creation_amount += 1

    if creation_amount == 0:
        print('No se creó ningún directorio (seguramente porque los directorios ya existen).\n')
    else:
        print('Se crearon ', creation_amount, ' directorios en total.\n')


if __name__ == '__main__':
    print(f"Estás usando la versión de Python {sys.version} \n")
    create_directories()
    

