# Copernicus Project 🌍

Este proyecto permite interactuar con la API de Sentinel Hub para procesar y descargar imágenes satelitales del programa Copernicus. Está diseñado para generar solicitudes personalizadas y obtener imágenes TIFF de bandas específicas de satélites Sentinel.

## 🚀 Funcionalidades

- **Autenticación OAuth2**: Gestión de tokens para acceder a la API de Sentinel Hub.
- **Generación de solicitudes**: Creación dinámica de solicitudes basadas en parámetros como el satélite, el área de interés (bbox) y el rango de fechas.
- **Descarga de imágenes TIFF**: Obtención de imágenes satelitales en formato TIFF con bandas específicas.
- **Procesamiento de datos**: Uso de scripts personalizados (`evalscript`) para definir las bandas y el formato de salida.

## 📂 Estructura del Proyecto

```
CopernicusProyect/
├── Auth/
│   ├── auth.py          # Gestión de autenticación OAuth2
│   └── __init__.py
├── Constants/
│   ├── constants.py     # Constantes del proyecto (bandas, fechas, cobertura de nubes, etc.)
│   └── __init__.py
├── Request/
│   ├── request.py       # Generación y envío de solicitudes a la API
│   └── __init__.py
├── utils/
│   ├── tiff_reader.py   # Procesamiento y visualización de imágenes TIFF
│   └── __init__.py
├── output/              # Carpeta de salida para las imágenes generadas
├── .env                 # Variables de entorno (ID y secreto del cliente)
├── requirements.txt     # Dependencias del proyecto
├── app.py               # Punto de entrada principal del proyecto
└── README.md            # Documentación del proyecto
```

## 🛠️ Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/copernicus-proyect.git
   cd copernicus-proyect
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno en el archivo `.env`:
   ```env
   CLIENT_ID=tu-client-id
   CLIENT_SECRET=tu-client-secret
   ```

## 🖥️ Uso

1. Define los parámetros necesarios en el archivo `constants.py`:
   - **BANDS**: Bandas disponibles para cada satélite.
   - **TIME_FROM** y **TIME_TO**: Rango de fechas para la consulta.
   - **CLOUD_COVERAGE**: Porcentaje máximo de cobertura de nubes permitido.

2. Ejecuta el archivo principal `app.py`:
   ```bash
   python app.py
   ```

3. El programa generará una solicitud a la API de Sentinel Hub y descargará las imágenes TIFF en función de los parámetros configurados.

## 📋 Dependencias

Este proyecto utiliza las siguientes librerías:

- `requests-oauthlib` para la autenticación OAuth2.
- `dotenv` para la gestión de variables de entorno.
- `rasterio` para trabajar con archivos TIFF.
- `matplotlib` para la visualización de imágenes.

Consulta el archivo [`requirements.txt`](requirements.txt) para más detalles.

## 📊 Ejemplo de Solicitud

El archivo `request.py` genera una solicitud con el siguiente formato:

```json
{
  "input": {
    "bounds": {
      "properties": {
        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
      },
      "bbox": [xmin, ymin, xmax, ymax]
    },
    "data": [
      {
        "type": "sentinel-2-l2a",
        "dataFilter": {
          "timeRange": {
            "from": "2023-01-01",
            "to": "2023-12-31"
          },
          "maxCloudCoverage": 20
        }
      }
    ]
  },
  "output": {
    "width": 424,
    "height": 234,
    "responses": [
      {
        "format": {
          "type": "image/tiff"
        }
      }
    ]
  },
  "evalscript": "//VERSION=3\nfunction setup() {\n  return {\n    input: ['B04', 'B03', 'B02'],\n    output: {\n      bands: 3,\n      sampleType: 'FLOAT32'\n    }\n  };\n}\n\nfunction evaluatePixel(sample) {\n  return [sample.B04, sample.B03, sample.B02];\n}"
}
```

## 📂 Organización de los Datos

Las imágenes descargadas se organizan automáticamente en una estructura de carpetas basada en el año, mes, semana y día. Esto facilita la navegación y el análisis de los datos.

### Ejemplo de Estructura de Carpetas

```
output/
├── 2020/
    ├── enero/
        ├── 01/
            ├── 01/
                ├── embalse_de_portodemouros/
                    ├── sentinel-2-l2a/
                        ├── B04.tiff
                        ├── B05.tiff
                        ├── B07.tiff
                        ├── B08.tiff
                    ├── sentinel-3-olci-l2/
                        ├── A865.tiff
                        ├── ADG443_NN.tiff
                        ├── B01.tiff
                        ├── ...
                ├── encoro_da_baxe/
                    ├── sentinel-2-l2a/
                        ├── B04.tiff
                        ├── B05.tiff
                        ├── B07.tiff
                        ├── B08.tiff
                    ├── sentinel-3-olci-l2/
                        ├── A865.tiff
                        ├── ADG443_NN.tiff
                        ├── B01.tiff
                        ├── ...
                ├── encoro_das_forcadas/
                    ├── sentinel-2-l2a/
                        ├── B04.tiff
                        ├── B05.tiff
                        ├── B07.tiff
                        ├── B08.tiff
                    ├── sentinel-3-olci-l2/
                        ├── A865.tiff
                        ├── ADG443_NN.tiff
                        ├── B01.tiff
                        ├── ...
```

### Descripción de la Estructura

- **Año**: Las carpetas principales están organizadas por año.
- **Mes**: Dentro de cada año, las carpetas están organizadas por mes.
- **Semana**: Dentro de cada mes, las carpetas están organizadas por semana.
- **Día**: Dentro de cada semana, las carpetas están organizadas por día.
- **Ubicación**: Dentro de cada día, las carpetas están organizadas por ubicación (por ejemplo, `embalse_de_portodemouros`).
- **Satélite y Producto**: Dentro de cada ubicación, las imágenes se dividen por satélite y producto (por ejemplo, `sentinel-2-l2a` o `sentinel-3-olci-l2`).
- **Bandas**: Dentro de cada producto, las imágenes TIFF se guardan por banda (por ejemplo, `B04.tiff`, `B05.tiff`).

Esta estructura asegura que los datos estén organizados de manera lógica y sean fácilmente accesibles para su análisis.

## 🛰️ Fuentes de Datos

Los datos son obtenidos de la [API de Sentinel Hub](https://www.sentinel-hub.com/), que proporciona acceso a imágenes satelitales del programa Copernicus.

## 🛡️ Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

¡Explora el mundo desde el espacio con el Copernicus Project! 🌌