from PyQt5.QtWidgets import QMainWindow,QApplication,QWidget,QPushButton,QAction,QLineEdit,QMessageBox, QFileDialog, QComboBox
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

connect("mongodb://daequan:360oogabooga@ds119151.mlab.com:19151/bme590finaldb")


def detectFname(path):
    """
    Parses filepath for the filename

    :returns filename
    """
    loc = path.rfind("/")
    if(loc == -1):
        return path
    else:
        return path[loc+1:]


def detectFilePathNoName(path):
    """
    Parses filepath for the filepath without the file name ending

    :returns path string
    """
    loc = path.rfind("/")
    if(loc == -1):
        return loc
    else:
        return path[0:loc+1]


def detectFtype(path):
    """
    Parses filepath for the type of file

    :returns filetype
    """
    loc = path.rfind(".")
    if(loc == -1):
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
    if(checkUserExist == 0):
        return 1
    else:
        return 0


def upload_image(user, filename, filetype, dimensions, filedata):
    """
    Needs fields filename, filedata, username, filetype, dimensions

    Constructs and then uploads image to appropriate user obj in db

    :returns 1 for funsies
    """
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
        counter = counter + 1;
    user_call.imgslist.append(newim)
    user_call.save()
    return 1


def showIM(username, filename):
    """
    Displays image as specified in filename

    :returns doesn't return lul
    """
    user_call = User.objects.raw({"_id": username}).first()
    saveupload = ""
    saveshape = []
    for k in user_call.imgslist:
        if k == "":
            continue
        if k['filename'] == filename:
            #imdata = k['imgstring']
            decodedim = decode_image_fromb64(k['imgstring'], k['filetype'], k['dimensions'])
            saveshape = str(k['dimensions'])
            saveupload = k['uploadtime'].strftime("%Y-%m-%d %H:%M:%S")
    if saveupload == "":
        return -1
    plt.imshow(decodedim)
    plt.title(saveupload + "  " + saveshape)
    plt.show()


def downloadIM(username, filename, fileformat):
    """
    Downloads specified image in given format

    Idk what to do for zip lol
    """
    testcount = User.objects.raw({"_id": username}).count()
    if testcount == 0:
        return
    user_call = User.objects.raw({"_id": username}).first()
    save = ''
    for k in user_call.imgslist:
        if k == "":
            continue
        if k['filename'] == filename:
            #imdata = k['imgstring']
            save = k['imgstring']
            decodedim = decode_image_fromb64(k['imgstring'], k['filetype'], k['dimensions'])
    #imbytes = save.encode()
    #decode = base64.b64decode(imbytes)
    #plt.imshow(decodedim)
    #plt.show()
    tosave = Image.fromarray(decodedim)
    if fileformat == ".jpg":
        tosave = tosave.convert("RGB")
    savestring = getRawName(filename) + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + fileformat
    #print(savestring)
    #f = io.BytesIO()
    tosave.save(savestring)
    return 1;
    #with zipfile.ZipFile('spam.zip', 'w') as myzip:
    #    myzip.writestr(savestring, tosave.tobytes())


def showHI(username, filename):
    """
    Displays histogram of given image
    """
    user_call = User.objects.raw({"_id": username}).first()
    saveupload = ""
    saveshape = []
    onedim = ''
    for k in user_call.imgslist:
        if k == "":
            continue
        if k['filename'] == filename:
            #imdata = k['imgstring']
            decodedim = decode_image_fromb64(k['imgstring'], k['filetype'], k['dimensions'])
            onedim = k['dimensions'][0]
    plt.hist(np.reshape(decodedim, (-1,1)), bins = 256, range=(0.0, 255.0))
    plt.title("histogram")
    plt.show()


