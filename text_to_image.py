import subprocess

## Image to text module
import argparse
import io

from google.cloud import vision
from google.cloud.vision import types

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "visionkey.json"


def detect_text(path): ## path is path to image
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    for text in texts:
        return(u'\n"{}"'.format(unicode(text.description)))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])
