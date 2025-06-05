# # main.py (con indentación corregida)
# from multiprocessing import Pool, TimeoutError # Asegúrate de importar TimeoutError de multiprocessing o concurrent.futures
# import os
# import signal
# import sys
# import time

# import requests
# from Request.request import Request
# from utils.tiff_reader import save_bands_tiff, create_flag_file, create_output_path

# from Constants.constants import (
#     BBOX,
#     SATELLITES,
#     TIME_FROM,
#     SENTINEL2_BANDS,
#     SENTINEL3_BANDS,
#     BANDS,
# )
# from datetime import datetime, timedelta
# # from concurrent.futures import ThreadPoolExecutor # Ya no se usa, puedes quitar esta línea

# # La función process_request debe estar definida a nivel global
# def process_request(
#     satellite, embalse, bbox, iso_date, current_date, max_retries=5, initial_delay=2
# ):
#     """
#     Función que encapsula la lógica de una sola petición y su procesamiento.
#     Incluye lógica de reintento con espera exponencial para errores 429.
#     Ahora también maneja el guardado de archivos .flag para datos vacíos o errores.
#     """
#     output_dir = os.getenv("OUTPUT_DIR")
    
#     if satellite == SATELLITES[0]: # Sentinel-2
#         band_products_to_check = SENTINEL2_BANDS
#     elif satellite == SATELLITES[1]: # Sentinel-3
#         band_products_to_check = SENTINEL3_BANDS
#     else:
#         print(f"Advertencia: Satélite desconocido '{satellite}'. No se pueden verificar las bandas.")
#         return

#     if not band_products_to_check:
#         print(f"Error: No se encontraron bandas definidas para el satélite {satellite}.")
#         return

#     base_output_path = create_output_path(output_dir, satellite, embalse, current_date)
    
#     flag_reference_band_name = band_products_to_check[0] if band_products_to_check else "default_band_name"
#     # ERROR EN LA LÍNEA DE ABAJO: os.out.join debería ser os.path.join
#     expected_flag_path = os.path.join(base_output_path, f"{satellite + "_" + current_date.strftime("%Y%m%d")}.flag") 

#     # --- Pre-verificación: ¿Ya existe el .flag o los TIFFs? ---
#     if os.path.exists(expected_flag_path):
#         print(f"Archivo .flag ya existe para '{embalse.lower()}' ({satellite.lower()}) en {iso_date.split('T')[0]}. Saltando petición API.")
#         return
        
#     all_bands_exist_as_tiff = True
#     for band_name in band_products_to_check:
#         filename = f"{band_name}.tiff"
#         expected_file_path = os.path.join(base_output_path, filename)
#         if not os.path.exists(expected_file_path):
#             all_bands_exist_as_tiff = False
#             break 

#     if all_bands_exist_as_tiff:
#         print(
#             f"Todos los archivos TIFF para '{embalse.lower()}' ({satellite.lower()}) en {iso_date.split('T')[0]} ya existen. Saltando petición API."
#         )
#         return
#     else:
#         print(
#             f"Faltan archivos TIFF para '{embalse.lower()}' ({satellite.lower()}) en {iso_date.split('T')[0]} o no hay archivo .flag. Procesando petición API."
#         )

#     delay = initial_delay
#     for attempt in range(max_retries):
#         try:
#             print(
#                 f"Intento {attempt + 1}: Consultando datos de El {embalse.lower()} en {iso_date} para {satellite.lower()}"
#             )
#             request_obj = Request(bbox=bbox, satellite=satellite, date=iso_date)
#             # Asegúrate de que la petición requests.post() en Request.py tiene un timeout
#             response = request_obj.get_response()

#             if response is None:
#                 print(f"Petición para {embalse.lower()} ({satellite.lower()}) en {iso_date.split('T')[0]} devolvió None.")
                
#                 if attempt < max_retries - 1:
#                     print(f"Reintentando en {delay} segundos (posiblemente un error temporal no 429 o un problema interno).")
#                     time.sleep(delay)
#                     delay *= 2
#                     continue
#                 else:
#                     print(f"No hay más reintentos para {embalse.lower()} ({satellite.lower()}). Creando archivo .flag.")
#                     return
#             elif response == 404:
#                 print(f"No hay datos disponibles para {embalse.lower()} ({satellite.lower()}) en {iso_date.split('T')[0]}. Creando archivo .flag.")
#                 create_flag_file(embalse, satellite, current_date, "no_data_available_after_successful_response")
#             saved = save_bands_tiff(response.content, embalse, satellite, current_date)
#             if saved:
#                 print(f"¡Guardado! Datos de {satellite.lower()} para {embalse.lower()} en {iso_date.split('T')[0]}")
#                 return
#             else:
#                 print(f"No se pudo guardar el TIFF para {embalse.lower()} ({satellite.lower()}). Creando archivo .flag.")
#                 create_flag_file(embalse, satellite, current_date, "failed_to_save_tiff_after_successful_response")
#                 return

