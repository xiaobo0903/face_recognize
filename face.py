#!/usr/bin/python
# -*- coding: UTF-8 -*-
#web main
from flask import Flask, request, jsonify
from face_recognize import *
from face_registe import *
from getfaces import *
import urllib
import json
from flask import render_template


app = Flask(__name__)

face_recognize = face_recognize("aaaaa")
face_registe = face_registe("aaaaa")
gfaces = getfaces("aaaaa")


#对于imgurl需要进行encode编码，否则会出错！
@app.route('/face/recognize', methods=['post','get'])
def recignize():
    p = request.args.get('imgurl')

    if p == None:
    	return jsonify({'t': p})

    imgurl = urllib.unquote(p)
    ret = face_recognize.faceRecognize(imgurl)  
    return jsonify(ret)

@app.route('/face/registe', methods=['post','get'])
def registe():

    filename = request.args.get("filename")
    if filename == None:
    	return jsonify({'t1': filename})

    name = request.args.get("facename")
    if name == None:
    	return jsonify({'t2': name})

    ret = face_registe.registeKnownface(filename, name)  
    face_recognize.joinNewFaces(filename, name)
    return jsonify(ret)

@app.route('/face/getknownfaces', methods=['post','get'])
def getknownfaces():

    page = request.args.get("page")
    if page == None:
    	page = 0
    ret = gfaces.getFaceList(int(page), 1)  
    return render_template("facelist.html",
        title = 'Home',
        faces = json.loads(ret))

@app.route('/face/getunknownfaces', methods=['post','get'])
def getunknownfaces():

    page = request.args.get("page")
    if page == None:
        page = 0
    ret = gfaces.getFaceList(int(page), 0)
    return render_template("facelist.html",
        title = 'Home',
        faces = json.loads(ret)) 

@app.errorhandler(404)
def not_found(error):
    return

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
