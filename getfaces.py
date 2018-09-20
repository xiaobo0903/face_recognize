#!/usr/bin/python
# -*- coding: UTF-8 -*-
#对于库中的内容进行查询, 按天进行查询

import os
import sys
import gridfs
import datetime
import json
import time
from pymongo import MongoClient
import pymongo
import ConfigParser
import base64

class getfaces:

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

    def getFaceList(self, page, flag):

        if self.db == None:
            self.db = self.connect()
            #print("connect to mongodb...")   

        regexstr = ""

        if flag == 1:
           regexstr = "^known_"+self.mycode+"_"
        else:
           regexstr = "^unknown_"+self.mycode+"_"

        sql = {"filename": {"$regex": regexstr}} 

        imgfs = gridfs.GridFS(self.db)

        #result = imgfs.find(sql).sort({"uploadDate":-1}).skip(10*page).limit(10)
        result = imgfs.find(sql).sort("uploadDate",pymongo.DESCENDING).skip(10*page).limit(10)

	stmp = ""

        for r in result:
	    dic = {}
	    ls_f=base64.b64encode(r.read())
            dic["name"] = r.name
            dic["date"] = r.upload_date.strftime("%Y-%m-%d %H:%M:%S")
            dic["img"] = ls_f

            if stmp == "":
                stmp = stmp+json.dumps(dic)
            else:
                stmp = stmp +","+json.dumps(dic)

        stmp = "["+stmp+"]"
        print stmp
        return stmp

if __name__== '__main__': 


     list = getfaces("aaaaa")
     list.getFaceList(0)
