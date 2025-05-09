from Auth.auth import Auth
from Constants.constants import BANDS, TIME_FROM, TIME_TO, CLOUD_COVERAGE


class Request:
    """Clase para realizar peticiones a la API de Copernicus Data Space Ecosystem (CDSE).
    Esta clase se encarga de construir la solicitud y enviar la petición a la API."""

    def __init__(self, bbox, satellite):
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
                                "from": TIME_FROM,
                                "to": TIME_TO,
                            },
                            "maxCloudCoverage": CLOUD_COVERAGE,
                        },
                    }
                ],
            },
            "output": {
                "width": 424,
                "height": 234,
                "responses": [{"format": {"type": "image/tiff"}}],
            },
            "evalscript": self.evalscript,
        }

    def get_response(self):
        response = self.auth.oauth.post(self.url, json=self.request)
        return response
