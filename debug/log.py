from ..notif.notif import notif
from threading import Thread
import time


def notif_( log ):
    print( log )
    
    timestr = time.strftime( "[%I:%M:%S %p]" )
    notif( content = f"'{timestr}\n{log}'" )

def printf( log ):
    Thread( target=notif_, args=(log,) ).start()

