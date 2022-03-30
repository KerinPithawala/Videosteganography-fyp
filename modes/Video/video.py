from stegano import lsb
from os.path import isfile, join

import face_recognition

import math
import time  # install time ,opencv,numpy modules
import cv2
import numpy as np
import math
import os
import shutil
from subprocess import run, call, STDOUT
from flask import Blueprint, render_template, current_app, url_for, redirect, request, session, flash
from datetime import timedelta
# from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename

video = Blueprint("video", __name__, static_folder="static",
                  template_folder="templates")

todecrypt=[]

p=3
q=11

#RSA Modulus
n = p * q

 
#Eulers Toitent
r= (p-1)*(q-1)

 
#GCD
'''CALCULATION OF GCD FOR 'e' CALCULATION.'''
def egcd(e,r):
    while(r!=0):
        e,r=r,e%r
    return e
 
#Euclid's Algorithm
def eugcd(e,r):
    for i in range(1,r):
        while(e!=0):
            a,b=r//e,r%e
            r=e
            e=b
 
#Extended Euclidean Algorithm
def eea(a,b):
    if(a%b==0):
        return(b,0,1)
    else:
        gcd,s,t = eea(b,a%b)
        s = s-((a//b) * t)
  
        return(gcd,t,s)
 
#Multiplicative Inverse
def mult_inv(e,r):
    gcd,s,_=eea(e,r)
    if(gcd!=1):
        return None
    else:
        return s%r
 
#e Value Calculation

for i in range(1,1000):
    if(egcd(i,r)==1):
        e=i

 
#d, Private and Public Keys

eugcd(e,r)
d = mult_inv(e,r)
public = (e,n)
private = (d,n)
#print("Private Key is:",private)
print("Public Key is:",public)

#Array to store the case of letter 
A=[]
 
#Encryption
'''ENCRYPTION ALGORITHM.'''
def rsa_encrypt(pub_key,n_text):
    e,n=pub_key
    x=[]
    m=0
    for i in n_text:
        if(i.isupper()):
            A.append(0)
            m = ord(i)-65
            c=(m**e)%n
            x.append(c)
        elif(i.islower()): 
            A.append(1)              
            m= ord(i)-97
            c=(m**e)%n
            x.append(c)
        elif(i.isspace()):
            A.append(2)
            spc=400
            x.append(400)
    return x  

print(A)
 
#Decryption
'''DECRYPTION ALGORITHM'''
def rsa_decrypt(priv_key,secret):
    d,n=priv_key   
    x=''
    m=0
    for i in secret:
        if(i=='400'):
            x+=' '
        else:
            m=(int(float(i))**d)%n
            m+=65
            c=chr(m)
            x+=c
    return x


@video.route("/encode")
def video_encode():

    return render_template("encode-video.html")


@video.route("/encode-result", methods=['POST', 'GET'])
def video_encode_result():
    if request.method == 'POST':
        message = request.form['message']
        if 'file' not in request.files:
            flash('No video found')
            # return redirect(request.url)
        file = request.files['video']
        if file.filename == '':
            flash('No selected video')
            # return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_VIDEO_FOLDER'], filename))
            encryption = True
            encrypt(os.path.join(
                current_app.config['UPLOAD_VIDEO_FOLDER'], filename), message)
        else:
            encryption = False
        result = request.form
        return render_template("encode-video-result.html", message=message, result=result, file=file, encryption=encryption)


@video.route("/decode")
def check_face():
    cam = cv2.VideoCapture(0)
    database ={'sarthak': "images\Photo on 07-03-22 at 11.54 AM.jpg", 'kerin':"images\Kerin-Test.jpg"}
    encodings={}
    for k,v in database.items():
        image = face_recognition.load_image_file(v)
        encoding = face_recognition.face_encodings(image)[0]
        encodings[k] = encoding

    
    
    while True:
        check, frame = cam.read()
        cv2.imshow('video', frame)
        unknown_encoding = face_recognition.face_encodings(frame)
        if len(unknown_encoding):
            unknown_encoding = unknown_encoding[0]
            results = face_recognition.compare_faces(list(encodings.values()), unknown_encoding)
    
            if True in results:
                cam.release()
                cv2.destroyAllWindows()
                return render_template("decode-video.html")

                break


    
        
        


@video.route("/decode-result", methods=['POST', 'GET'])
def video_decode_result():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No Video found')
            


        file = request.files['video']
        if file.filename == '':
            flash('No selected video')
            # return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                current_app.config['UPLOAD_VIDEO_FOLDER'], filename))
            decryption = True
            decrpytedText = decrypt(os.path.join(
                current_app.config['UPLOAD_VIDEO_FOLDER'], filename))
        else:
            decryption = False
        result = request.form
        return render_template("decode-video-result.html", result=result, decrypytedText=decrpytedText, file=file, decryption=decryption)


# encrypt Video

def encrypt(f_name, input_string):
    frame_extraction(f_name)
    print(os.getcwd())
    path = str(os.getcwd()) + \
        "\modes\Video\\ffmpeg-4.3.1-2020-10-01-full_build\\bin\\ffmpeg"
    print(path)
    # command = path + " -i "+ f_name + " -q:a 0 -map a" + str(os.getcwd())+"/tmp/audio.mp3 -y"
    # os.system(command)
    # run([path, "-i", f_name, "-q:a", "0", "-map", "a",
    #      str(os.getcwd())+"/tmp/audio.mp3", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)

    
    encode_string(input_string)

    sec_command = path + " -i tmp/%d.png -vcodec png modes/Video/static/enc-video.mp4 -y"
    print(sec_command)
    os.system(sec_command)
    # call([path, "-i", "tmp/%d.png", "-vcodec", "png", "video.mov",
    #       "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)

    # third_command = path + ""
    # call([path, "-i", "video.mov", "-i", "tmp/audio.mp3", "-codec",
    #       "copy", "data/enc-" + str(f_name)+".mov", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)

#Convert split string
'''
def split_string(s_str, count=10):
    per_c = math.ceil(len(s_str)/count)
    c_cout = 0
    out_str = ''
    split_list = []
    for s in s_str:
        out_str += s
        c_cout += 1
        if c_cout == per_c:
            split_list.append(out_str)
            out_str = ''
            c_cout = 0
    if c_cout != 0:
        split_list.append(out_str)
    return split_list
'''

def frame_extraction(video):
    if not os.path.exists("./tmp"):
        os.makedirs("tmp")
    temp_folder = "./tmp"
    print("[INFO] tmp directory is created")

    vidcap = cv2.VideoCapture(video)
    count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break
        cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
        count += 1


def encode_string(input_string, root="./tmp/"):
    ciphertxt=rsa_encrypt(public,input_string)
    todecrypt=ciphertxt
    list_string= [str(x) for x in ciphertxt]
    print(ciphertxt)
    print(type(ciphertxt))
    #convert integer to string list
    #split_string_list = split_string(ciphertxt)
    for i in range(0, len(list_string)):
        f_name = "{}{}.png".format(root, i)
        secret_enc = lsb.hide(f_name, list_string[i])
        secret_enc.save(f_name)
        print("[INFO] frame {} holds {}".format(f_name, list_string[i]))


def decrypt(video):
    
    frame_extraction(video)
    secret = []
    root = "./tmp/"
    for i in range(len(os.listdir(root))):
        f_name = "{}{}.png".format(root, i)
        secret_dec = lsb.reveal(f_name)
        if secret_dec == None:
            break
        secret.append(secret_dec)
    #print(secret_dec)
    #intsecret = [int(x) for x in secret]
    print("secret=", secret)
    
    
    final_result = rsa_decrypt(private, secret)

    li_final_result=list(final_result)

    for i in range(0,len(A)):
        if A[i]==1:
            li_final_result[i]=li_final_result[i].lower()

    print(li_final_result)

    output_result="".join(li_final_result)
    
    print(output_result)
    
    
            
    clean_tmp()
    return output_result


def clean_tmp(path="./tmp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] tmp files are cleaned up")


