import time, os
import cv2 as cv
import uiautomator2 as u2


class types:
    click = "android.widget.TextView"
    text = "android.view.ViewGroup"
    button = "android.widget.Button"


def dump():
    # Dump ui heirarchy to xml file
    time.sleep(2)
    d = u2.connect()
    
    path = "/storage/emulated/0/outmess.xml"

    with open(path, 'w', encoding='utf-8') as f:
        f.write( d.dump_hierarchy(pretty=False) )


def viewElement( selector, log=False ):
    time.sleep(2)
    d = u2.connect()

    path = "/storage/emulated/0/termux_dump"
    if not os.path.exists( path):
        os.mkdir( path )

    found = {}
    
    el = d(**selector)          
    if el.exists:
        try:
            info = el.info

            found[f"{info['text'].split('\n')[0]}"] = info

            shortName = info['className'].split('.')[-1]
            print(f"{shortName} | {repr(info['text'])}\nBounds | {info['bounds']}\n")
        
        except Exception as e:
            print(f"TextWidget {selector}:Error")
            

    if log:
        # Draw rectangle of positions of every element found
        adbshot = path + '/adbshot.png'
        os.system(f"adb shell screencap {adbshot}")

        time.sleep(0.8)
        img = cv.imread( adbshot, 1 )

        for name, info in found.items():
            print(f'Marking {name}')
            coo = info.get('bounds')
            
            if coo is not None:
                tl = coo['left'], coo['top']
                br = coo['right'], coo['bottom']

                img_copy = img.copy()

                cv.rectangle(
                    img_copy, tl, br,
                    color = (0,255,0),
                    lineType = cv.LINE_4,
                    thickness = 3
                )
                cv.imwrite( f"{path}/{name}.png", img_copy )    
    os.system("adb shell cmd notification post -S bigtext Done Done Done &> /dev/null")

def viewElements( _type, _range=(0,20), log=False, getcenter=False ):
    # Dump all specified widget type
    time.sleep(2)
    d = u2.connect()

    path = "/storage/emulated/0/termux_dump"
    if not os.path.exists( path):
        os.mkdir( path )

    found = {}

    selector = {"className": _type }
    for i in range( _range if _range is int else _range[0], _range[1] ):  # Arbitrary max limit
        
        el = d(**selector, instance=i)      
        if not el.exists:
            break
        
        try:
            info = el.info

            found[f"Instance {i}-{info['text'].split('\n')[0]}"] = info

            shortName = info['className'].split('.')[-1]
            print(f"[Instance {i}] {shortName} | {repr(info['text'])}")
            
            if getcenter:
                coo = info['bounds']

                width = coo['right'] - coo['left']
                height = coo['bottom'] - coo['top']

                x = coo['right'] - ( width // 2 )
                y = coo['bottom'] - ( height // 2 )

                print(f"center {x}:{y}")
        
        except Exception as e:
            #print(f"TextWidget Instance {i}:Error")
            continue

    if log:
        # Draw rectangle of positions of every element found
        adbshot = path + '/adbshot.png'
        os.system(f"adb shell screencap {adbshot}")

        time.sleep(0.8)
        img = cv.imread( adbshot, 1 )

        for name, info in found.items():
            print(f'Marking {name}')
            coo = info.get('bounds')
            
            if coo is not None:
                tl = coo['left'], coo['top']
                br = coo['right'], coo['bottom']

                img_copy = img.copy()

                cv.rectangle(
                    img_copy, tl, br,
                    color = (0,255,0),
                    lineType = cv.LINE_4,
                    thickness = 3
                )
                cv.imwrite( f"{path}/{name}.png", img_copy )    
    os.system("adb shell cmd notification post -S bigtext Done Done Done &> /dev/null")

if __name__=='__main__':
    dump()
    pass
