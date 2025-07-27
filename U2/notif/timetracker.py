import time


class Time:


    def __init__( self ):
        self.str = "00:00"
        self.seconds = 0


    def set_seconds( self, n : int ):
        if not isinstance( n, int ):
            self.str = "Error"
            return
        self.seconds = n

        # Convert int to time string
        hour = ( n // 3600 ) % 24
        mins = ( n // 60 ) % 60
        secs = ( n % 60 )

        _str = ""
        _str += f"{hour:02d}:" if hour else ""
        _str += f"{mins:02d}:{secs:02d}"
        self.str = _str


    def set_string( self, s : str ):
        if not isinstance( s, str ):
            self.seconds = 0
            self.str = "Error"
            return
        self.str = s

        # Convert time string to seconds
        _split = s.split( ':' )

        hour = int( _split[0] ) * 3600 if len( _split ) > 2 else 0
        mins = int( _split[-2] ) * 60
        secs = int( _split[-1] )

        self.seconds = hour + mins + secs


    def __repr__( self ):
        return self.str


class Tracker( Time ):


    def __init__( self, min_interval = 0 ):
        super().__init__()
        # List containers for tracked time
        self.shortL = []
        self.longL = []

        # Sum of every elapsed time calculated
        self.total_intervals = 0
        self.track_calls = 0

        # Minimum interval required to track
        self.min_interval = min_interval

        # Time class for average time interval
        self.avgTime = Time()


    def trackS( self ):
        self.shortL.append( time.time() )

        if len( self.shortL ) > 1:
            t = self.shortL
      
            interval = int( t[1] - t[0] )

            # Set a minimum interval to prevent messing with average intervak
            if interval > self.min_interval:
                self.total_intervals += interval
                
                self.track_calls += 1
                self.calc_avg()

            self.set_seconds( interval )
            del t[0]


    def reset_avg( self ):
        # Reset recorded avg time
        self.avgTime.set_seconds( 0 )

        self.total_intervals = 0
        self.track_calls = 0


    def calc_avg( self ):
        self.avgTime.set_seconds( self.total_intervals // self.track_calls ) if self.track_calls else None


if __name__=='__main__':
    pass


