import cv2
import os
import numpy as np
from pathlib import Path
import cvlib as cv
import time
from cv2 import threshold
from cvlib.object_detection import draw_bbox
# from matplotlib.patches import draw_bbox

from flask import Flask , request, render_template , redirect , url_for

from playsound import playsound
# from utils import download_file

from cloudant.client import Cloudant

ACCOUNT_NAME, API_KEY="79628593-233b-4247-b432-61ed8226e146-bluemix","6aWXpKcrTZqjUWu6NeZJXXygl1kk7Q12uVTCVILJQObw"
client=Cloudant.iam(ACCOUNT_NAME, API_KEY, connect=True)

my_database=client.create_database('my_database')
app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/afterreg',methods=['POST'])
def afterreg():
    x=[x for x in request.form.values()]
    print(x)
    data={
        '_id':x[1],
        'name':x[0],
        'psw':x[2]
    }
    # print(data)
    query={'_id':{'$eq':data['_id']}}

    docs=my_database.get_query_result(query)
    # print(docs)

    # print(len(docs.all()))

    if(len(docs.all())==0):
        url=my_database.create_document(data)
        return render_template('register.html',message='Registration Successful, Please login using your details')
    else:
        return render_template('register.html',message="You are alredy a member, please login using your details")
    return "nothing"


@app.route('/login')
def login():
    return render_template('login.html',message="")

@app.route('/afterlogin',methods=['POST'])
def afterlogin():
    x=[x for x in request.form.values()]
    user =x[0]
    passw=x[1]
    # print(user,passw)

    query={'_id':{'$eq':user}}

    docs=my_database.get_query_result(query)

    # print(docs)

    # print(len(docs.all()))


    if(len(docs.all())==0):
        print("login")
        return render_template('login.html',message="The user is not found")
    else:
        # print("holaaaaaaaaaa")
        if((user==docs[0][0]['_id'] and passw==docs[0][0]['psw'])):
            return redirect(url_for('prediction'))
        else:
            print('Invalid User')
            # flash("invalid")
            return render_template('login.html',message="invalid credentials")
    return "nothing"

@app.route('/logout')
def logout():
    return render_template('logout.html')

# class dotdict(dict):
#     """dot.notation access to dictionary attributes"""
#     __getattr__ = dict.get
#     __setattr__ = dict.__setitem__
#     __delattr__ = dict.__delitem__

@app.route('/prediction')
def prediction():
    return render_template('prediction.html',prediction="Checking for drowning")

def draww(frame,bbox,conf):
    for i in range(len(bbox)):
        print("confidenc :")
        print(conf)
        start_point = (bbox[i][0], bbox[i][1])
        end_point = (bbox[i][2], bbox[i][3])
        color = (255, 0, 0)
        thickness = 2
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
    return frame

