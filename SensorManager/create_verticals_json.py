import requests
import json
from json_utilities import *

VERTICALS_API = "https://iudx-rs-onem2m.iiit.ac.in/resource/sensors"

VERTICALS_DATA = requests.get(VERTICALS_API)
VERTICAL_JSON = VERTICALS_DATA.json()


write_JSON(FOLDER_PATH,'verticals.json',VERTICAL_JSON)