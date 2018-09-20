#!/usr/bin/python
# -*- coding: UTF-8 -*-
#根据opencv的识别库进行人的正脸的识别

import face_recognition
import cv2
import os
import sys
import gridfs
import datetime
#import glob2 as gb
import json
import time
from skimage import io
from pymongo import MongoClient
import ConfigParser
from cStringIO import StringIO
import numpy as np
from PIL import Image
import base64

class face_recognize:

    db_ip = ""
    db_port = 0
    db_user = ""
    db_passwd = ""
    db_name = "" 
    db = None
    scaleFactor = 0
    minNeighbors = 0
    minSize = 0
    tolerance = 0
   
    known_face_names=[]
    known_face_encodings=[]   
    mycode = ""

    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")

    def __init__(self, mycode):
       
        config = ConfigParser.ConfigParser()
        config.readfp(open(("./config.ini"), "rb"))
        self.db_ip = config.get("mongodb", "ip")
        self.db_port = config.getint("mongodb", "port")
        self.db_name = config.get("mongodb", "dbname")                
        self.db_user = config.get("mongodb", "user")
        self.db_passwd = config.get("mongodb", "passwd")
        self.scaleFactor = config.getfloat("face_recognize", "scaleFactor")       
        self.minNeighbors = config.getint("face_recognize", "minNeighbors")
        self.tolerance = config.getfloat("face_recognize", "tolerance")

        self.minSize = config.getint("face_recognize", "minSize")
        self.mycode = mycode
        self.loadKnownFaces()       

    def connect(self):   
        client = MongoClient(self.db_ip, self.db_port)
        db = client[self.db_name]
        db.authenticate(self.db_user,self.db_passwd)
        return db

    #由数据库来导入已知人像库的数据,根据mycode来导入本单位的人脸库，格式是:known_mycode_名称_时间戳.jpg；

    def loadKnownFaces(self):

        if self.db == None:
            self.db = self.connect()
            #print("connect to mongodb...")   

	imgfs = gridfs.GridFS(self.db)

	regexstr = "^known_"+self.mycode+"_"

	sql = {"filename": {"$regex": regexstr}}

        result = imgfs.find(sql)

	for r in result:

	    sf = r.name.split("_")
            img_str = r.read()
            nparr = np.fromstring(img_str, np.uint8)
            image = cv2.imdecode(nparr, cv2.COLOR_BGR2GRAY)
            someone_img = face_recognition.face_locations(image)
            someone_face_encoding = face_recognition.face_encodings(image, someone_img)[0] 
            self.known_face_names.append(sf[2])
            self.known_face_encodings.append(someone_face_encoding) 

    #对于新加入库中的人脸进行加载

    def joinNewFaces(self, filename, facename):

        if self.db == None:
            self.db = self.connect()
            #print("connect to mongodb...")   

	imgfs = gridfs.GridFS(self.db)

        nfilename = filename.replace("unknown", "known")
        nfilename = nfilename.replace("none", facename) 
	sql = {"filename": nfilename}

        result = imgfs.find(sql)

	for r in result:

            img_str = r.read()
            sf = r.name.split("_")
	    nparr = np.fromstring(img_str, np.uint8)
            image = cv2.imdecode(nparr, cv2.COLOR_BGR2GRAY)
            someone_img = face_recognition.face_locations(image)
            someone_face_encoding = face_recognition.face_encodings(image, someone_img)[0] 
            self.known_face_names.append(sf[2])
            self.known_face_encodings.append(someone_face_encoding) 
            break

    def getImage(self, imgurl):      
        image = io.imread(imgurl)
        #image = cv2.imread(imgurl)
        return image

    def getFace(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = self.faceCascade.detectMultiScale(
          gray,
          scaleFactor=self.scaleFactor,
          minNeighbors=self.minNeighbors,
          minSize=(self.minSize, self.minSize)    
                #flags = cv2.CV_HAAR_SCALE_IMAGE
        )       

        return faces

    #对于图像中的提取的人脸与库中的标本进行处理；   
    def saveUnknownFace(self, faces):

        if len(faces) == 0:
            return
	collactionname = "unknownface" 

	if self.db == None:
            self.db = self.connect()
            #print("connect to mongodb...")

	imgfs = gridfs.GridFS(self.db)

        for face in faces:
	    try: 
                fname = "unknown_"+self.mycode+"_none_"+str(self.getTimeStamp())+".jpg"
                img_encode = cv2.imencode('.jpg', face)[1]
                data_encode = np.array(img_encode)
                data = data_encode.tostring()
                imgfs.put(data, content_type = "jpg", filename =fname)
            except Exception as e:
                print e

    #取时间戳；   
    def getTimeStamp(self):
        millis = int(round(time.time() * 1000000))     
        return millis

    #对于图像中的提取的人脸与库中的标本进行处理；   
    def recognize(self, image, faces):

        mm = 0
        unmatch = []
        match_face = [] 
        mint = 0
        imgBase64 = []

        for (x, y, w, h) in faces:

            cropImg = image[y:y+h, x:x+w]
            rgb_small_frame=cropImg[:,:,::-1]

            img_encode = cv2.imencode('.jpg', rgb_small_frame)[1]
            data_encode = np.array(img_encode)
            str_encode = data_encode.tostring()
            imgBase64.append(base64.b64encode(str_encode))
            mm = mm+1

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            face_names = []

            for mface in face_encodings:

                match = face_recognition.compare_faces(self.known_face_encodings, mface, tolerance=self.tolerance)

                cute_clock = datetime.datetime.now()

                if True in match:
                    match_index=match.index(True)
                    print ("find face:"+self.known_face_names[match_index]+':'+str(cute_clock))
                    print "recognize face: [ "+self.known_face_names[match_index] +" ]"
                    name = "match"
                    mface = {}
                    mface["face"] = self.known_face_names[match_index] 
                    match_face.append(mface)
                    mint = mint + 1
                else:
                    unmatch.append(cropImg)   
        self.saveUnknownFace(unmatch)

        return "{\"status\":1, \"faces\":"+str(len(faces))+", \"recognize\": "+str(mint)+", \"identify\":"+json.dumps(match_face)+", \"info\":\"Find "+str(len(faces))+" face\"}"
        

    #人像识别的主入口程序
    def faceRecognize(self, imgurl):

        image = self.getImage(imgurl)

        if image == None:
            return "{\"status\":-1, \"faces\":0, \"recognize\": 0, \"identify\":[], \"info\": \"Get Image Error! \"}"

        faces = self.getFace(image)
        if len(faces) == 0:
            return "{\"status\":1, \"faces\":0, \"recognize\": 0, \"identify\":[], \"info\": \"no face\"}"

        return self.recognize(image, faces)

if __name__== '__main__': 

    face_recognize = face_recognize(sys.argv[2])
    ret = face_recognize.faceRecognize(sys.argv[1])