@app.route('/result',methods=['post'])
def res():
    webcam1 = cv2.VideoCapture('drowninga.mp4')
    webcam2 = cv2.VideoCapture('drowninga.mp4')
    webcam3 = cv2.VideoCapture('drowninga.mp4')
    webcam4 = cv2.VideoCapture('drowninga.mp4')
    # print("looooooooook")
    x=[x for x in request.form.values()]
    # print(x)
    # print("looooooooook")
    if not webcam1.isOpened():
        print("Could Not Open Webcam")
        exit()
    t0=time.time()
    center0=np.zeros(2)

    isDrowning1=False
    isDrowning2=False
    isDrowning3=False
    isDrowning4=False
    # print(request.form.values)
    mod=request.form['model']
    # print(mod)
    # print("loooooooooooooooooooooooooook")
    while webcam1.isOpened():
        
        # mod='yolov3-tiny'
        threshold=10
        status,frame=webcam1.read()
        bbox,label,conf=cv.detect_common_objects(frame,model=mod)

        status1,frame1=webcam2.read()
        bbox1,label1,conf1=cv.detect_common_objects(frame1,model=mod)

        status2,frame2=webcam3.read()
        bbox2,label2,conf2=cv.detect_common_objects(frame2,model=mod)

        status3,frame3=webcam4.read()
        bbox3,label3,conf3=cv.detect_common_objects(frame3,model=mod)
        print("confidence :",conf," label :",label)
        # print("seeeeeeee")
        # print("---------------------------------------------")
        print("bbox :",bbox)
        # print("---------------------------------------------")
        if(len(bbox)>0):

            bbox0=bbox[0]

            center =[0,0]

            center=[(bbox0[0]+bbox0[2])/2,(bbox0[1]+bbox0[3])/2]
            
            hmov=abs(center[0]-center0[0])
            vmov= abs(center[1]-center0[1])

            x=time.time()
            threshold=10

            if(hmov>threshold or vmov>threshold):
                print(x-t0,'s')
                t0=time.time()
                isDrowning1=False 
            else:
                print(x-t0,'s')
                if((time.time()-t0)>10):
                    isDrowning1=True 
                
            print('bbox: ',bbox,'center:',center, 'center0:',center0 )
            print('Is he drowning  (1): ',isDrowning1)

            center0 =center 

            # out=draw_bbox(frame,bbox,label,conf,isDrowning)
         
            # print(bbbox.x0)
            # out=draw_bbox(frame,bbbox,label,conf)
            # out=draw_bbox(bbox,frame)
            
            # frame=draww(frame,bbox,conf)
            # out=frame
            out= draw_bbox(frame, bbox, label, conf)
            cv2.imshow("Real-Time objects detection",out)
        else:
            out=frame
            cv2.imshow("Real-Time objects detection",out)
        # cv2.imshow("Real-Time objects detection",frame)

        # print("seeeeeeee")
        # print("---------------------------------------------")
        # print(bbox1)
        # print("---------------------------------------------")
        if(len(bbox1)>0):

            bbox0=bbox1[0]

            center =[0,0]

            center=[(bbox0[0]+bbox0[2])/2,(bbox0[1]+bbox0[3])/2]
            
            hmov=abs(center[0]-center0[0])
            vmov= abs(center[1]-center0[1])

            x=time.time()
            threshold=10

            if(hmov>threshold or vmov>threshold):
                print(x-t0,'s')
                t0=time.time()
                isDrowning2=False 
            else:
                print(x-t0,'s')
                if((time.time()-t0)>10):
                    isDrowning2=True 
                
            print('bbox: ',bbox1,'center:',center, 'center0:',center0 )
            print('Is he drowning  (2): ',isDrowning2)

            center0 =center 

            # out=draw_bbox(frame,bbox,label,conf,isDrowning)
         
            # print(bbbox.x0)
            # out=draw_bbox(frame,bbbox,label,conf)
            # out=draw_bbox(bbox,frame)
            
            # frame=draww(frame,bbox,conf)
            # out=frame
            out= draw_bbox(frame1, bbox1, label1, conf1)
            cv2.imshow("Real-Time objects detection",out)
        else:
            out=frame1
            cv2.imshow("Real-Time objects detection",out)
        # cv2.imshow("Real-Time objects detection",frame)

        # print("seeeeeeee")
        # print("---------------------------------------------")
        # print(bbox2)
        # print("---------------------------------------------")
        if(len(bbox2)>0):

            bbox0=bbox2[0]

            center =[0,0]

            center=[(bbox0[0]+bbox0[2])/2,(bbox0[1]+bbox0[3])/2]
            
            hmov=abs(center[0]-center0[0])
            vmov= abs(center[1]-center0[1])

            x=time.time()
            threshold=10

            if(hmov>threshold or vmov>threshold):
                print(x-t0,'s')
                t0=time.time()
                isDrowning3=False 
            else:
                print(x-t0,'s')
                if((time.time()-t0)>10):
                    isDrowning3=True 
                
            print('bbox: ',bbox2,'center:',center, 'center0:',center0 )
            print('Is he drowning  (3): ',isDrowning3)

            center0 =center 

            # out=draw_bbox(frame,bbox,label,conf,isDrowning)
         
            # print(bbbox.x0)
            # out=draw_bbox(frame,bbbox,label,conf)
            # out=draw_bbox(bbox,frame)
            
            # frame=draww(frame,bbox,conf)
            # out=frame
            out= draw_bbox(frame2, bbox2, label2, conf2)
            cv2.imshow("Real-Time objects detection",out)
        else:
            out=frame2
            cv2.imshow("Real-Time objects detection",out)
        # cv2.imshow("Real-Time objects detection",frame)

        # print("seeeeeeee")
        # print("---------------------------------------------")
        # print(bbox3)
        # print("---------------------------------------------")
        if(len(bbox3)>0):

            bbox0=bbox3[0]

            center =[0,0]

            center=[(bbox0[0]+bbox0[2])/2,(bbox0[1]+bbox0[3])/2]
            
            hmov=abs(center[0]-center0[0])
            vmov= abs(center[1]-center0[1])

            x=time.time()
            threshold=10

            if(hmov>threshold or vmov>threshold):
                print(x-t0,'s')
                t0=time.time()
                isDrowning3=False 
            else:
                print(x-t0,'s')
                if((time.time()-t0)>10):
                    isDrowning3=True 
                
            print('bbox: ',bbox3,'center:',center, 'center0:',center0 )
            print('Is he drowning (4) : ',isDrowning4)

            center0 =center 

            # out=draw_bbox(frame,bbox,label,conf,isDrowning)
         
            # print(bbbox.x0)
            # out=draw_bbox(frame,bbbox,label,conf)
            # out=draw_bbox(bbox,frame)
            
            # frame=draww(frame,bbox,conf)
            # out=frame
            out= draw_bbox(frame3, bbox3, label3, conf3)
            cv2.imshow("Real-Time objects detection",out)
        else:
            out=frame3
            cv2.imshow("Real-Time objects detection",out)
        # cv2.imshow("Real-Time objects detection",frame)

        if(isDrowning1==True):
            audio =os.path.dirname(__file__)+"/sound.wav"
            playsound(audio)
            # playsound('alarm.mp3')
            webcam1.release()
            cv2.destroyAllWindows()
            # return "nothing"
            return render_template('prediction.html',prediction="Emergency !!! The Person is drowning in top left")

        if(isDrowning2==True):
            audio =os.path.dirname(__file__)+"/sound.wav"
            playsound(audio)
            # playsound('alarm.mp3')
            webcam1.release()
            cv2.destroyAllWindows()
            # return "nothing"
            return render_template('prediction.html',prediction="Emergency !!! The Person is drowning in top right")

        if(isDrowning3==True):
            audio =os.path.dirname(__file__)+"/sound.wav"
            playsound(audio)
            # playsound('alarm.mp3')
            webcam1.release()
            cv2.destroyAllWindows()
            # return "nothing"
            return render_template('prediction.html',prediction="Emergency !!! The Person is drowning in bottom left")

        if(isDrowning4==True):
            audio =os.path.dirname(__file__)+"/sound.wav"
            playsound(audio)
            # playsound('alarm.mp3')
            webcam1.release()
            cv2.destroyAllWindows()
            # return "nothing"
            return render_template('prediction.html',prediction="Emergency !!! The Person is drowning in bottom right")    

        if cv2.waitKey(1) & 0XFF == ord('q'):
            break 

    cv2.destroyAllWindows()
    return render_template('prediction.html',prediction="Checking for drowning")


if __name__ =='__main__':
    app.run(debug=True)