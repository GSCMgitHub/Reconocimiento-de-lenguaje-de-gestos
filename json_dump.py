import os
import json
from constants import *


def json_dump(file_path_LIST = WORDS_JSON_PATH, file_path_DICT = DICT_JSON_PATH, info_path = FRAME_ACTIONS_PATH, show_info=True):
    #1. Creación de nuevo contenido para los archivos JSON (diccionario y lista)
    originals = os.listdir(info_path)
    fixed = []

    for word in originals:
        fixed_text_part1 = word.replace('_', ' ')
        fixed_text_part2 = fixed_text_part1.upper()
        if show_info:
            print('Texto original - Texto arreglado: ', word, ' - ', fixed_text_part2)
        fixed.append(fixed_text_part2)     
    dictionary = dict(zip(originals, fixed))

    words_list = { 
        "word_ids": [

        ]
    }

    words_dict = { 
        "words_text": {

        }

    }

    words_list["word_ids"].extend(fixed)
    words_dict["word_text"].update(dictionary)   

    # 2. Lee el archivo JSON (diccionario)
    with open(file_path_DICT, 'r') as file_d:
        data_dict = json.load(file_d)

    with open(file_path_LIST, 'r') as file_l:
        data_list = json.load(file_l)
    
    if show_info:
        print('\n')

        print('Diccionario: ', dictionary)
        print('Claves: ', originals)
        print('Valores: ', fixed)
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

    if show_info:
        with open(file_path_DICT, 'r') as file_d:
            new_data_dict = json.load(file_d)
            print('Contenido JSON actual (diccionario): ', new_data_dict)

        with open(file_path_LIST, 'r') as file_d:
            new_data_list = json.load(file_d)
            print('Contenido JSON actual (lista): ', new_data_list)

        print('\n')

    #Ojo a la nota de acá
        print("""NOTA IMPORTANTE:
                 Todavía hay trabajo manual: poner tíldes y cualquier otro signo que sea importante.\n""")
   
if __name__ == "__main__":
    json_dump(WORDS_JSON_PATH, DICT_JSON_PATH, FRAME_ACTIONS_PATH)