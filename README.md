# bme590final
EH158 ZL101, Image Processing
## Summary of Functionalities
+ Tracks files and actions for every single user
+ Allows image upload, image processing, and image display services
+ Image processing tasks supported include Histogram Equalization, Contrast Stretching, Log Compression, Reverse Video, and Gamma Correction
+ Supports .jpg, .png, and .tiff image file formats;  files can also be saved in a .zip file
+ Stores timestamps of image uploads, information on user logins, and latency in calling image processing tasks
## How to Use
+ For a walkthrough of the application, please refer to the shareable link on google drive or to the notes; both of these are listed below
## To Run
+ Use Python 3, install requirements
+ Run python app.py to start up the app
## Detailed Notes
+ First you enter a username in the field that says username
+ Then click set or create user
+ Then click add image, this will prompt you to select some images to be added
+ after you have selected, click uploaded added images to upload to db
+ Type the name of an image you have uploaded, case sensitive and with the .png at the end, in the filename field 1
+ Click show image to see the image
+ At the top of the image we show the dimensions as well as when it was uploaded
+ Now in the dropdown next to field 1, select the kind of processing you want to do on the image in filename field 1, and click Do IM Processing
+ With the dropdown still selected as the processing you just did, click show image to see the processed version
+ Note that for processed images we show an additional how long it took and how many times its been called at the bottom
+ Click show histogram to see the color histogram of the image as specified in the field 1 and dropdown next to field 1
+ Trying to show a processed version of an image that you haven't yet done will result in nothing happen, same for histogram
+ Do some processing on whatever images you want
+ Use field 2 to enter another filename and processing already done (both field 1 and 2 should be filled out) and click compare images to see the images side by side
+ Save an image as specified in field 1 in the desired format using the save image button and corresponding dropdown
+ Save multiple processed images by first specifying an image in field 1 and appropriate dropdown, and then clicking add to zip. Do this multiple times and when you have added all desired files, click save zip which will save all the images you just added to a zip file
+ for the current user, click show time on to show how long it's been since you signed on
+ for the current user, click show time since creation to show how long it's been since you first created your username
## Links:
+ Video demonstrations: https://drive.google
.com/open?id=1f1ifNnkn_FP88YFaNwRF4YtoYpvYbcN_
+ Server URL: http://vcm-7452.vm.duke.edu:5000
## Build status:

[![Build Status](https://travis-ci.org/zl101bme590final.svg?branch=master)](https://travis-ci.org/zl101/bme590final)
