import os
import json
import constants
from constants import *


def j_dump(file_path_LIST, file_path_DICT, info_path, debug=False):
    #1. Creación de nuevo contenido para el archivo JSON (diccionario y lista)
    keys = os.listdir(info_path)
    values = []

    for word in keys:
        fixed_text = word.replace('_', ' ')
        if debug:
            print('Texto arreglado: ', fixed_text)
        values.append(fixed_text)     
    dictionary = dict(zip(keys, values))

    words_list = { 
        "word_ids": [

        ]
    }
    words_list["word_ids"].extend(values)   

    # 2. Lee el archivo JSON (diccionario)
    with open(file_path_DICT, 'r') as file_d:
        data_dict = json.load(file_d)

    with open(file_path_LIST, 'r') as file_l:
        data_list = json.load(file_l)
    
    #DEBUG 1
    if debug:
        print('\n')

        print('Diccionario: ', dictionary)
        print('Claves: ', keys)
        print('Valores: ', values)
        print('\n')

        print('Archivo (diccionario): ', file_d)
        print('Archivo (lista): ', file_l)
        print('Contenido JSON anterior (lista): ', data_list)
        print('Contenido JSON anterior (diccionario): ', data_dict)
        print('\n')

    # 3. Lo escribe de vuelta a los archivos JSON

    with open(file_path_LIST, 'w') as file_l: #LISTA
        file_l = json.dump(words_list, file_l, indent=4) 

    with open(file_path_DICT, 'w') as file_d: #DICCIONARIO
        file_d = json.dump(dictionary, file_d, indent=4)

    #DEBUG 3
    if debug:
        with open(file_path_DICT, 'r') as file_d:
            new_data_dict = json.load(file_d)
            print('Contenido JSON actual (diccionario): ', new_data_dict)
        with open(file_path_LIST, 'r') as file_d:
            new_data_list = json.load(file_d)
            print('Contenido JSON actual (lista): ', new_data_list)
        print('\n')

    #Ojo a la nota de acá
        print("""NOTA IMPORTANTE:
Todavía hay trabajo manual: poner tíldes y cualquier otro signo o mayúsculas/minúsculas que sean importantes.""")
   
if __name__ == "__main__":
    j_dump(WORDS_JSON_PATH, DICT_JSON_PATH, FRAME_ACTIONS_PATH, True)