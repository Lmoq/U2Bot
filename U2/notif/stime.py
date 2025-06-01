import time


def timenow() -> str:
    return time.strftime("%a %H:%M:%S")

def getHour() -> str:
    return time.strftime("%H:%M")

def getHourSec() -> str:
    return time.strftime("%H:%M:%S")

class Stime:
    # A string class that can be converted to seconds, 
    # perform arbitrary operations to its instances
    # init : str = "Abvdayname 24Hour:Minutes:Seconds"
    tmap = {
        "Mon" : 0,
        "Tue" : 1,
        "Wed" : 2,
        "Thu" : 3,
        "Fri" : 4,
        "Sat" : 5,
        "Sun" : 6
    }
    max_seconds = 604800 
    
    def __init__( self, time_str:str="", default = True ): 
        self.str = timenow() if (default and not time_str) else time_str
        self.seconds = 0

        if self.str:
            self.to_seconds( self.str )


    def to_seconds( self, string ):
        # Convert time string to seconds
        _str = string.split(' ')

        day = self.tmap.get( _str[0] )
        hour, mins, secs = _str[1].split(':')

        self.seconds = ( day * ( 3600 * 24 ) ) + \
               ( int(hour) * 3600 ) + \
               ( int(mins) * 60 ) + \
               ( int(secs) )


    def now( self ):
        # Update value to current time
        self.str = timenow()
        self.to_seconds( self.str )


    def to_str( self, _int ):
        # Convert seconds to time string
        day = (_int // ( 3600 * 24 )) % 7
        hour = (_int // 3600 ) % 24
        mins = (_int // 60 ) % 60
        secs = _int % 60

        for k,v in self.tmap.items():
            if day == v:
                day = k
                break
        self.str = f"{day} {hour:02d}:{mins:02d}:{secs:02d}"


    def __add__( self, _int ):
        if not isinstance( _int, int ):
            return None

        new = Stime( default = False )

        new.seconds = (self.seconds + _int) % Stime.max_seconds
        new.to_str( new.seconds )
        
        return new


    def __iadd__( self, _int ):
        if not isinstance( _int, int ):
            return None

        self.seconds = ( self.seconds + _int ) % 604800
        self.to_str( self.seconds )
        
        return self


    def __sub__( self, _int ):
        if not isinstance( _int, int ):
            return None

        new = Stime( default = False )
        
        new.seconds = (self.seconds - _int) % Stime.max_seconds
        new.to_str( new.seconds )
        
        return new

    
    def __isub__( self, _int ):
        if not isinstance( _int, int ):
            return None

        self.seconds = ( self.seconds - _int ) % 604800
        self.to_str( self.seconds )
        
        return self


    def __lt__( self, stime ):
        if not isinstance( stime, Stime ):
            return none

        return self.seconds < stime.seconds

    
    def __gt__( self, stime ):
        if not isinstance( stime, Stime ):
            return none

        return self.seconds > stime.seconds

 
    def __le__( self, stime ):
        if not isinstance( stime, Stime ):
            return none

        return self.seconds <= stime.seconds


    def __ge__( self, stime ):
        if not isinstance( stime, Stime ):
            return none

        return self.seconds >= stime.seconds
    

    def __eq__( self, stime ):
        if not isinstance( stime, Stime ):
            return none

        return self.seconds == stime.seconds
    

    def __repr__( self ):
        return self.str


    def in_range( self, start, end ):
        if self >= start and self <= end:
            return True
        elif start > end:
            if self >= end or self <= start:
                return True
        return False


if __name__=='__main__':
    pass