#         except requests.exceptions.RequestException as e:
#             print(
#                 f"Error de conexión/red para {embalse.lower()} ({satellite.lower()}): {e}. Reintentando en {delay} segundos..."
#             )
#             time.sleep(delay)
#             delay *= 2
#             continue

#         except Exception as e:
#             print(
#                 f"Error inesperado al procesar {embalse.lower()} ({satellite.lower()}): {e}"
#             )
#             create_flag_file(embalse, satellite, current_date, f"unexpected_processing_error: {str(e)}")
#             return 

#     print(
#         f"Falló la petición para {embalse.lower()} ({satellite.lower()}) después de {max_retries} intentos."
#     )
#     create_flag_file(embalse, satellite, current_date, "all_retries_failed_api_not_responding")

# def worker_init():
#     """
#     Ignora la señal SIGINT en los procesos hijos para que solo el proceso principal
#     maneje el KeyboardInterrupt.
#     """
#     signal.signal(signal.SIGINT, signal.SIG_IGN)


# def main():
#     date_format = "%Y-%m-%dT%H:%M:%SZ"
#     start_date = datetime.strptime(TIME_FROM, date_format)
#     end_date = datetime.now()

#     if start_date > end_date:
#         start_date, end_date = end_date, start_date

#     current_date = start_date
#     max_workers = 5 # Ajusta este valor según la capacidad de tu sistema y las limitaciones de la API.
#     try:
#         while current_date <= end_date:
#             iso_date = current_date.strftime(date_format)
#             # >>> Indentación corregida aquí <<<
#             print(f"\nProcesando fecha: {iso_date.split('T')[0]}")

#             with Pool(processes=max_workers, initializer=worker_init) as pool:
#                 tasks_for_date = []
#                 for satellite in SATELLITES:
#                     for embalse, bbox in BBOX.items():
#                         tasks_for_date.append((
#                             satellite,
#                             embalse,
#                             bbox,
#                             iso_date,
#                             current_date,
#                         ))
                
#                 async_results = pool.starmap_async(process_request, tasks_for_date)
                
#                 try:
#                     async_results.get(timeout=3600) 
#                 except TimeoutError:
#                     print(f"Algunas tareas para la fecha {iso_date.split('T')[0]} excedieron el tiempo límite y fueron terminadas.")
#                     pool.terminate()
#                     pool.join()
#                     sys.exit(1)

#                 except Exception as exc:
#                     print(f"Una excepción inesperada ocurrió durante el procesamiento de la fecha {iso_date.split('T')[0]}: {exc}")
#                     pool.terminate()
#                     pool.join()
#                     sys.exit(1)

#             current_date += timedelta(days=1) # Este también debe estar dentro del while

#         print("\n¡Proceso de peticiones concurrentes completado!") # Este fuera del while, dentro del try
#     except KeyboardInterrupt:
#         print("\n¡Ctrl+C detectado! Deteniendo el proceso...")
#         sys.exit(0)


# if __name__ == "__main__":
#     main()
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys
import time
from datetime import datetime, timedelta
from Request.request import Request
from utils.tiff_reader import save_bands_tiff, create_flag_file, create_output_path
from Constants.constants import BBOX, SATELLITES, TIME_FROM, SENTINEL2_BANDS, SENTINEL3_BANDS

stop_event = threading.Event()

def signal_handler(sig, frame):
    print("\n¡Ctrl+C detectado! Deteniendo el proceso...")
    stop_event.set()  # Señal para detener la ejecución
    sys.exit(0)

# Registrar el manejador de señales
signal.signal(signal.SIGINT, signal_handler)

