from app import encode_image_as_b64_wmetrics, decode_image_fromb64
from PIL import Image
import numpy as np
import pytest


@pytest.mark.parametrize("testinput,expected", [
    ("cat.jpg", True),
])
def test(testinput, expected):
    encoded = encode_image_as_b64_wmetrics(testinput)
    decoded = decode_image_fromb64(encoded[3], encoded[1], encoded[2])
    img = np.asarray(Image.open(testinput))
    return np.allclose(decoded, img)
