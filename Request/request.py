from urllib import response
import numpy as np
import rasterio
import requests
from Auth.auth import Auth
from Constants.constants import BANDS, TIME_FROM, TIME_TO, CLOUD_COVERAGE
from datetime import datetime, timedelta
from PIL import Image
import io
from utils.tiff_reader import is_empty_tiff_rasterio 


class Request:
    """Clase para realizar peticiones a la API de Copernicus Data Space Ecosystem (CDSE).
    Esta clase se encarga de construir la solicitud y enviar la petición a la API."""

    def __init__(self, bbox, satellite, date):
        self.satellite = satellite
        print(BANDS[satellite])
        self.url = "https://sh.dataspace.copernicus.eu/api/v1/process"
        self.auth = Auth()
        self.evalscript = f"""
            //VERSION=3
            function setup() {{
              return {{
                input: {BANDS[satellite]},
                output: {{
                  bands: {len(BANDS[satellite])},
                  sampleType: "FLOAT32",  // para valores numéricos precisos
                }},
              }};
            }}

            function evaluatePixel(sample) {{
              return [{', '.join([ f"sample.{band}" for band in BANDS[satellite]])}];
            }}
        """
        self.request = {
            "input": {
                "bounds": {
                    "properties": {
                        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                    },
                    "bbox": bbox,
                },
                "data": [
                    {
                        "type": satellite,
                        "dataFilter": {
                            "timeRange": {
                                "from": date,
                                "to": date.split("T")[0] + "T23:59:59Z",
                            },
                            "maxCloudCoverage": CLOUD_COVERAGE,
                        },
                    }
                ],
            },
            "output": {
                "width": 1508,
                "height": 1199.507,
                "responses": [{"format": {"type": "image/tiff"}}],
            },
            "evalscript": self.evalscript,
        }

    def get_response(self):
        """
        Realiza la petición de procesamiento.
        Devuelve el objeto de respuesta si es un TIFF válido y no vacío.
        Devuelve None si no hay datos, hay un error o el TIFF está vacío/corrupto.
        No guarda archivos ni crea .flag aquí.
        """
        response = None 
        REQUEST_TIMEOUT = (15, 30)
        try:
            print(f"DEBUG: Realizando petición de procesamiento a {self.url}...")
            response = self.auth.oauth.post(self.url, json=self.request)
            response.raise_for_status() # Lanza una excepción para errores HTTP (4xx, 5xx)

            content_type = response.headers.get("Content-Type", "")
            print(f"DEBUG: Content-Type de la respuesta del proceso: {content_type}")

            if "image/tiff" in content_type:
                expected_range = None
                if self.satellite == "sentinel-2-l2a":
                    expected_range = (0, 10000) 
                elif self.satellite == "sentinel-3-olci-l2":
                    # Aquí ajusta el rango según las bandas específicas que pidas
                    # Para CHL_OC4ME, CHL_NN, TSM_NN, PAR, KD490_M07, ADG443_NN, los rangos son muy variados.
                    # El valor de 65535 es un buen indicador de "sin datos" para UINT16 que se convierten a FLOAT32.
                    # Un rango muy amplio (ej. 0 a 10000) podría ser útil, o solo confiar en NaNs y 65535.
                    expected_range = (0.01, 100.0) # Un rango más genérico para productos L2 de OLCI. Ajustar si es necesario.
                    
                is_empty, reason = is_empty_tiff_rasterio(response.content, expected_data_range=expected_range)
                if is_empty:
                    print(f"⚠️ TIFF recibido pero parece estar vacío (motivo: {reason}).")
                    return 404 # Indica que no hay datos útiles
                else:
                    print("✅ TIFF recibido y parece contener datos válidos.")
                    return response # Devuelve el objeto response para que se procese fuera
            else:
                print(f"❌ La respuesta no es un TIFF. Content-Type: {content_type}")
                try:
                    error_json = response.json()
                    print(f"Mensaje de error de la API: {error_json}")
                except ValueError:
                    print(f"Contenido no JSON: {response.text[:500]}...")
                return None # No es un TIFF, o es un error de la API (no reintentable aquí)
        except requests.exceptions.Timeout as e:
            print(f"❌ Error de timeout: La petición a la API excedió el tiempo límite ({REQUEST_TIMEOUT}s). {e}")
            # Crea un archivo .flag o maneja este caso como un fallo para esta fecha/embalse
            return None # Indica que la petición falló debido a un timeout

        except requests.exceptions.HTTPError as e:
            print(f"❌ Error HTTP {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 429:
                print("DEBUG: Límite de peticiones excedido (429).")
                # Aquí puedes implementar una lógica de reintento con espera exponencial
                # Si `get_response` está haciendo los reintentos para 429, el `process_request`
                # en main.py no necesita reintentar ese tipo de error.
                # Si quieres que el `main.py` maneje el reintento del 429, `get_response`
                # debería lanzar algo que `main.py` pueda capturar o devolver un valor específico.
                # Para simplificar ahora, devolvemos None para que `process_request` lo maneje.
                return None
            else:
                # Otros errores HTTP, como 400, 404, 500
                return None
        except requests.exceptions.RequestException as e:
            # Captura errores HTTP (de raise_for_status()) y errores de red
            status_code = response.status_code if response is not None else "N/A"
            print(f"❌ Error de red/API al realizar la petición de procesamiento (Status: {status_code}): {e}")
            if response is not None and response.text:
                print(f"DEBUG: Contenido del error: {response.text[:500]}")
            # get_response simplemente devuelve None. El reintento se maneja en process_request.
            return None 
        except Exception as e:
            print(f"❌ Error inesperado al obtener la respuesta de procesamiento: {e}")
            return None



