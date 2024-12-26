import os
import json
import constants
from constants import *


def j_dump(file_path, info_path, debug=False):
    #1. Creación de nuevo contenido para el archivo JSON (diccionario)
    keys = os.listdir(info_path)
    values = []      

    for word in keys:
        fixed_text = word.replace('_', ' ')
        if debug:
            print('Texto arreglado: ', fixed_text)
        values.append(fixed_text)     
        
    dictionary = dict(zip(keys, values))

    # 2. Lee el archivo JSON
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    #DEBUG 1
    if debug:
        print('\n')

        print('Diccionario: ', dictionary)
        print('Claves: ', keys)
        print('Valores: ', values)
        print('\n')

        print('Archivo: ', file)
        print('Contenido JSON anterior: ', data)
        print('words_text anterior: ', words_text)
        print('\n')

    # 3. Llenar 'words_text' de constants.py
    constants.words_text = dictionary

    #DEBUG 2
    if debug:
        print('words_text actual: ', constants.words_text)


    # 4. Lo escribe de vuelta al archivo JSON
    with open(file_path, 'w') as file:
        file = json.dump(dictionary, file, indent=4)

    #DEBUG 3
    if debug:
        with open(file_path, 'r') as file:
            new_data = json.load(file)
            print('Contenido JSON actual: ', new_data)
        print('\n')

    #Ojo a la nota de acá
        print("""NOTA IMPORTANTE:
Todavía hay trabajo manual: poner tíldes y cualquier otro signo o mayúsculas/minúsculas que sean importantes.""")
   
if __name__ == "__main__":
    j_dump(WORDS_JSON_PATH, FRAME_ACTIONS_PATH, True)