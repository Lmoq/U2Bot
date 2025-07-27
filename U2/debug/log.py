from ..notif import notif, getHour, getHourSec
import os, logging


class NotifLog:
    title = "U2"
    recheck = 0
    gInfo = 0
    timeout = 0
    total_duration = ""
    restarts = 0

    capacity = 4

    def __init__( self ):
        self.list = []


    def __lt__( self, string ):
        self.list.append( string )
        
        if len( self.list ) > NotifLog.capacity:
            self.list.pop( 0 )


    def __repr__( self ):
        l = self.list
        # Added layer of string quote marks
        # for termux notif content arg
        return ' '.join([f'--line "{t}"' for t in l ])

    
    def updateTitle( self ):
        NotifLog.title = f'U2 | RC : {NotifLog.recheck} | DR : {NotifLog.total_duration} | RS : {NotifLog.restarts}'

notiflog = NotifLog()

def notif_( timeStamp, log ):
    # Log to adb shell notifciation
    stamp = "" if not timeStamp else f"[ {getHourSec()} ] "
    log_ = stamp + log

    notiflog < log_
    notiflog.updateTitle()

    cm = f'''echo 'cmd notification post -S inbox {notiflog} -t "{NotifLog.title}" notif logs &> /dev/null' > ~/pipes/adbpipe'''
    os.system(cm)


logging.basicConfig(
    filename = 'out.log',
    level = logging.INFO,
    datefmt = "%Y-%m-%d %H:%M:%S",
    format = "%(asctime)s : %(message)s"
)

def debugLog( message ):
    logging.info( message )

if __name__=='__main__':
    pass
