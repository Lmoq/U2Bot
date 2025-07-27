import cv2 as cv
import os, time, re

count = 0
# Ensure adbpipe and shell is running
def boxArea( coo:dict=None, name:str="snip", overlap=True ):
    global count    
    # coo = ui.info['bounds']
    if not overlap:
        name = f'{count:02d}-{name}'
        count += 1

    # Format string to a valid file name
    replaced_spaces = name.replace( ' ','_' )
    fixed_name = re.sub(r'[^a-zA-Z0-9_\-\[\]\s]','', replaced_spaces )

    path = f'/storage/emulated/0/termux_dump/{fixed_name}.png'
    
    os.system(f"echo screencap {path} > ~/pipes/adbpipe")

    if coo is not None:
        time.sleep(0.8)
        img = cv.imread( path, 1 )

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
    pass
