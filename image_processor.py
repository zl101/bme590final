import io
import base64
import datetime
import numpy as np
from pymodm import connect
from pymodm import MongoModel, fields
from flask import Flask, jsonify, request
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from skimage import data, exposure, img_as_float

app = Flask(__name__)

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")


class User(MongoModel):
    username = fields.CharField(primary_key=True)
    imgslist = fields.ListField()


def histogram_equalize(image):
    nim = exposure.equalize_hist(image)
    nim = 256*nim
    nim = nim.astype(np.uint8)
    return encode_image_no_path(nim)


def contrast_stretch(image, args):
    return 0


def log_compress(image, args):
    return 0


def reverse_video(image, args):
    return 0


def validateNewUser(input):
    """
    -1 for invalid, 0 for already exists, 1 for ur gucci
    """
    if(not isinstance(input, type({}))):
        return -1
    if "username" not in input.keys():
        return -1
    if(not isinstance(input["username"], type("a"))):
        return -1
    checkUserExist = User.objects.raw({"_id": input['username']}).count()
    if(checkUserExist == 0):
        return 1
    else:
        return 0


def validateNewImage(input):
    if(not isinstance(input, type({}))):
        return -1
    if "username" not in input.keys():
        return -1
    if "filename" not in input.keys():
        return -1
    if "filetype" not in input.keys():
        return -1
    if "filedata" not in input.keys():
        return -1
    if "dimensions" not in input.keys():
        return -1
    return 1



@app.route("/api/process_image", methods=["POST"])
def process_image():
    # Histogram Equalization [default]
    # Contrast Stretching
    # Log Compression
    # Reverse Video
    """
    Needs filename, method, method_args, username
    """
    r = request.get_json()
    # validate json, parse json
    usertoprocess = User.objects.raw({"_id": username}).first()
    for k in usertoprocess.imgslist:
        if k == "":
            continue
        if k['filename'] == r['filename']:
            whichim = k
            imstr = k['imstring']
            image = decode_b64_image(imstr, k['filetype'], k['dimensions'])
            break
    # raw_img = image_to_process.raw_image
    if method.lower() == "histogram equalization":
        processed = histogram_equalize(image)
    elif method.lower() == "contrast stretching":
        processed = contrast_stretch(raw_img, method_args)
    elif method.lower() == "log compression":
        processed = log_compress(raw_img, method_args)
    elif method.lower() == "reverse video":
        processed = reverse_video(raw_img, method_args)
    else:
        return -1
    whichim["processeddict"][method.lower()] = [processed,
                                                datetime.datetime.now()]
    usertoprocess.save()


if __name__ == "__main__":
    app.run(host="127.0.0.1")
