from ..notif import notif, getHour
from threading import Thread


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
        # Added layer of string quote marks
        # for termux notif content arg
        return f"'{'\n'.join(l)}'"

notiflog = NotifLog(4)


def logNotif( timestamp, log ):
    # Log to termux-notification
    stamp = "" if not timestamp else f"[ {getHour()} ] "
    
    log_ = stamp + log

    notiflog < log_
    notif( content = notiflog )


def notif_( timeStamp, log ):
    # Log to stdout and notifciation
    Thread( target=logNotif, args=(timeStamp,log,) ).start()


if __name__=='__main__':
    pass
