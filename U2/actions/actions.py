import os

class buttonInstance:
    # Center position of each button instance
    i3 = ( 360, 601 )
    i4 = ( 360, 745 )
    i5 = ( 360, 889 )
    i6 = ( 360, 1033 )


def adbClick( uiBounds ):
    # Click center of UiObject
    coo = uiBounds
    
    left = coo['left']
    right = coo['right']

    top = coo['top']
    bottom = coo['bottom']

    x = left + int(( right - left) / 2)
    y = top + int(( bottom - top ) / 2)
    os.system( f"echo input tap {x} {y} > ~/pipes/adbpipe &" )


def adbClickNoUi( coo:tuple ):
    # Click directly using adb shell
    x,y = coo
    os.system( f"echo input tap {x} {y} > ~/pipes/adbpipe &" )


def vibrate( duration, times ):
    duration *= 1000
    cm = []
    for i in range( times ): 
        cm.append( f"termux-vibrate -f -d {duration}" )
    cm = ";sleep 0.5;".join( cm )

    os.system( cm + " &")


if __name__=='__main__':
    pass


