import numpy as np
import math
import pickle
import cv2

horizontal_fov = 66 #degrees
aspect_ratio = 1200/1600
vertical_fov = aspect_ratio*horizontal_fov #assuming equal FOV on both axes of lens
pool_dimensions = [2, 9]
pool_floor_height = 0 #assume pool is on the ground

visual_map_precision = 0.01 #in m
green_reduction_intensity = int(0.2*255) #out of 255
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
    total_conf = (x_conf + visual_map[x_coord][y_coord][3] + y_conf + visual_map[x_coord][y_coord][4])
    new_color_conf = (x_conf + y_conf)
    current_color_conf = (visual_map[x_coord][y_coord][3] + visual_map[x_coord][y_coord][4])
    visual_map[x_coord][y_coord][0] = (color[0]*new_color_conf + visual_map[x_coord][y_coord][0]*current_color_conf)/total_conf
    visual_map[x_coord][y_coord][1] = (color[1]*new_color_conf + visual_map[x_coord][y_coord][1]*current_color_conf)/total_conf
    visual_map[x_coord][y_coord][2] = (color[2]*new_color_conf + visual_map[x_coord][y_coord][2]*current_color_conf)/total_conf
    visual_map[x_coord][y_coord][3] = (x_conf + visual_map[x_coord][y_coord][3])/2
    visual_map[x_coord][y_coord][4] = (y_conf + visual_map[x_coord][y_coord][4])/2

    #HIGHEST CONFIDENCE WITH PRIORITY ON Y
    if (visual_map[x_coord][y_coord][4] < y_conf):
        visual_map[x_coord][y_coord][0] = color[0]
        visual_map[x_coord][y_coord][1] = color[1]
        visual_map[x_coord][y_coord][2] = color[2]
        visual_map[x_coord][y_coord][3] = x_conf
        visual_map[x_coord][y_coord][4] = y_conf
    elif (visual_map[x_coord][y_coord][4] == y_conf and visual_map[x_coord][y_coord][3] < x_conf)
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

def build_heatmap():
    #make grey black
    #make white true white
    #make yellow pure yellow
    #etc
    #indicate center points of dead zones (white zones)
    return

if __name__ == "__main__":
    img_data = load_from_file("image_data.sav")
    for data in img_data:
        add_img_to_map(data)
    build_heatmap()