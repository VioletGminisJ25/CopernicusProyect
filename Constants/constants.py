"""Modulo de constantes para el acceso a la API de Copernicus Data Space Ecosystem (CDSE)."""

# Constants/constants.py
SATELLITES = [
    "sentinel-3-olci-l2",
    "sentinel-2-l2a",
]

SENTINEL3_BANDS = [
    "IWV_W",
    "CHL_OC4ME",
    "TSM_NN",
    "PAR",
    "KD490_M07",
    "A865",
    "T865",
    "CHL_NN",
    "ADG443_NN",
    "B01",
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B09",
    "B10",
    "B11",
    "B12",
    "B16",
    "B17",
    "B18",
    "B21",
]

SENTINEL2_BANDS = [
    "B04",
    "B05",
    "B07",
    "B08",
]

BANDS = {
    "sentinel-3-olci-l2": SENTINEL3_BANDS,
    "sentinel-2-l2a": SENTINEL2_BANDS,
}

BBOX = {
    "Embalse de portodemouros": [-8.20713, 42.808751, -8.062248, 42.879612],
    "Encoro da Baxe": [-8.618259, 42.59685, -8.590279, 42.610749],
    "Encoro das Forcadas": [-8.095722, 43.590898, -8.050489, 43.617623],
}
TIME_FROM = "2020-01-01T00:00:00Z"
TIME_TO = "2020-12-31T00:00:00Z"
CLOUD_COVERAGE = 5
