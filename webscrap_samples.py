import os
import requests
from constants import VIDEO_FILE_INPUT_PATH
from bs4 import BeautifulSoup

'''
    ### OBTENER MUESTRAS VÍA SCRAPPING
    Busca y descarga los videos, y los guarda en la carpeta de entrada (VIDEO_FILE_INPUT_PATH).
    Cabe decir que esto funciona para un sitio en específico (me refiero al enlace en url_specific).
'''

def webscrap_samples(url_specific = 'https://www.utm.edu.ec/inclusion/index.php/servicios/apoyo-educativo/glosario-de-lengua-de-senias-ecuatorianas-lsec', url_general = 'https://www.utm.edu.ec'):
    
    '''
        ### 1.  Con url_specific, se buscarán valores href, los cuales serán usados para encontrar 
                las urls donde se encuentran los videos.

                Aquí un ejemplo de un valor href: 
                /inclusion/index.php/servicios/apoyo-educativo/glosario-de-lengua-de-senias-ecuatorianas-lsec/category/3-a
    '''
    # Lista de elementos con length 1 (declaración) y valores href (sirven para encontrar los enlaces donde están los videos)
    letras = []
    href_s = []

    #solicitud GET
    response = requests.get(url_specific, verify=False)

    # Verifica que la solicitud fue exitosa
    if response.status_code == 200:
        # Creación de un objeto BeautifulSoup con el contenido HTML de la página
        soup = BeautifulSoup(response.content, 'html.parser')

        # Se encuentra y se extra todo lo que tenga el tag "a"
        elementos = soup.find_all('a')

    # Busca elementos que sean de un caracter (letra)  y sus valores href
        for elemento in elementos:
            if len(elemento.text) == 1:
                letras.append(elemento.text)
                href = elemento.get('href')
                href_s.append(href)

        diccionario_href = dict(zip(letras,href_s))

        '''
            2.  
                2.1. Con url_general, se formarán las url's donde están los videos.

                    Valor href: 
                        /inclusion/index.php/servicios/apoyo-educativo/glosario-de-lengua-de-senias-ecuatorianas-lsec/category/3-a
                    Entonces, url_general + valor href =
                        https://www.utm.edu.ec/inclusion/index.php/servicios/apoyo-educativo/glosario-de-lengua-de-senias-ecuatorianas-lsec/category/3-a
         
                2.2. A continuación, se buscarán links de google drive los cuales contienen las ID's de los videos. Se
                    Link de drive: https://drive.google.com/file/d/17OKgDQBISNK5ALWE2VX7v8Pc8xT8Cuur/preview
                    El ID sería:                                   17OKgDQBISNK5ALWE2VX7v8Pc8xT8Cuur

                2.3. Por último, con esta ID, se encontrarán los links de descarga de google drive de los videos.
                    Pasa de esto:                https://drive.google.com/file/d/_ID_aquí_/preview
                    A esto:           https://drive.usercontent.google.com/uc?id=_ID_aquí_/&export=download
                
        '''
        src_s = []

        for letra, href in diccionario_href.items():
            sub_url = url_general + href
            sub_response = requests.get(sub_url, verify=False)

            if sub_response.status_code == 200:
                sub_soup = BeautifulSoup(sub_response.content, 'html.parser')
                iframes = sub_soup.find_all('iframe', src=True)
                print()

                if len(iframes) == 0: #Avisar si no encuentra ningún iframe.
                    print('No iframes encontrados para la letra:',letra,'\n')
                else:
                    print(letra)
                    print()
                    for iframe in iframes:
                        src = iframe.get('src')
                        src_s.append(src)
                        print(src)
                    print()
            else:
                print('Error al realizar la solicitud:', sub_response.status_code)
                break
                
        
        download_links = []

        print('Links de descarga:\n')
        for src in src_s:
            raw_download_url = src.replace('https://drive.google.com/file/d/','https://drive.usercontent.google.com/uc?id=')
            download_url = raw_download_url.replace('/preview', '&export=download')
            print(download_url)
            download_links.append(download_url)

        '''
            ### 3.  De los links de descarga, se extraen los archivos (videos). Los archivos son guardados dentro de
                    VIDEO_FILE_INPUT_PATH.
        '''
        video_amount = 0

        for link in download_links:
            download_link_response = requests.get(link, verify=False)
            
            if download_link_response.status_code == 200:
                content_disposition = download_link_response.headers.get('content-disposition')
                
                #Encuentra el nombre del archivo en los encabezados
                if content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                    SAVE_VID_PATH = os.path.join(VIDEO_FILE_INPUT_PATH, filename)

                    with open(SAVE_VID_PATH, 'wb') as file: #Guarda el archivo en VIDEO_FILE_INPUT (constants.py)
                        file.write(download_link_response.content)

                    video_amount += 1
                    print('\nEl archivo ', filename,' ha sido guardado en:', SAVE_VID_PATH)

                    if video_amount == 1: #Indica cuantos videos se han descargado via print().
                        print('\nHasta ahora, se ha descargado 1 archivo.\n')
                    else:
                        print('\nHasta ahora, se han descargado',video_amount,'archivos.\n')
                else:
                    print('No se encontró el nombre del archivo en los encabezados.')
    else:
        print('Error al realizar la solicitud:', response.status_code)

if __name__ == "__main__": 
    webscrap_samples()