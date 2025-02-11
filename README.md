## WORK IN PROGRESS: ESTE PROYECTO TODAVÍA NO ESTÁ TERMINADO.

Este es un modelo de una red neuronal que traduce Lengua de Señas Ecuatoriana (LSEC) a texto (y voz). Se ha utilizado MediaPipe para obtener los puntos de la seña y para el entrenamiento se usan TensorFlow y Keras.

## SCRIPTS PRINCIPALES
- webscrap_samples.py → obtiene las muestras por medio de scrapping (las saca del sitio web).
- capture_samples.py → captura las muestras y las ubica en la carpeta frame_actions.
- normalize_samples.py → normaliza las muestras para que todas tengan la misma cantidad de frames (importante).
- json_dump.py → llena los arcrhivos json (importantes), que sirven para otros scripts.
- create_keypoints.py → crea los keypoints que se usarán en el entrenamiento.
- training_model.py → entrena la red neuronal.
- evaluate_model.py → donde se realiza la prueba de la red neuronal.
- main.py → donde se utiliza una GUI (interfaz) para usar el traductor.

## SCRIPTS SECUNDARIOS
- model.py → aquí se ajusta el modelo de la red neuronal.
- constants.py → configuración/ajustes de la red neuronal.
- helpers.py → funciones que se utilizan en los scripts principales y creación de directorios faltantes.

## Pasos para probar la red neuronal
1. Obtener muestras
   1.1. (automático) Usar webscrap_samples.py
   1.2. (manual) Poner videos en la carpeta de entrada
3. Capturar las muestras con capture_samples.py
4. Normalizar las muestras con normalize_samples.py
5. Llenar los archivos .json con json_dump.py
6. Generar los .h5 (keypoints) de cada palabra con create_keypoints.py
7. Entrenar el modelo con training_model.py
8. Realizar pruebas con evaluate_model.py

## Video de la explicación del código original:
https://youtu.be/3EK0TxfoAMk
Nota: Esta es una versión modificada, el video explica sobre la versión anterior a esta.
