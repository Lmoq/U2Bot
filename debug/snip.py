import cv2 as cv
import os, time

# Ensure adbpipe and shell is running
def boxArea( coo:dict ):
    # coo = ui.info['bounds']
    path = "/storage/emulated/0/VSCODE/CV/needle.png"

    os.system(f"echo screencap {path} > ~/pipes/adbpipe")
    time.sleep(0.5)
    img = cv.imread( path, 1 )

    if coo is not None:

        tl = coo['left'], coo['top']
        br = coo['right'], coo['bottom']
        
        cv.rectangle(
            img, tl, br,
            color = (0,255,0),
            lineType = cv.LINE_4,
            thickness = 3
        )
    cv.imwrite( path, img)

if __name__=='__main__':
    import time
    coo = {
            'left':109, 
            'top':921, 
            'right':507, 
            'bottom':1160
    }
    time.sleep(2)
    boxArea(coo)


