from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, \
    QAction, QLineEdit, QMessageBox, \
    QFileDialog, QComboBox
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import numpy as np
import io
import base64
import datetime
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from pymodm import connect
from pymodm import MongoModel, fields
import zipfile
import os
from matplotlib.pyplot import figure
import logging

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")


def detectFname(path):
    """
    Parses filepath for the filename

    :returns filename
    """
    loc = path.rfind("/")
    if (loc == -1):
        return path
    else:
        return path[loc + 1:]


def detectFilePathNoName(path):
    """
    Parses filepath for the filepath without the file name ending

    :returns path string
    """
    loc = path.rfind("/")
    if (loc == -1):
        return loc
    else:
        return path[0:loc + 1]


def detectFtype(path):
    """
    Parses filepath for the type of file

    :returns filetype
    """
    loc = path.rfind(".")
    if (loc == -1):
        return loc
    else:
        return path[loc:]


def getRawName(path):
    """
    Given a filename with no path before it, returns just the name, no type

    :returns filename
    """
    loc = path.rfind(".")
    if loc == -1:
        return loc
    else:
        return path[0:loc]


def constructImg(uploadTime, fileName, imgString, fileType, dimensions):
    """
    Creates Image Struct
    """
    toret = {}
    toret['uploadtime'] = uploadTime
    toret['filename'] = fileName
    toret['imgstring'] = imgString
    toret['processeddict'] = {}
    toret['filetype'] = fileType
    toret["dimensions"] = dimensions
    return toret


def encode_image_as_b64_wmetrics(image_path):
    """
    Encodes imagepath to 64b with metrics like name, type, and dimensions

    :returns list of metrics as well as encoding
    """
    imname = detectFname(image_path)
    img = np.asarray(Image.open(image_path))
    shape = img.shape
    imtype = detectFtype(image_path)
    return [imname, imtype, shape, base64.b64encode(img).decode()]


def decode_b64_image_helper(base64_string, format, dimensions):
    """
    Helper Function for decode
    """
    decode = base64.b64decode(base64_string)
    res = np.frombuffer(decode, dtype=np.uint8)
    return np.reshape(res, dimensions)


def decode_image_fromb64(imstring, format, shape):
    """
    Decodes image string into numpy image

    :returns nd array image of dtype uint8
    """
    imbytes = imstring.encode()
    decoded = decode_b64_image_helper(imbytes, format, shape)
    return decoded


def validateNewUser(input):
    """
    -1 for invalid, 0 for already exists, 1 for ur gucci
    """
    checkUserExist = User.objects.raw({"_id": input}).count()
    if (checkUserExist == 0):
        return 1
    else:
        return 0


def fetchDbHelper(list, filename, processing):
    """
    Helper function to fetch useful image traits stored in db
    """
    saveupload = ""
    saveshape = ""
    numtimes = ""
    howlong = ""
    decodedim = ""
    for k in list:
        if k == "":
            continue
        if k['filename'] == filename:
            # imdata = k['imgstring']
            if processing == 'none':
                decodedim = decode_image_fromb64(k['imgstring'], k['filetype'],
                                                 k['dimensions'])
                saveshape = str(k['dimensions'])
                saveupload = k['uploadtime'].strftime("%Y-%m-%d %H:%M:%S")
            else:
                if processing not in k['processeddict'].keys():
                    break
                temp = k['processeddict'][processing]
                decodedim = decode_image_fromb64(temp[0], k['filetype'],
                                                 k['dimensions'])
                saveshape = str(k['dimensions'])
                saveupload = temp[1].strftime("%Y-%m-%d %H:%M:%S")
                numtimes = temp[3]
                howlong = temp[2]
    return [decodedim, saveshape, saveupload, numtimes, howlong]


def upload_image(user, filename, filetype, dimensions, filedata):
    """
    Needs fields filename, filedata, username, filetype, dimensions

    Constructs and then uploads image to appropriate user obj in db

    :returns 1 for funsies
    """
    testcount = User.objects.raw({"_id": user}).count()
    if testcount == 0:
        return
    newim = constructImg(datetime.datetime.now(),
                         filename,
                         filedata,
                         filetype,
                         dimensions)
    user_call = User.objects.raw({"_id": user}).first()
    counter = 0
    for k in user_call.imgslist:
        if k == "":
            continue
        if k['filename'] == filename:
            del user_call.imgslist[counter]
        counter = counter + 1
    user_call.imgslist.append(newim)
    user_call.save()
    return 1


