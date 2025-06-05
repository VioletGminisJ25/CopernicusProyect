"""Modulo de constantes para el acceso a la API de Copernicus Data Space Ecosystem (CDSE)."""

# Constants/constants.py
SATELLITES = [
    "sentinel-2-l2a",
    "sentinel-3-olci-l2",
    # "sentinel-3-slstr",
]

SENTINEL3_BANDS = [
    "CHL_OC4ME",
    "CHL_NN",
    "TSM_NN",
    "PAR",
    "KD490_M07",
    "ADG443_NN",
    # "IWV_W",
    # "A865",
    # "T865",
    # "B01",
    # "B02",
    # "B03",
    # "B04",
    # "B05",
    # "B06",
    # "B07",
    # "B08",
    # "B09",
    # "B10",
    # "B11",
    # "B12",
    # "B16",
    # "B17",
    # "B18",
    # "B21",
]

SENTINEL2_BANDS = [
    "B02",
    "B03",
    "B04",
    "B05",
    "B06",
    "B07",
    "B08",
    "B08",
    "B09",
    "B10",
    "B11",

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
TIME_FROM = "2023-01-01T00:00:00Z"
TIME_TO = "2020-12-31T23:59:00Z"
CLOUD_COVERAGE = 15
