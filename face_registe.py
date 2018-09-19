#!/usr/bin/python
# -*- coding: UTF-8 -*-
#根据opencv的识别库进行人的正脸的识别

import sys
from pymongo import MongoClient
import ConfigParser
from cStringIO import StringIO

class face_registe:

    db_ip = ""
    db_port = 0
    db_user = ""
    db_passwd = ""
    db_name = "" 
    db = None
   
    mycode = ""


    def __init__(self, mycode):
       
        config = ConfigParser.ConfigParser()
        config.readfp(open(("./config.ini"), "rb"))
        self.db_ip = config.get("mongodb", "ip")
        self.db_port = config.getint("mongodb", "port")
        self.db_name = config.get("mongodb", "dbname")                
        self.db_user = config.get("mongodb", "user")
        self.db_passwd = config.get("mongodb", "passwd")
        self.mycode = mycode

    def connect(self):   
        client = MongoClient(self.db_ip, self.db_port)
        db = client[self.db_name]
        db.authenticate(self.db_user,self.db_passwd)
        return db

    #由数据库来导入已知人像库的数据,根据mycode来导入本单位的人脸库，格式是:known_mycode_名称_时间戳.jpg；

    def registeKnownface(self, filename, facename):

	print filename + "_" + facename
        if self.db == None:
            self.db = self.connect()
            #print("connect to mongodb...")   
        collactionname = "fs.files" 
        collection = self.db[collactionname]
	nfilename = filename.replace("unknown", "known")
        nfilename = nfilename.replace("none", facename)
	
        result = collection.update({"filename": filename}, {"$set":{"filename": nfilename}}) 

        print result
	if result["updatedExisting"]:
	    return "{'status':'1', 'info':'update succeeded!'}"
        else:
            return "{'status':'-1', 'info':'update failed!'}"

if __name__== '__main__': 


     face = face_registe("aaaaa")
     face.registeKnownface(sys.argv[1], sys.argv[2])
