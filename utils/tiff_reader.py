"""
Este módulo contiene funciones para guardar y abrir archivos TIFF utilizando la biblioteca rasterio.
Las funciones están diseñadas para trabajar con datos de satélites y permiten guardar bandas específicas en formato TIFF, así como abrir y visualizar estas bandas.
El módulo también incluye la creación de directorios para organizar los archivos TIFF guardados, basándose en la fecha y el embalse especificado.
"""

import io
import rasterio
from rasterio.io import MemoryFile
import numpy as np
import matplotlib.pyplot as plt
import os
from Constants.constants import BANDS, TIME_FROM
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, "Spanish_Spain.1252")


def save_bands_tiff(response, embalse, satellite, iso_date):
    """
    Guarda las bandas de un archivo TIFF en un directorio específico.
    La función crea un directorio basado en la fecha y el embalse especificado, y guarda cada banda como un archivo TIFF separado.
    """
    # Convierte la cadena de tiempo a un objeto datetime

    date_obj = iso_date

    # Crea un directorio con la estructura de carpetas Año/Mes/Día
    # output_dir = f"output/{date_obj.year}/{date_obj.strftime("%B")}/{str(date_obj.isocalendar().week).zfill(2)}/{str(date_obj.day).zfill(2)}/{str(embalse).lower().replace(" ","_")}/{satellite.lower()}"
    output_dir = create_output_path(os.getenv("OUTPUT_DIR"), satellite, embalse, date_obj)

    os.makedirs(output_dir, exist_ok=True)

    with MemoryFile(response) as memfile:
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
    path="output/2020/enero/01/01/encoro_das_forcadas/sentinel-3-olci-l2/TSM_NN.tiff",
):
    """
    Abre un archivo TIFF y lo visualiza utilizando matplotlib.
    """
    try:
        with rasterio.open(path) as src:
            band = src.read(1)
            plt.imshow(band, cmap="viridis")
            plt.colorbar()
            plt.title(f"Visualización de Banda {path.split('/')[-1].split(".")[0]}")
            plt.show()
    except Exception as e:
        print(f"No se pudo abrir el archivo: {e}")


def create_output_path(base_dir, satellite, embalse, current_date):
    """Crea la estructura de directorios para guardar los TIFFs."""
    year = current_date.year
    month_name_lower = current_date.strftime("%B").lower()
    day = f"{current_date.day:02d}"
    embalse_lower = embalse.lower().replace(" ", "_")
    satellite_folder_name = satellite.lower()
    path = os.path.join(
        base_dir,
        str(year),
        month_name_lower,
        str(current_date.isocalendar().week).zfill(2),
        day,
        embalse_lower,
        satellite_folder_name,
    )
    os.makedirs(path, exist_ok=True)
    return path


def create_flag_file(embalse, satellite, current_date, reason):
    """
    Crea un archivo .flag en el directorio de salida para indicar que no hay datos útiles.
    """
    output_dir = os.getenv("OUTPUT_DIR")
    output_base_path = create_output_path(output_dir, satellite, embalse, current_date)

    # Usamos la primera banda como referencia para el nombre del flag
    # Esto asume que si la respuesta general es "vacía", aplica a todas las bandas.
    if BANDS[satellite]:
        flag_reference_band_name = satellite + "_" + current_date.strftime("%Y%m%d")
    else:
        flag_reference_band_name = "no_bands_defined"  # Fallback

    flag_filename = os.path.join(output_base_path, f"{flag_reference_band_name}.flag")

    with open(flag_filename, "w") as f:
        f.write(
            f"No data available or image processing issue for {current_date.isoformat().split('T')[0]}\n"
        )
        f.write(f"Reason: {reason}\n")
        f.write(
            "This file indicates that a request was made, but no valid data was found or saved for this product.\n"
        )
    print(f"⚠️ Creado archivo .flag: {flag_filename} - Motivo: {reason}")
    return True

