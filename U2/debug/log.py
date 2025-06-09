from ..notif import notif, getHour, getHourSec
import os


class NotifLog:
    title = "U2"
    recheck = 0
    gInfo = 0
    timeout = 0

    def __init__( self, capacity ):
        self.capacity = capacity
        self.list = []


    def __lt__( self, string ):
        self.list.append( string )
        
        if len( self.list ) > self.capacity:
            self.list.pop( 0 )


    def __repr__( self ):
        l = self.list
        # Added layer of string quote marks
        # for termux notif content arg
        return ' '.join([f'--line "{t}"' for t in l ])

    
    def updateTitle( self ):
        NotifLog.title = f'U2 | RCH : {NotifLog.recheck} | GI : {NotifLog.gInfo} | TM : {NotifLog.timeout} |'

notiflog = NotifLog(4)

def logNotif( timestamp, log ):
    # Log to termux-notification
    # notif( content = notiflog )
    pass

def notif_( timeStamp, log ):
    # Log to stdout and notifciation
    # Thread( target=logNotif, args=(timeStamp,log,) ).start()
    stamp = "" if not timeStamp else f"[ {getHourSec()} ] "
    log_ = stamp + log

    notiflog < log_
    notiflog.updateTitle()

    cm = f'''echo 'cmd notification post -S inbox {notiflog} -t "{NotifLog.title}" notif Logs &> /dev/null' > ~/pipes/adbpipe'''
    os.system(cm)

if __name__=='__main__':
    pass
