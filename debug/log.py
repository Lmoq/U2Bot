from ..notif.notif import notif
from threading import Thread
import time

class NotifLog:

    def __init__( self, capacity ):
        self.capacity = capacity
        self.list = []

    def __lt__( self, string ):
        self.list.append( string )
        
        if len( self.list ) > self.capacity:
            self.list.pop( 0 )

    def __repr__( self ):
        l = self.list
        return f"'{'\n'.join(l)}'"

notiflog = NotifLog(2)

def notif_( log ):
    print( log )
    
    timestr = time.strftime( "[ %I:%M:%S %p ]" )
    notiflog < f"{timestr} {log}"

    notif( content = notiflog )

def printf( log ):
    Thread( target=notif_, args=(log,) ).start()


if __name__=='__main__': 
    timestr = time.strftime( "[ %I:%M:%S %p ]" )
    log < f"{timestr} Lmao"

    print(log)
