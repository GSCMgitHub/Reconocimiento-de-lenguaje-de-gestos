import os
import cv2

# CONFIGURACIONES
MIN_LENGTH_FRAMES = 5
LENGTH_KEYPOINTS = 1662
MODEL_FRAMES = 15

# RUTAS
ROOT_PATH = os.getcwd()
VIDEO_FILE_INPUT_PATH = os.path.join(ROOT_PATH, "video_file_input")
FRAME_ACTIONS_PATH = os.path.join(ROOT_PATH, "frame_actions")
DATA_PATH = os.path.join(ROOT_PATH, "data")
DATA_JSON_PATH = os.path.join(DATA_PATH, "data.json")
MODEL_FOLDER_PATH = os.path.join(ROOT_PATH, "models")
MODEL_PATH = os.path.join(MODEL_FOLDER_PATH, f"actions_{MODEL_FRAMES}.keras")
KEYPOINTS_PATH = os.path.join(DATA_PATH, "keypoints")
WORDS_JSON_PATH = os.path.join(MODEL_FOLDER_PATH, "words_list.json") #LISTA
DICT_JSON_PATH = os.path.join(MODEL_FOLDER_PATH, "words_dict.json") #DICCIONARIO

# PARÁMETROS (MOSTRAR IMÁGEN)
FONT = cv2.FONT_HERSHEY_PLAIN
FONT_SIZE = 1.5
FONT_POS = (5, 30)