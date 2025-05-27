import os


def adbClick( uiBounds ):
    coo = uiBounds
    
    left = coo['left']
    right = coo['right']

    top = coo['top']
    bottom = coo['bottom']

    x = left + int(( right - left) / 2)
    y = top + int(( bottom - top ) / 2)
    os.system( f"echo input tap {x} {y} > ~/pipes/adbpipe &" )