def is_empty_tiff_rasterio(tiff_bytes, expected_data_range=None):
    # ... (contenido de la función is_empty_tiff_rasterio, como se definió arriba) ...
    """
    Verifica si un TIFF multibanda (GeoTIFF) está vacío o contiene principalmente valores
    uniformes (negro/blanco/relleno/sin datos) utilizando Rasterio.

    Args:
        tiff_bytes (bytes): Contenido binario del TIFF.
        expected_data_range (tuple, optional): Tupla (min_val, max_val) del rango esperado
                                                para los datos de la banda. Esto ayuda a
                                                determinar los umbrales de "negro" y "blanco".
    Returns:
        tuple: (bool, str) donde bool es True si está vacío/corrupto, y str es el motivo.
    """
    try:
        with rasterio.open(io.BytesIO(tiff_bytes)) as src:
            # 1. Comprobar si hay un valor NoData explícito en los metadatos del TIFF
            if src.nodata is not None:
                band_data_with_nodata_mask = src.read(1, masked=True)
                if np.all(band_data_with_nodata_mask.mask):
                    # print("Debug: TIFF contiene solo valores de NoData explícitos (enmascarados).")
                    return True, "only_nodata"

            # 2. Leer la banda como float32 para manejar NaNs y valores de relleno.
            band_data = src.read(1).astype(np.float32)

            # 3. Contar la proporción de píxeles NaN. Si una alta proporción son NaN, consideramos la imagen vacía.
            nan_count = np.sum(np.isnan(band_data))
            total_pixels = band_data.size
            nan_ratio = nan_count / total_pixels

            if nan_ratio > 0.99: # Más del 99% de los píxeles son NaN
                # print(f"Debug: {nan_ratio*100:.2f}% de los píxeles son NaN. Considerado vacío.")
                return True, "mostly_nan"

            # Filtrar NaNs para calcular estadísticas solo de datos válidos.
            valid_data = band_data[~np.isnan(band_data)]

            if valid_data.size == 0: # Si después de quitar NaNs no queda ningún píxel válido
                # print("Debug: TIFF no contiene datos válidos después de filtrar NaNs (todos eran NaN o NoData).")
                return True, "no_valid_pixels"

            mean_val = np.mean(valid_data)
            std_dev = np.std(valid_data)
            # min_val_actual = np.min(valid_data) # No se usa directamente en la lógica
            # max_val_actual = np.max(valid_data) # No se usa directamente en la lógica

            # print(
            #     f"Debug: Band 1 (valid data) - Mean: {mean_val:.4f}, Std Dev: {std_dev:.4f}"
            # )

            # Umbral de desviación estándar para uniformidad. Si es casi cero, es uniforme.
            uniformity_threshold_std = 0.001 

            if std_dev < uniformity_threshold_std:
                # 4. Comprobar valores de relleno comunes y extremos para los datos válidos restantes
                # Valor de relleno común para datos de satélite (ej. 65535.0 en FLOAT32)
                if np.isclose(mean_val, 65535.0, atol=1.0): 
                     # print(f"Debug: TIFF uniforme y promedio cercano a 65535.0 (posible relleno).")
                     return True, "uniform_fill_65535"
                # Valor de relleno común para "negro" (0.0)
                if np.isclose(mean_val, 0.0, atol=1e-6): 
                     # print(f"Debug: TIFF uniforme y promedio cercano a 0.0 (posible relleno/negro).")
                     return True, "uniform_fill_0"

                # 5. Si se proporciona un rango de datos esperado, verificar si el valor promedio
                # está significativamente fuera de ese rango para los datos válidos restantes.
                if expected_data_range is not None:
                    min_expected, max_expected = expected_data_range
                    # Evitar división por cero si el rango es cero
                    data_range = max_expected - min_expected if max_expected != min_expected else 1.0 

                    # Si el valor promedio está significativamente fuera del rango esperado
                    if mean_val < min_expected - data_range * 0.01 or \
                       mean_val > max_expected + data_range * 0.01:
                        # print(f"Debug: TIFF uniforme y promedio fuera del rango esperado para datos válidos ({mean_val:.4f}).")
                        return True, "uniform_out_of_range"
                    
                    # Si es muy uniforme y muy cercano a los extremos del rango esperado (negro/blanco físico)
                    if np.isclose(mean_val, min_expected, atol=data_range * 0.005):
                        # print(f"Debug: TIFF uniforme y muy cercano al mínimo esperado para datos válidos ({mean_val:.4f}).")
                        return True, "uniform_near_min_expected"
                    if np.isclose(mean_val, max_expected, atol=data_range * 0.005):
                        # print(f"Debug: TIFF uniforme y muy cercano al máximo esperado para datos válidos ({mean_val:.4f}).")
                        return True, "uniform_near_max_expected"

        return False, "has_data" # No es un TIFF vacío según los criterios

    except rasterio.errors.RasterioIOError as e:
        # print(f"❌ Error de Rasterio al intentar abrir el TIFF. Podría ser un archivo corrupto o no válido: {e}")
        with open("debug_corrupt_tiff_S3.bin", "wb") as f: # Guardar para depuración
            f.write(tiff_bytes)
        return True, "corrupt_tiff" 
    except Exception as e:
        # print(f"❌ Error inesperado en is_empty_tiff_rasterio: {e}")
        return True, f"unexpected_error: {str(e)}"

