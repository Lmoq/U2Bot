import os, subprocess


class Direction:
    left = 'left'
    up = 'up'
    right = 'right'
    down = 'down'

class buttonInstance:
    # Center position of each button instance
    i3 = ( 360, 601 )
    i4 = ( 360, 745 )
    i5 = ( 360, 889 )
    i6 = ( 360, 1033 )


def adbClick( uiBounds : dict ):
    # Click center of UiObject
    coo = uiBounds
    
    left = coo['left']
    right = coo['right']

    top = coo['top']
    bottom = coo['bottom']

    x = left + int(( right - left) / 2)
    y = top + int(( bottom - top ) / 2)
    os.system( f"echo input tap {x} {y} > ~/pipes/adbpipe &" )


def adbClickNoUi( coo : tuple ):
    # Click directly using adb shell
    x,y = coo
    os.system( f"echo input tap {x} {y} > ~/pipes/adbpipe &" )


def adbSwipeUi( uiBounds : dict, direction : str, points : int, duration : int = 50 ):
    assert hasattr( Direction, direction ), "direction : left, up, right, down"

    coo = uiBounds

    left = coo['left']
    right = coo['right']

    top = coo['top']
    bottom = coo['bottom']

    x = left + int(( right - left) / 2)
    y = top + int(( bottom - top ) / 2)

    cm = ""

    match direction:
        case Direction.left:
            cm = f"input swipe {x} {y} {x-points} {y} {duration}"
        case Direction.up:
            cm = f"input swipe {x} {y} {x} {y-points} {duration}"
        case Direction.right:
            cm = f"input swipe {x} {y} {x+points} {y} {duration}"
        case Direction.down:
            cm = f"input swipe {x} {y} {x} {y+points} {duration}"

    os.system( f"echo '{cm}' > ~/pipes/adbpipe" )


def adbType( text : str ):
    command = f'''echo input text "{repr(text)}" > ~/pipes/adbpipe &'''
    os.system( command )


def vibrate( duration, times ):
    duration *= 1000
    cm = []
    for i in range( times ): 
        cm.append( f"termux-vibrate -f -d {duration}" )
    cm = ";sleep 0.5;".join( cm )

    os.system( cm + " &")


def switch_keyboard( toggle : str = "on/off" ):
    # Set default ime
    if toggle.lower() == "on":
        subprocess.run( "adb shell ime set com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME", stdout=subprocess.DEVNULL, shell=True )
    # Disable keyboard
    elif toggle.lower() == "off":
        subprocess.run( "adb shell ime set com.wparam.nullkeyboard/.NullKeyboard", stdout=subprocess.DEVNULL, shell=True )


if __name__=='__main__':
    pass


