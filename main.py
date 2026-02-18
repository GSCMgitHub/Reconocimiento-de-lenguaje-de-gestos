import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from PyQt5.uic import loadUi

import numpy as np
from keras.models import load_model
from mediapipe.modules.python.solutions.holistic import Holistic
from evaluate_model import normalize_keypoints
from helpers import *
from constants import *
from text_to_speech import text_to_speech


class VideoRecorder(QMainWindow):

    def __init__(self):
        '''### VENTANA PRINCIPAL
        Esta clase representa la ventana principal de la aplicación. Se encarga de capturar video desde la cámara, procesar los frames para detectar keypoints, y mostrar el resultado en la interfaz gráfica.
        '''
        super().__init__()
        loadUi('mainwindow.ui', self)
        
        self.capture = cv2.VideoCapture(0)
        
        self.init_lsp()
        
        # self.btn_start.clicked.connect(self.start_recording)
        # self.btn_stop.clicked.connect(self.stop_recording)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30ms
    
    def init_lsp(self):
        '''### INICIALIZAR MODELO Y VARIABLES
        Se inicializa el modelo de mediapipe, se cargan los pesos del modelo de reconocimiento de palabras, y se definen las variables necesarias para el proceso de captura y reconocimiento.
            #### Variables:
            > `kp_seq`: Lista que almacena la secuencia de keypoints detectados en cada frame.
            > `sentence`: Lista que almacena las palabras reconocidas hasta el momento.
            > `count_frame`: Contador de frames que se han procesado desde que se detectó la última mano.
            > `fix_frames`: Contador de frames que se han procesado sin detectar manos después de haber grabado una secuencia de keypoints.
            > `margin_frame`: Número de frames que se deben procesar después de detectar la última mano antes de considerar que la secuencia de keypoints ha terminado.
            > `delay_frames`: Número de frames que se deben procesar sin detectar manos antes de comenzar a procesar la secuencia de keypoints para predecir la palabra reconocida.
            > `model`: Modelo de reconocimiento de palabras cargado desde el archivo especificado en `MODEL_PATH`.
            > `recording`: Booleano que indica si se está grabando una secuencia de keypoints (es decir, si se han detectado manos recientemente y se están procesando los frames para capturar la secuencia de keypoints).
        '''
        self.holistic_model = Holistic()
        self.kp_seq, self.sentence = [], []
        self.count_frame = 0
        self.fix_frames = 0
        self.margin_frame = 1
        self.delay_frames = 3
        self.model = load_model(MODEL_PATH)
        self.recording = False
    
    def update_frame(self):
        '''### ACTUALIZAR FRAME
        Esta función se ejecuta cada vez que el timer se activa (cada 30ms). Captura un frame de la cámara, procesa los keypoints, y actualiza la interfaz gráfica con el video y el texto reconocido.
            - Si se detectan manos o si se está grabando, se incrementa el contador de frames y se agregan los keypoints a la secuencia.
            - Si no se detectan manos y se ha grabado una cantidad suficiente de frames, se procesa la secuencia de keypoints para predecir la palabra reconocida. Si la confianza de la predicción es alta, se obtiene el texto correspondiente y se reproduce mediante text-to-speech.
            - Finalmente, se actualiza el label con el texto reconocido y se muestra el video con los keypoints dibujados.
        '''
        word_ids = get_word_ids(WORDS_JSON_PATH)

        with open('words_dict', 'r') as file:
            words_dict = json.load(file)
        words_text = words_dict['words_text']

        ret, frame = self.capture.read()
        if not ret: return
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = mediapipe_detection(frame, self.holistic_model)
        
        if there_hand(results) or self.recording:
            self.recording = False
            self.count_frame += 1
            if self.count_frame > self.margin_frame:
                self.kp_seq.append(extract_keypoints(results))
            
        else:
            if self.count_frame >= MIN_LENGTH_FRAMES + self.margin_frame:
                self.fix_frames += 1
                if self.fix_frames < self.delay_frames:
                    self.recording = True
                    return
                
                self.kp_seq = self.kp_seq[: - (self.margin_frame + self.delay_frames)]
                kp_normalized = normalize_keypoints(self.kp_seq, int(MODEL_FRAMES))
                res = self.model.predict(np.expand_dims(kp_normalized, axis=0))[0]
                
                if res[np.argmax(res)] > 0.7:
                    word_id = word_ids[np.argmax(res)].split('-')[0]
                    sent = words_text.get(word_id)
                    self.sentence.insert(0, sent)
                    text_to_speech(sent) # ONLY LOCAL (NO SERVER)
            
            self.recording = False
            self.fix_frames = 0
            self.count_frame = 0
            self.kp_seq = []
        
        self.lbl_output.setText(" - ".join(self.sentence))
        draw_keypoints(image, results)
        
        height, width, channel = image.shape
        step = channel * width
        qImg = QImage(image.data, width, height, step, QImage.Format_RGB888)
        
        scaled_qImg = qImg.scaled(self.lbl_video.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.lbl_video.setPixmap(QPixmap.fromImage(scaled_qImg))

    # def start_recording(self):
    #     if not self.recording:
    #         self.recording = True
    #         # self.video_writer = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
    #         self.btn_start.setEnabled(False)
    #         self.btn_stop.setEnabled(True)
    
    # def stop_recording(self):
    #     if self.recording:
    #         self.recording = False
    #         # self.video_writer.release()
    #         self.btn_start.setEnabled(True)
    #         self.btn_stop.setEnabled(False)
    
    def closeEvent(self, event):
        self.capture.release()
        # if self.is_recording:
            # self.video_writer.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoRecorder()
    window.show()
    # window.showFullScreen()
    sys.exit(app.exec_())
