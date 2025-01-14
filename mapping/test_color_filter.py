from get_camera_feed import *

if __name__ == "__main__":
    pwd = os.path.realpath(os.path.dirname(__file__))
    cv2.namedWindow("unfiltered", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("unfiltered", 400, 300)    
    for name in ["/bottle (1).jpg", "/bottle (2).jpg", "/bottle (3).jpg"]:
        img = cv2.imread(pwd + name)
        cv2.imshow("unfiltered", img)
        cv2.waitKey(0)
        img = balance_colors(img)
        cv2.namedWindow("filtered", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("filtered", 400, 300)    
        cv2.imshow("filtered", img)
        cv2.waitKey(0)
