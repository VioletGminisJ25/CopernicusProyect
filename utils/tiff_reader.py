"""
Este módulo contiene funciones para guardar y abrir archivos TIFF utilizando la biblioteca rasterio.
Las funciones están diseñadas para trabajar con datos de satélites y permiten guardar bandas específicas en formato TIFF, así como abrir y visualizar estas bandas.
El módulo también incluye la creación de directorios para organizar los archivos TIFF guardados, basándose en la fecha y el embalse especificado.
"""

import rasterio
from rasterio.io import MemoryFile
import numpy as np
import matplotlib.pyplot as plt
import os
from Constants.constants import BANDS, TIME_FROM
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")


def save_bands_tiff(response, embalse, satellite):
    """
    Guarda las bandas de un archivo TIFF en un directorio específico.
    La función crea un directorio basado en la fecha y el embalse especificado, y guarda cada banda como un archivo TIFF separado.
    """
    # Convierte la cadena de tiempo a un objeto datetime
    date_obj = datetime.strptime(TIME_FROM, "%Y-%m-%dT%H:%M:%SZ")

    # Crea un directorio con la estructura de carpetas Año/Mes/Día
    output_dir = f"output/{date_obj.year}/{date_obj.strftime("%B")}/{str(date_obj.isocalendar().week).zfill(2)}/{str(date_obj.day).zfill(2)}/{str(embalse).lower().replace(" ","_")}/{satellite.lower()}"
    os.makedirs(output_dir, exist_ok=True)

    with MemoryFile(response.content) as memfile:
        with memfile.open() as src:

            for i in range(1, src.count + 1):
                band_data = src.read(i)
                print(f"Escribiendo la banda: {BANDS[satellite][i - 1]}")

                output_path = os.path.join(output_dir, f"{BANDS[satellite][i-1]}.tiff")
                print(f"Guardando archivo en: {output_path}")

                profile = src.profile
                profile.update(dtype=rasterio.float32, count=1)

                with rasterio.open(output_path, "w", **profile) as dst:
                    dst.write(band_data, 1)
    print(f"Archivos TIFF guardados exitosamente en: {output_dir}")


def open_tiff(
    path="output/2020/enero/01/01/embalse_de_portodemouros/sentinel-2-l2a/B04.tiff",
):
    """
    Abre un archivo TIFF y lo visualiza utilizando matplotlib.
    """
    try:
        with rasterio.open(path) as src:
            band = src.read(1)
            plt.imshow(band, cmap="viridis")
            plt.colorbar()
            plt.title("Visualización de Banda 1")
            plt.show()
    except Exception as e:
        print(f"No se pudo abrir el archivo: {e}")


from PIL import Image