def showIM(username, filename, processing):
    """
    Displays image as specified in filename

    :returns doesn't return lul
    """
    testcount = User.objects.raw({"_id": username}).count()
    if testcount == 0:
        return -1
    user_call = User.objects.raw({"_id": username}).first()
    ret = fetchDbHelper(user_call.imgslist, filename, processing)
    if ret[1] == "":
        return -1
    decodedim = ret[0]
    saveupload = ret[2]
    saveshape = ret[1]
    numtimes = ret[3]
    howlong = ret[4]
    plt.imshow(decodedim)
    plt.title(saveupload + "  " + saveshape)
    if howlong != "":
        plt.xlabel("runtime: " + str(howlong) + " | numtimes:" + str(numtimes))
    plt.show()


def downloadIM(username, filename, fileformat, processing):
    """
    Downloads specified image in given format

    Idk what to do for zip lol
    """
    testcount = User.objects.raw({"_id": username}).count()
    if testcount == 0:
        return
    user_call = User.objects.raw({"_id": username}).first()
    ret = fetchDbHelper(user_call.imgslist, filename, processing)
    if ret[1] == "":
        return -1
    decodedim = ret[0]
    saveupload = ret[2]
    saveshape = ret[1]
    numtimes = ret[3]
    howlong = ret[4]
    tosave = Image.fromarray(decodedim)
    if fileformat == ".jpg":
        tosave = tosave.convert("RGB")
    savestring = getRawName(filename) + datetime.datetime.now().strftime(
        "%Y%m%d%H%M%S") + fileformat
    # print(savestring)
    # f = io.BytesIO()
    tosave.save(savestring)
    return 1


def showHI(username, filename, processing):
    """
    Displays histogram of given image
    """
    testcount = User.objects.raw({"_id": username}).count()
    if testcount == 0:
        return
    user_call = User.objects.raw({"_id": username}).first()
    ret = fetchDbHelper(user_call.imgslist, filename, processing)
    if ret[1] == "":
        return -1
    decodedim = ret[0]
    plt.hist(np.reshape(decodedim, (-1, 1)), bins=256, range=(0.0, 255.0))
    plt.title("histogram")
    plt.show()


def compareIM(username, filename1, processing1, filename2, processing2):
    """
    compares two selected images
    """
    testcount = User.objects.raw({"_id": username}).count()
    if testcount == 0:
        return
    user_call = User.objects.raw({"_id": username}).first()
    ret = fetchDbHelper(user_call.imgslist, filename1, processing1)
    if ret[1] == "":
        return -1
    decodedim1 = ret[0]
    saveupload1 = ret[2]
    saveshape1 = ret[1]
    numtimes1 = ret[3]
    howlong1 = ret[4]
    ret2 = fetchDbHelper(user_call.imgslist, filename2, processing2)
    if ret2[1] == "":
        return -1
    decodedim2 = ret2[0]
    saveupload2 = ret2[2]
    saveshape2 = ret2[1]
    numtimes2 = ret2[3]
    howlong2 = ret2[4]
    figure(num=None, figsize=(12, 8))
    plt.subplot(1, 2, 1)
    plt.imshow(decodedim1)
    plt.title(saveupload1 + "  " + saveshape1)
    if howlong1 != "":
        plt.xlabel(
            "runtime: " + str(howlong1) + " | numtimes:" + str(numtimes1))
    plt.subplot(1, 2, 2)
    plt.imshow(decodedim2)
    plt.title(saveupload2 + "  " + saveshape2)
    if howlong2 != "":
        plt.xlabel(
            "runtime: " + str(howlong2) + " | numtimes:" + str(numtimes2))
    plt.show()


