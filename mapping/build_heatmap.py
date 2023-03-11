import numpy as np
import math
import pickle
import cv2
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
import os

horizontal_fov = 66 #degrees
aspect_ratio = 1200/1600
vertical_fov = aspect_ratio*horizontal_fov #assuming equal FOV on both axes of lens
pool_dimensions = [2, 9]
pool_floor_height = 0 #assume pool is on the ground

visual_map_precision = 0.05 #in m
visual_map = np.zeros((int(pool_dimensions[0]/visual_map_precision), int(pool_dimensions[1]/visual_map_precision), 5))
assumeRobotAlwaysCentered = True

start_y = None
start_x = None

def save_to_file(data, name):
    with open(name, "wb") as f:
        pickle.dump(data, f)

def load_from_file(name):
    with open(name, "rb") as f:
        return pickle.load(f)

def roundToPrecision(x):
    decimals = math.log10(visual_map_precision)
    return int(x*(10**decimals))/(10**decimals)

def add_mapping(color, world_x, world_y, x_conf, y_conf):
    global visual_map
    x_coord = roundToPrecision(world_x)-start_x
    y_coord = roundToPrecision(world_y)-start_y
    if x_coord < 0 or x_coord > visual_map.shape[0]: return
    if y_coord < 0 or y_coord > visual_map.shape[1]: return
    #NOT SURE WHICH IS BEST TAKE EITHER OF IMPLEMENTATIONS BELOW
    #WEIGHTED AVERAGE
    new_color_conf = (x_conf + y_conf)
    current_color_conf = (visual_map[x_coord][y_coord][3] + visual_map[x_coord][y_coord][4])
    total_conf = new_color_conf + current_color_conf
    visual_map[x_coord][y_coord][0] = (color[0]*new_color_conf + visual_map[x_coord][y_coord][0]*current_color_conf)/total_conf
    visual_map[x_coord][y_coord][1] = (color[1]*new_color_conf + visual_map[x_coord][y_coord][1]*current_color_conf)/total_conf
    visual_map[x_coord][y_coord][2] = (color[2]*new_color_conf + visual_map[x_coord][y_coord][2]*current_color_conf)/total_conf
    visual_map[x_coord][y_coord][3] = (x_conf + visual_map[x_coord][y_coord][3])/2
    visual_map[x_coord][y_coord][4] = (y_conf + visual_map[x_coord][y_coord][4])/2
    return
    #HIGHEST CONFIDENCE WITH PRIORITY ON Y
    if (visual_map[x_coord][y_coord][4] < y_conf):
        visual_map[x_coord][y_coord][0] = color[0]
        visual_map[x_coord][y_coord][1] = color[1]
        visual_map[x_coord][y_coord][2] = color[2]
        visual_map[x_coord][y_coord][3] = x_conf
        visual_map[x_coord][y_coord][4] = y_conf
    elif (visual_map[x_coord][y_coord][4] == y_conf and visual_map[x_coord][y_coord][3] < x_conf):
        visual_map[x_coord][y_coord][0] = color[0]
        visual_map[x_coord][y_coord][1] = color[1]
        visual_map[x_coord][y_coord][2] = color[2]
        visual_map[x_coord][y_coord][3] = x_conf
        visual_map[x_coord][y_coord][4] = y_conf

def add_img_to_map(data):
    global start_x
    global start_y
    img, x, y, z, start_x, start_y = data
    if assumeRobotAlwaysCentered: x = start_x
    height, width, _ = img.shape
    for r in range(len(img)):
        row = img[r]
        y_distance_from_center = abs(r-height/2)
        y_center_amt = y_distance_from_center/(0.5*height)
        y_confidence = 1. - y_center_amt
        depth = z-pool_floor_height
        world_y = y + y_center_amt*depth*vertical_fov
        for p in range(len(row)):
            x_distance_from_center = abs(p-width/2)
            x_center_amt = x_distance_from_center/(0.5*width)
            x_confidence = 1. - x_center_amt
            pixel = row[p]
            world_x = x + x_center_amt*depth*horizontal_fov
            add_mapping(pixel, world_x, world_y, x_confidence, y_confidence)

def compare_colors(c1, c2):
    color1_rgb = sRGBColor(c1[2], c1[1], c1[0])
    color2_rgb = sRGBColor(c2[2], c2[1], c2[0])
    color1_lab = convert_color(color1_rgb, LabColor)
    color2_lab = convert_color(color2_rgb, LabColor)
    delta_e = delta_e_cie2000(color1_lab, color2_lab)
    return delta_e

def build_heatmap(in_map=None):
    global visual_map
    if not in_map is None:
        visual_map = in_map
    colors = {
    #background
    'grey':(170, 170, 170),
    'black':(0, 0, 0),
    #dead coral
    'white':(255, 255, 255),
    #yellow coral
    'neon_yellow':(170, 255, 255),
    'medium_yellow':(77, 246, 197),
    'darker_yellow':(65, 207, 163),
    #orange coral
    'orange':(50, 127, 255),
    'medium_orange':(30, 100, 230),
    'dark_orange':(20, 90, 180),
    #blue coral
    'blue':(255, 0, 0),
    #'navy_blue':(180, 80, 50)
    }
    #'dark_blue':(150, 0, 0)}
    for r in range(len(visual_map)):
        row = visual_map[r]
        for p in range(len(row)):
            pixel_color = row[p]
            closest_color = ["none", np.inf]
            if np.std(pixel_color) < 25:
                if np.mean(pixel_color) > 225:
                    visual_map[r][p] = (255,255,255)
                else:
                    visual_map[r][p] = (0,0,0)
            else:
                for name, color in colors.items():
                    color_diff = compare_colors(color, pixel_color)
                    if color_diff < closest_color[1]:
                        closest_color[0] = name
                        closest_color[1] = color_diff
                if closest_color[0] in ['grey','black']:
                    visual_map[r][p] = (0,0,0)
                elif closest_color[0] in ['white', 'light_grey']:
                    visual_map[r][p] = (255,255,255)
                elif closest_color[0] in ['neon_yellow', 'medium_yellow', 'darker_yellow']:
                    visual_map[r][p] = (0,255,255)
                elif closest_color[0] in ['orange', 'medium_orange', 'dark_orange']:
                    visual_map[r][p] = (0,110,255)
                elif closest_color[0] in ['blue', 'navy_blue', 'dark_blue']:
                    visual_map[r][p] = (255,0,0)
    add_dead_coral_centers()
    return visual_map

def add_dead_coral_centers():
    global visual_map
    # convert the image to grayscale
    gray_image = cv2.cvtColor(visual_map, cv2.COLOR_BGR2GRAY)

    blur_amt = 0.25
    gray_image = cv2.blur(gray_image, (int(blur_amt*gray_image.shape[0]), int(blur_amt*gray_image.shape[0])))
    
    # convert the grayscale image to binary image
    ret,thresh = cv2.threshold(gray_image,127,255,0)
    
    # find contours in the binary image
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        # calculate moments for each contour
        M = cv2.moments(c)

        if M["m00"] != 0:
            # calculate x,y coordinate of center
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            if np.mean(visual_map[cY][cX]) == 255: visual_map[cY][cX] = (0, 0, 255)

if __name__ == "__main__":
    pwd = os.path.realpath(os.path.dirname(__file__))
    img_data = load_from_file(pwd + "/image_data.sav")
    for data in img_data:
        add_img_to_map(data)
    cv2.imshow("heatmap", build_heatmap())
    cv2.waitKey(0)