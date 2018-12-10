import io
import base64
#import pillow
from pymodm import connect
from pymodm import MongoModel, fields
from flask import Flask, jsonify, request
from matplotlib import pyplot as plt
import matplotlib.image as mpimg

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")

class Image(MongoModel):
    filename = fields.CharField(primary_key=True)
    raw_image = fields.CharField()
    processed_images = fields.DictField()
    metrics = fields.DictField()
    timestamp = fields.DateTimeField()


def encode_image_as_b64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read())


def decode_b64_image(base64_string):
    image_bytes = base64.b64decode(base64_string)
    image_buf = io.BytesIO(image_bytes)
    i = mpimg.imread(image_buf, format='jpg')
    plt.imshow(i, interpolation='nearest')
    plt.show()


if __name__ == "__main__":
    # img = Image(filename="img0",
    #             raw_image="5",
    #             processed_images = {},
    #             metrics ={})
    # img.save()
    #
    # for i in Image.objects.raw({}):
    #     print(i)
    #     print(i.filename)
    #     print(i.processed_images)
    filepath = "./cat.jpg"
    encoded = encode_image_as_b64(filepath)
    print(encoded)
    decode_b64_image(encoded)