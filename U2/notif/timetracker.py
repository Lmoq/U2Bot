import time
from .stime import Stime


class Tracker( Stime ):

    def __init__( self, time_str:str="", **kwargs ):
        super().__init__( time_str, **kwargs )
        self.shortL = []
        self.longL = []

        self.trackStr = ""
        self.avgStr = ""
        # Sum of every elapsed time
        self.total_duration = 0

        # Number of times calculation of interval done
        self.time_stamps = 0


    def trackS( self ):
        self.shortL.append( time.time() )

        if len( self.shortL ) > 1:
            t = self.shortL
      
            self.seconds = int( t[1] - t[0] )
            
            if self.seconds > 100:
                self.total_duration += self.seconds
                self.time_stamps += 1
            
            self.to_str( self.seconds )
            del t[0]

            self.trackStr = f"{self.str}"[7:]


    def get_avg( self ):
        self.to_str( self.total_duration // self.time_stamps ) if self.time_stamps else None
        self.avgStr = f"{self.str}"[7:]


if __name__=='__main__':
    t = Tracker()
    print(f"[ {t.trackS()} ]")
    time.sleep(1)
    print(f"[ {t.trackS()} ]")
    