class User(MongoModel):
    username = fields.CharField(primary_key=True)
    imgslist = fields.ListField()
    loginhist = fields.ListField()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Hello, world!'
        self.left = 290
        self.top = 200
        self.width = 800
        self.height = 800
        self.files = []
        self.user = ""
        self.tozip = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.textbox = QLineEdit(self)
        self.textbox.move(30, 30)
        self.textbox.setText("Username Field")
        self.textbox2 = QLineEdit(self)
        self.textbox2.move(30, 120)
        self.textbox2.setText("Filename Field 1")
        self.textbox.resize(280, 40)
        self.textbox2.resize(280, 40)
        self.textbox3 = QLineEdit(self)
        self.textbox3.move(30, 210)
        self.textbox3.setText("Filename Field 2")
        self.textbox3.resize(280, 40)
        self.button = QPushButton('Set or Create User', self)
        self.button.move(30, 400)
        self.button.clicked.connect(self.callCreateUser)
        self.button2 = QPushButton('Add Image', self)
        self.button2.move(400, 400)
        self.button2.clicked.connect(self.callAddImage)
        self.button3 = QPushButton('Upload Added Images', self)
        self.button3.move(30, 500)
        self.button3.clicked.connect(self.callProcessImages)
        self.comboBox = QComboBox(self)
        self.comboBox.addItem("none")
        self.comboBox.addItem("histogram equalization")
        self.comboBox.addItem("contrast stretching")
        self.comboBox.addItem("log compression")
        self.comboBox.addItem("reverse video")
        self.comboBox.addItem("gamma correction")
        self.comboBox.move(350, 125)
        self.comboBox2 = QComboBox(self)
        self.comboBox2.addItem("none")
        self.comboBox2.addItem("histogram equalization")
        self.comboBox2.addItem("contrast stretching")
        self.comboBox2.addItem("log compression")
        self.comboBox2.addItem("reverse video")
        self.comboBox2.addItem("gamma correction")
        self.comboBox2.move(350, 215)
        self.comboBox3 = QComboBox(self)
        self.comboBox3.addItem(".jpg")
        self.comboBox3.addItem(".png")
        self.comboBox3.addItem(".tif")
        self.comboBox3.move(600, 600)
        self.button4 = QPushButton('Do IM Processing', self)
        self.button4.move(400, 500)
        self.button4.clicked.connect(self.callExternalProcessing)
        self.button5 = QPushButton('Show Image', self)
        self.button5.move(30, 600)
        self.button5.clicked.connect(self.showImage)
        self.button7 = QPushButton('Save Image', self)
        self.button7.move(400, 600)
        self.button7.clicked.connect(self.downloadImage)
        self.button8 = QPushButton('Show Histogram', self)
        self.button8.move(30, 700)
        self.button8.clicked.connect(self.showHistogram)
        self.button9 = QPushButton('Compare Images', self)
        self.button9.move(400, 700)
        self.button9.clicked.connect(self.compareImages)
        self.button10 = QPushButton('Show Time On', self)
        self.button10.move(350, 30)
        self.button10.clicked.connect(self.showMetrics1)
        self.button11 = QPushButton('Show Time Since Creation', self)
        self.button11.move(575, 30)
        self.button11.clicked.connect(self.showMetrics2)
        self.button12 = QPushButton('Add to Zip', self)
        self.button12.move(30, 300)
        self.button12.clicked.connect(self.addToZip)
        self.button13 = QPushButton('Save Zip', self)
        self.button13.move(150, 300)
        self.button13.clicked.connect(self.saveZip)
        self.button.resize(200, 30)
        self.button2.resize(200, 30)
        self.button3.resize(200, 30)
        self.button4.resize(200, 30)
        self.button5.resize(200, 30)
        self.button7.resize(200, 30)
        self.button8.resize(200, 30)
        self.button9.resize(200, 30)
        self.button10.resize(200, 30)
        self.button11.resize(200, 30)
        self.comboBox.resize(200, 30)
        self.comboBox2.resize(200, 30)
        # self.imlabel = Qlabel(self)

        self.show()

    # @pyqtSlot()
    def callCreateUser(self):
        """
        Creates a user, first validating it, then writes it to db
        """
        username = self.textbox.text()
        check = validateNewUser(username)
        msg = ""
        if (check == -1):
            msg = "Invalid"
        if (check == 0):
            msg = "User Set (Already Exists)"
            self.user = username
            user_call = User.objects.raw({"_id": username}).first()
            user_call.loginhist[1] = datetime.datetime.now()
            user_call.save()
        if check == 1:
            cpy = datetime.datetime.now()
            u = User(username=username, imgslist=[""],
                     loginhist=[cpy, cpy])
            u.save()
            msg = "User Created"
            self.user = username
        QMessageBox.question(self, 'Message!', msg, QMessageBox.Ok,
                             QMessageBox.Ok)

    def callAddImage(self):
        fileName, _ = QFileDialog.getOpenFileNames(self, 'Single File',
                                                   QtCore.QDir.rootPath(),
                                                   '*.jpg;*.png;*.tif;*.zip')
        for k in fileName:
            self.files.append(k)
        QMessageBox.question(self, 'Message!', "Image(s) Added to List",
                             QMessageBox.Ok, QMessageBox.Ok)

    def callProcessImages(self):
        """
        Helper function that uploads images and adds desired metrics
        """
        for filepath in self.files:
            prepend = 0
            if (detectFtype(filepath) == '.zip'):
                prepend = prepend + 1
                mypath = detectFilePathNoName(filepath)
                ndir = mypath + str(
                    prepend) + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                with zipfile.ZipFile(filepath, "r") as zip_ref:
                    zip_ref.extractall(ndir)
                for j in os.listdir(ndir):
                    nfile = mypath + j
                    self.files.append(nfile)
            else:
                temp = encode_image_as_b64_wmetrics(filepath)
                upload_image(self.user, temp[0], temp[1], temp[2], temp[3])
        self.files = []

    def downloadImage(self):
        """
        Handler Function
        """
        downloadIM(self.user, self.textbox2.text(),
                   self.comboBox3.currentText(), self.comboBox2.currentText())
        logging.info("Image(s) downloaded")

    def showImage(self):
        """
        Handler Function
        """
        showIM(self.user, self.textbox2.text(), self.comboBox.currentText())
        # r= requests.post("http://127.0.0.1:5000/api/upload_image",
        # json={"username":"chris", "filename":fname})

    def showHistogram(self):
        """
        Handler Function
        """
        showHI(self.user, self.textbox2.text(), self.comboBox.currentText())

    def callExternalProcessing(self):
        """
        Handler Function
        """
        processingtype = self.comboBox.currentText()
        imname = self.textbox2.text()
        r = requests.post("http://vcm-7452.vm.duke.edu:5000/api/im_processing",
                          json={"username": self.user, "filename": imname,
                                "processing": processingtype})
        response = r.status_code
        if response == 500:
            logging.error(r.text)
        elif response == 200:
            logging.info("Image Processed")
        else:
            logging.error("Unexpected Error")
            logging.error(r.text)

    def compareImages(self):
        """
        Handler function
        """
        in1 = self.textbox2.text()
        in2 = self.comboBox.currentText()
        in3 = self.textbox3.text()
        in4 = self.comboBox2.currentText()
        compareIM(self.user, in1, in2, in3, in4)

    def showMetrics1(self):
        """
        Shows how long a user has been signed in
        """
        username = self.user
        testcount = User.objects.raw({"_id": username}).count()
        if testcount == 0:
            return
        user_call = User.objects.raw({"_id": username}).first()
        toshow = ""
        timeon = datetime.datetime.now() - user_call.loginhist[1]
        QMessageBox.question(self, 'Message!', str(timeon),
                             QMessageBox.Ok, QMessageBox.Ok)

    def showMetrics2(self):
        """
        Shows how long a user has been active
        """
        username = self.user
        testcount = User.objects.raw({"_id": username}).count()
        if testcount == 0:
            return
        user_call = User.objects.raw({"_id": username}).first()
        toshow = ""
        created = datetime.datetime.now() - user_call.loginhist[0]
        QMessageBox.question(self, 'Message!', str(created),
                             QMessageBox.Ok, QMessageBox.Ok)

    def saveZip(self):
        """
        Saves to zip selected files
        """
        username = self.user
        testcount = User.objects.raw({"_id": username}).count()
        if testcount == 0:
            return
        user_call = User.objects.raw({"_id": username}).first()
        inputlist = user_call.imgslist
        with zipfile.ZipFile('spam.zip', 'w') as myzip:
            for k in self.tozip:
                filename = k[0]
                ptype = k[1]
                ret = fetchDbHelper(inputlist, filename, ptype)
                decodedim = ret[0]
                saveupload = ret[2]
                saveshape = ret[1]
                numtimes = ret[3]
                howlong = ret[4]
                if saveupload == "":
                    continue
                tosave = Image.fromarray(decodedim)
                fileformat = detectFtype(filename)
                savestring = getRawName(filename) \
                             + datetime.datetime.now().strftime("%Y%m%d%H%M%S") \
                             + fileformat
                tosave.save(savestring)
                with open(savestring, "rb") as image_file:
                    encodedim = base64.b64encode(image_file.read())
                image_bytes = base64.b64decode(encodedim)
                image_buf = io.BytesIO(image_bytes)
                myzip.writestr(savestring, image_buf.read())
        self.tozip = []

    def addToZip(self):
        toadd = [self.textbox2.text(), self.comboBox.currentText()]
        self.tozip.append(toadd)


if __name__ == '__main__':
    logging.basicConfig(filename="applog.txt",
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