class User(MongoModel):
    username = fields.CharField(primary_key=True)
    imgslist = fields.ListField()
    loginhist = fields.ListField()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title='Hello, world!'
        self.left=290
        self.top=200
        self.width=800
        self.height=800
        self.files = []
        self.user = ""
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.textbox=QLineEdit(self)
        self.textbox.move(30,30)
        self.textbox.setText("Username Field")
        self.textbox2=QLineEdit(self)
        self.textbox2.move(30,120)
        self.textbox2.setText("Filename Field 1")
        self.textbox.resize(280,40)
        self.textbox2.resize(280,40)
        self.textbox3=QLineEdit(self)
        self.textbox3.move(30,210)
        self.textbox3.setText("Filename Field 2")
        self.textbox3.resize(280,40)
        self.button=QPushButton('Set or Create User',self)
        self.button.move(30,400)
        self.button.clicked.connect(self.callCreateUser)
        self.button2=QPushButton('Add Image',self)
        self.button2.move(400,400)
        self.button2.clicked.connect(self.callAddImage)
        self.button3=QPushButton('Upload Added Images',self)
        self.button3.move(30,500)
        self.button3.clicked.connect(self.callProcessImages)
        self.comboBox = QComboBox(self)
        self.comboBox.addItem("A")
        self.comboBox.addItem("B")
        self.comboBox.addItem("C")
        self.comboBox.addItem("D")
        self.comboBox.move(350, 125)
        self.comboBox2 = QComboBox(self)
        self.comboBox2.addItem("A")
        self.comboBox2.addItem("B")
        self.comboBox2.addItem("C")
        self.comboBox2.addItem("D")
        self.comboBox2.move(350, 215)
        self.comboBox3 = QComboBox(self)
        self.comboBox3.addItem(".jpg")
        self.comboBox3.addItem(".png")
        self.comboBox3.addItem(".tif")
        self.comboBox3.move(600, 600)
        self.button4=QPushButton('Do IM Processing',self)
        self.button4.move(400,500)
        self.button4.clicked.connect(self.callExternalProcessing)
        self.button5=QPushButton('Show Image',self)
        self.button5.move(30,600)
        self.button5.clicked.connect(self.showImage)
        self.button6=QPushButton('Test',self)
        self.button6.move(300,350)
        self.button6.clicked.connect(self.on_click)
        self.button7=QPushButton('Save Image',self)
        self.button7.move(400,600)
        self.button7.clicked.connect(self.downloadImage)
        self.button8=QPushButton('Show Histogram',self)
        self.button8.move(30,700)
        self.button8.clicked.connect(self.showHistogram)
        self.button.resize(200,30)
        self.button2.resize(200,30)
        self.button3.resize(200,30)
        self.button4.resize(200,30)
        self.button5.resize(200,30)
        self.button7.resize(200,30)
        self.button8.resize(200,30)
        #self.imlabel = Qlabel(self)

        self.show()
      # @pyqtSlot()
    def callCreateUser(self):
        username = self.textbox.text()
        check = validateNewUser(username)
        msg = ""
        if(check == -1):
           msg = "Invalid"
        if(check == 0):
           msg =  "User Set (Already Exists)"
           self.user = username
           User.objects.raw({"_id":username}).first().loginhist.append(datetime.datetime.now())
        if check==1:
            u = User(username=username, imgslist=[""], loginhist = [datetime.datetime.now()])
            u.save()
            msg =  "User Created"
            self.user = username
        QMessageBox.question(self, 'Message!',msg, QMessageBox.Ok, QMessageBox.Ok)

    def callAddImage(self):
        fileName, _ = QFileDialog.getOpenFileNames(self, 'Single File', QtCore.QDir.rootPath() , '*.jpg;*.png;*.tif;*.zip')
        for k in fileName:
            self.files.append(k)
        QMessageBox.question(self, 'Message!', "Image(s) Added to List",QMessageBox.Ok, QMessageBox.Ok)

    def callProcessImages(self):
        for filepath in self.files:
            prepend = 0
            if(detectFtype(filepath) == '.zip'):
                prepend = prepend + 1
                mypath = detectFilePathNoName(filepath)
                ndir = mypath + str(prepend) + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                with zipfile.ZipFile(filepath,"r") as zip_ref:
                    zip_ref.extractall(ndir)
                for j in os.listdir(ndir):
                    nfile =mypath + j
                    self.files.append(nfile)
            else:
                temp = encode_image_as_b64_wmetrics(filepath)
                upload_image(self.user, temp[0], temp[1], temp[2], temp[3])
        self.files = []

    def downloadImage(self):
        downloadIM(self.user, self.textbox2.text(), self.comboBox3.currentText())

    def showImage(self):
        showIM(self.user, self.textbox2.text())
        #r= requests.post("http://127.0.0.1:5000/api/upload_image", json={"username":"chris", "filename":fname})

    def showHistogram(self):
        showHI(self.user, self.textbox2.text())

    def callExternalProcessing(self):
        print(self.comboBox.currentText())
        #r= requests.post("http://127.0.0.1:5000/api/im_processing", json={"username":"chris", "filename":"cat.jpg", "processing": "histogram equalization"})

    def on_click(self):
        print("nada")

if __name__ == '__main__':
    app=QApplication(sys.argv)
    ex=App()
    sys.exit(app.exec_())