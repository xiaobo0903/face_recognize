环境：
ubuntu16中安装程序

安装python环境，python2.7.12
安装pip工具：apt install python-pip
安装python所需的工具：
pip pymongo //对于mongo的访问包

建立访问数据库(mongodb):face_recognize
建立数据库的帐户：

db.createUser({user:"dbuser", pwd:"dbpwd", roles:["readWrite", "dbAdmin"]})
可查看congfig.ini中的配置内容

安装flask: pip install flask
安装CMake: pip install CMake
安装scikit-image: apt install python-skimage
安装face_recognition: pip install face_recognition
安装numpy: pip install numpy
安装cv2: pip install python-opencv

运行: python face.py

验证:

识别人像：
http://ip/face/recognize?imgurl=urlencode(imgurl)    

查询人像(注册库):
http://ip/face/getknownface
查询人像(未注册):
http://ip/face/getunknownface

注册人像：
http://ip/face/registe?filename=unknown_aaa_none_999999.jpg&facename=郭德纲
