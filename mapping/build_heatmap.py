
horizontal_fov = 66 #degrees
aspect_ratio = 1200/1600
vertical_fov = aspect_ratio*horizontal_fov #assuming equal FOV on both axes of lens
pool_dimensions = [2, 9]
pool_floor_height = 0 #assume pool is on the ground

visual_map_precision = 0.01 #in m
green_reduction_intensity = int(0.2*255) #out of 255
visual_map = np.zeros((int(pool_dimensions[0]/visual_map_precision), int(pool_dimensions[1]/visual_map_precision), 3))

def save_map_to_file():
    with open("map.pickle") as f:
        pickle.dump(imgs[feed_name], f)

def remove_green_tint(img):
    img_b, img_g, img_r = cv2.split(img) #split by channel
    img_g = np.uint16(img_g)
    img_g += color_shift_intensity
    np.clip(img_g, 0, 255, out=img_g)
    img_g = np.uint8(img_g)
    img = cv2.merge((img_b, img_g, img_r)) #merge adjusted channels
    return img

def roundToPrecision():
    decimals = math.log10()

def add_mapping(color, world_x, world_y, x_distance_from_center, y_distance_from_center):
    

def image_cb(img, x, y, z):
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
