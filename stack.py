#!/usr/bin/env python3
""" Python3 utility to stack jpg files """

import fnmatch
import os
import numpy
from PIL import Image

files = os.listdir('.')
images = [name for name in files if fnmatch.fnmatch(name, 'img*.jpg')]
if len(images):
    width, height = Image.open(images[0]).size
    stack = numpy.zeros((height, width, 3), numpy.float)
    for image in images:
        print(image)
        image_new = numpy.array(Image.open(image), dtype=numpy.float)
        stack = numpy.maximum(stack, image_new)
    stack = numpy.array(numpy.round(stack), dtype=numpy.uint8)
    output = Image.fromarray(stack, mode="RGB")
    output.save("stacked_image.jpg", "JPEG", quality=95, subsampling=0)
    print("Stacked images saved to stacked_image.jpg")
else:
    print("No matching files found to stack.")
