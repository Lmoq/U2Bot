import cv2 as cv
import os, time

count = 0
# Ensure adbpipe and shell is running
def boxArea( coo:dict, name:str="snip", overlap=True ):
    global count    
    # coo = ui.info['bounds']
    if not overlap:
        name = f'{count:02d}-{name}'
        count += 1

    path = f"/storage/emulated/0/termux_dump/{name}.png"
    
    os.system(f"echo screencap {path} > ~/pipes/adbpipe")
    time.sleep(0.8)

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
    cv.imwrite( path, img )

if __name__=='__main__':
    import time
    time.sleep(2)
    coo = {'bottom': 1474, 'left': 586, 'right': 694, 'top': 1384} 
    boxArea(coo, 1)


