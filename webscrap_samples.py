import os
import requests
from constants import VIDEO_FILE_INPUT_PATH
from bs4 import BeautifulSoup

# URL de la página web a scrapear
url_main = 'https://www.utm.edu.ec/inclusion/index.php/servicios/apoyo-educativo/glosario-de-lengua-de-senias-ecuatorianas-lsec'

# Lista de elementos con length 1 (declaración) y valores href (sirven para encontrar los enlaces donde están los videos)
letras = []
href_s = []

#solicitud GET
response = requests.get(url_main, verify=False)

# Verifica que la solicitud fue exitosa
if response.status_code == 200:
    # Creación de un objeto BeautifulSoup con el contenido HTML de la página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Se encuentra y se extra todo lo que tenga el tag "a"
    elementos = soup.find_all('a')

# Busca elementos que sean de solo una letra y sus valores href
    #print("Letras:")
    for elemento in elementos:
        if len(elemento.text) == 1:
            letras.append(elemento.text)
            href = elemento.get('href')
            href_s.append(href)
            #print(elemento.text)

    #print("Letras y valores enlaces listos.")
    diccionario_href = dict(zip(letras,href_s))
    #print("\nDiccionario listo (letras y href's): ")

    #for letra, href in diccionario_href.items():
    #    print(f"Letra: {letra}")
    #    print(f"Valor href: {href}")
    #    print()

    
#URL 2: hecha para encajar con el valor href
    url_2 = 'https://www.utm.edu.ec'
#src_s será los links de google drive sin modificar
    src_s = []

    #print("Enlaces de videos (Sin modificar):\n")
    for letra, href in diccionario_href.items():

        sub_url = url_2 + href
        sub_response = requests.get(sub_url, verify=False)

        if sub_response.status_code == 200:
            sub_soup = BeautifulSoup(sub_response.content, 'html.parser')
            iframes = sub_soup.find_all('iframe', src=True)
            print()

            if len(iframes) == 0: #Avisar si no encuentra ningún iframe.
                print('No iframes encontrados para la letra:',letra,'\n')
            else:
                #print(letra)
                #print()
                for iframe in iframes:
                    src = iframe.get('src')
                    src_s.append(src)
                    #print(src)
                #print()
        else:
            print('Error al realizar la solicitud:', sub_response.status_code)
            break
            
    
    video_links = []

    print('Links de descarga:')
    for src in src_s:
        url_parte1 = src.replace('https://drive.google.com/file/d/','https://drive.usercontent.google.com/uc?id=')
        url_parte2 = url_parte1.replace('/preview', '&export=download')
        print(url_parte2,'\n')
        video_links.append(url_parte2)


    video_amount = 0

    for link in video_links:
        download_response = requests.get(link, verify=False)
        
        if download_response.status_code == 200:
            download_soup = BeautifulSoup(download_response.content, 'html.parser')
            content_disposition = download_response.headers.get('content-disposition')
            
            #Encuentra el nombre del archivo en los encabezados
            if content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
                SAVE_VID_PATH = os.path.join(VIDEO_FILE_INPUT_PATH, filename)

                with open(SAVE_VID_PATH, 'wb') as file: #Guarda el archivo en VIDEO_FILE_INPUT (constants.py)
                    file.write(download_response.content)

                video_amount += 1
                print('\nEl archivo ', filename,' ha sido guardado en:', SAVE_VID_PATH)

                if video_amount == 1: #Indica cuantos videos se han descargado via print().
                    print('\nHasta ahora, se ha descargado 1 archivo.\n')
                else:
                    print('\nHasta ahora, se han descargado',video_amount,'archivos.\n')

            else:
                print('No se encontró el nombre del archivo en los encabezados.')


    #El diccionario src contiene las letras y los links (google drive) correspondientes.
    #diccionario_vid_url = dict(zip(letras,video_links))

    #print("\nDiccionario listo (letras y video links): ")
    #for letra, video in diccionario_vid_url.items():
    #    print(f"Letra: {letra}")
    #    print(f"Video link: {video}")
    #    print()


else:
    print('Error al realizar la solicitud:', response.status_code)

    #TODO:
    #Descargar los archivos