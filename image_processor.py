import io
import base64
import datetime
from pymodm import connect
from pymodm import MongoModel, fields
from flask import Flask, jsonify, request
from matplotlib import pyplot as plt
import matplotlib.image as mpimg


app = Flask(__name__)

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")

class Image(MongoModel):
    filename = fields.CharField(primary_key=True)
    raw_image = fields.CharField()
    processed_images = fields.ListField()
    metrics = fields.DictField()
    timestamp = fields.DateTimeField()


def encode_image_as_b64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read())


def decode_b64_image(base64_string, format):
    image_bytes = base64.b64decode(base64_string)
    image_buf = io.BytesIO(image_bytes)
    i = mpimg.imread(image_buf, format=format)
    plt.imshow(i, interpolation='nearest')
    plt.show()


def histogram_equalize(image, args):
    return 0


def contrast_stretch(image, args):
    return 0


def log_compress(image, args):
    return 0


def reverse_video(image, args):
    return 0


@app.route("/api/upload_image/", methods=["POST"])
def upload_image(filename, filepath):
    image_encoded = encode_image_as_b64(filepath)
    img = Image(filename=filename,
                raw_image=image_encoded,
                processed_images = {},
                metrics ={},
                timestamp = datetime.datetime.now())
    img.save()


@app.route("/api/process_image/", methods=["POST"])
def process_image(filename, method, method_args):
    #Histogram Equalization [default]
    #Contrast Stretching
    #Log Compression
    #Reverse Video
    image_to_process = Image.objects.raw({"_id": filename}).first()
    raw_img = image_to_process.raw_image
    if method.lower() == "Histogram Equalization":
        processed = histogram_equalize(raw_img, method_args)
    elif method.lower() == "Contrast Stretching":
        processed = contrast_stretch(raw_img, method_args)
    elif method.lower() == "Log Compression":
        processed = log_compress(raw_img, method_args)
    elif method.lower() == "Reverse Video":
        processed = reverse_video(raw_img, method_args)
    else:
        return -1
    temp = image_to_process.processed_images
    temp.append([processed, method, datetime.datetime.now()])
    image_to_process.processed_images = temp
    image_to_process.save()


if __name__ == "__main__":
    app.run(host="127.0.0.1")
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

    # filepath = "./cat.jpg"
    # encoded = encode_image_as_b64(filepath)
    # print(encoded)
    # decode_b64_image(encoded)
    #r2 = requests.post("http://bme590.suyash.io/sum", json={"a": 1, "b": 2})