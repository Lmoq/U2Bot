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


def vibrate( duration, times ):
    duration *= 1000
    cm = []
    for i in range( times ): 
        cm.append( f"termux-vibrate -d {duration}" )
    cm = ";sleep 0.5;".join( cm )

    os.system( cm + " &")


if __name__=='__main__':
    vibrate( 1, 2 )


