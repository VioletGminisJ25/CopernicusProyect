"""
Este es el punto de entrada principal para la aplicación. Aquí se importan los módulos necesarios y se define la función principal que coordina la ejecución del programa.
La función principal itera sobre los satélites y embalses definidos en el módulo de constantes, realiza solicitudes a la API de Copernicus Data Space Ecosystem (CDSE) para obtener datos de imágenes satelitales y guarda las bandas TIFF resultantes en un directorio específico. También incluye la visualización de una banda TIFF utilizando matplotlib.
"""

from Request.request import Request
from utils.tiff_reader import save_bands_tiff, open_tiff
from Constants.constants import BBOX, SATELLITES


def main():
    for satellite in SATELLITES:
        print(satellite)
        print(f"Consultando los datos de {satellite.lower()}")
        for embalse, bbox in BBOX.items():
            print(f"Consultando los datos de El {embalse.lower()}")
            request = Request(bbox=bbox, satellite=satellite)
            response = request.get_response()
            print(response.content)
            print(response.headers["Content-Type"])
            if response.headers["Content-Type"] == "image/tiff":
                save_bands_tiff(response, embalse, satellite=satellite)

            else:
                print("Tipo de contenido no reconocido")
    open_tiff()


if __name__ == "__main__":
    main()
