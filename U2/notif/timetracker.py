import time
from .stime import Stime


class Tracker( Stime ):

    def __init__( self, time_str:str="", **kwargs ):
        super().__init__( time_str, **kwargs )
        self.shortL = []
        self.longL = []

        # Sum of every elapsed time
        self.total_duration = 0

        # Number of times calculation of interval done
        self.time_stamps = 0
        self.avgTime = Stime( Stime.beginning )

        # Set string to minutes and seconds only
        self.str = self.str[7:]
        self.avgTime.str = self.avgTime.str[7:]


    def trackS( self ):
        self.shortL.append( time.time() )

        if len( self.shortL ) > 1:
            t = self.shortL
      
            self.seconds = int( t[1] - t[0] )
            
            if self.seconds > 40:
                self.total_duration += self.seconds
                
                self.time_stamps += 1
                self.calc_avg()

            self.to_str( self.seconds )

            # Set string to minutes and seconds only
            self.str = self.str[7:]
            self.avgTime.str = self.avgTime.str[7:]
            
            del t[0]


    def calc_avg( self ):
        self.avgTime.to_str( self.total_duration // self.time_stamps ) if self.time_stamps else None
        self.avgTime.to_seconds( self.avgTime.str )


if __name__=='__main__':
    pass


