import pickle
import requests
import cv2
import numpy as np
import os

all_imgs = []
start_y = None
start_x = None

green_intensity_change = -30 #out of 255
blue_intensity_change = 40 #out of 255
red_intensity_change = 0 #out of 255

def save_to_file(data, name):
    with open(name, "wb") as f:
        pickle.dump(data, f)

def liveFeed():
    while True:
        img_data = load_from_file(pwd + "/image_data.sav")
        cv2.imshow("live", img_data[-1][0])

def balance_colors(img):
    img_b, img_g, img_r = cv2.split(img) #split by channel
    #change green
    img_g = np.int32(img_g)
    img_g += green_intensity_change
    np.clip(img_g, 0, 255, out=img_g)
    img_g = np.uint8(img_g)
    #change red
    img_r = np.int32(img_r)
    img_r += red_intensity_change
    np.clip(img_r, 0, 255, out=img_r)
    img_r = np.uint8(img_r)
    #change blue
    img_b = np.int32(img_b)
    img_b += blue_intensity_change
    np.clip(img_b, 0, 255, out=img_b)
    img_b = np.uint8(img_b)
    #combine channels
    img = cv2.merge((img_b, img_g, img_r)) #merge adjusted channels
    return img

def save_img(img, x, y, z):
    global all_imgs
    global start_x
    global start_y
    if start_x == None: start_x = x
    if start_y == None: start_y = y
    #ADD LIVE FEED HERE?
    img = balance_colors(img)
    all_imgs.append((img,x,y,z,start_x,start_y))
    save_to_file(all_imgs, pwd + "/image_data.sav")

def getImg():
    r = requests.get('http://172.20.10.9/video')
    print(r)

def getPosition():
    r = requests.get('http://172.20.10.9/position')
    print(r)

if __name__ == "__main__":
    pwd = os.path.realpath(os.path.dirname(__file__))
    while True:
        img = getImg()
        x,y,z = getPosition()
        save_img(img, x, y, z)