def process_request(satellite, embalse, bbox, iso_date, current_date, max_retries=5, initial_delay=2):
    """
    Función que encapsula la lógica de una sola petición y su procesamiento.
    Incluye lógica de reintento con espera exponencial para errores 429.
    """
    if stop_event.is_set():
            print(f"Deteniendo tarea para {embalse} ({satellite}) debido a Ctrl+C.")
            return
    output_dir = os.getenv("OUTPUT_DIR")
    
    if satellite == SATELLITES[0]:  # Sentinel-2
        band_products_to_check = SENTINEL2_BANDS
    elif satellite == SATELLITES[1]:  # Sentinel-3
        band_products_to_check = SENTINEL3_BANDS
    else:
        print(f"Advertencia: Satélite desconocido '{satellite}'. No se pueden verificar las bandas.")
        return

    if not band_products_to_check:
        print(f"Error: No se encontraron bandas definidas para el satélite {satellite}.")
        return

    base_output_path = create_output_path(output_dir, satellite, embalse, current_date)
    expected_flag_path = os.path.join(base_output_path, f"{satellite}_{current_date.strftime('%Y%m%d')}.flag")

    # Pre-verificación: ¿Ya existe el .flag o los TIFFs?
    if os.path.exists(expected_flag_path):
        print(f"Archivo .flag ya existe para '{embalse.lower()}' ({satellite.lower()}) en {iso_date.split('T')[0]}. Saltando petición API.")
        return

    all_bands_exist_as_tiff = all(
        os.path.exists(os.path.join(base_output_path, f"{band_name}.tiff"))
        for band_name in band_products_to_check
    )

    if all_bands_exist_as_tiff:
        print(f"Todos los archivos TIFF para '{embalse.lower()}' ({satellite.lower()}) en {iso_date.split('T')[0]} ya existen. Saltando petición API.")
        return

    print(f"Faltan archivos TIFF para '{embalse.lower()}' ({satellite.lower()}) en {iso_date.split('T')[0]}. Procesando petición API.")

    delay = initial_delay
    for attempt in range(max_retries):
        if stop_event.is_set():
            print(f"Deteniendo tarea para {embalse} ({satellite}) debido a Ctrl+C.")
            return
        try:
            print(f"Intento {attempt + 1}: Consultando datos de {embalse.lower()} en {iso_date} para {satellite.lower()}")
            request_obj = Request(bbox=bbox, satellite=satellite, date=iso_date)
            response = request_obj.get_response()

            if response is None:
                print(f"Petición para {embalse.lower()} ({satellite.lower()}) en {iso_date.split('T')[0]} devolvió None.")
                if attempt < max_retries - 1:
                    print(f"Reintentando en {delay} segundos...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    print(f"No hay más reintentos para {embalse.lower()} ({satellite.lower()}). Creando archivo .flag.")
                    create_flag_file(embalse, satellite, current_date, "no_valid_data_or_error_after_retries")
                    return
            elif response == 404:
                print(f"No hay datos disponibles para {embalse.lower()} ({satellite.lower()}) en {iso_date.split('T')[0]}. Creando archivo .flag.")
                create_flag_file(embalse, satellite, current_date, "no_data_available")
                return

            saved = save_bands_tiff(response.content, embalse, satellite, current_date)
            if saved:
                print(f"¡Guardado! Datos de {satellite.lower()} para {embalse.lower()} en {iso_date.split('T')[0]}")
                return
            else:
                print(f"No se pudo guardar el TIFF para {embalse.lower()} ({satellite.lower()}). Creando archivo .flag.")
                create_flag_file(embalse, satellite, current_date, "failed_to_save_tiff")
                return

        except Exception as e:
            print(f"Error inesperado al procesar {embalse.lower()} ({satellite.lower()}): {e}")
            create_flag_file(embalse, satellite, current_date, f"unexpected_error: {str(e)}")
            return

def main():
    date_format = "%Y-%m-%dT%H:%M:%SZ"
    start_date = datetime.strptime(TIME_FROM, date_format)
    end_date = datetime.now()

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    current_date = start_date
    max_workers = 10  # Ajusta este valor según la capacidad de tu sistema y las limitaciones de la API.

    while current_date <= end_date:
        if stop_event.is_set():
            print(f"Deteniendo tarea para {embalse} ({satellite}) debido a Ctrl+C.")
            break
        iso_date = current_date.strftime(date_format)
        print(f"\nProcesando fecha: {iso_date.split('T')[0]}")

        tasks = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for satellite in SATELLITES:
                for embalse, bbox in BBOX.items():
                    tasks.append(
                        executor.submit(process_request, satellite, embalse, bbox, iso_date, current_date)
                    )
            try:
                for future in as_completed(tasks):
                    if stop_event.is_set():
                        print("Deteniendo tareas en ejecución...")
                        executor.shutdown(wait=False)  # Detiene la creación de nuevas tareas
                        return
                    try:
                        future.result()  # Esto captura excepciones lanzadas dentro de `process_request`
                    except Exception as exc:
                        print(f"Error en una tarea: {exc}")
            except KeyboardInterrupt:
                print("\n¡Ctrl+C detectado! Deteniendo el proceso...")
                stop_event.set()
                executor.shutdown(wait=False)  # Detiene la creación de nuevas tareas
                return

        current_date += timedelta(days=1)

    print("\n¡Proceso de peticiones concurrentes completado!")

if __name__ == "__main__":
    main()
