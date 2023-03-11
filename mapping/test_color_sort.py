from build_heatmap import *
from get_camera_feed import balance_colors

remove_green = False
filename = "/coral.jpg"

if __name__ == "__main__":
    pwd = os.path.realpath(os.path.dirname(__file__))
    cv2.namedWindow("unfiltered", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("unfiltered", 600, 400)    
    img = cv2.imread(pwd + filename)
    if remove_green:
        img = balance_colors(img)
    cv2.imshow("green removed", img)
    cv2.waitKey(0)
    img = build_heatmap(img)
    cv2.namedWindow("filtered", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("filtered", 600, 400)    
    cv2.imshow("filtered", img)
    cv2.waitKey(0)
