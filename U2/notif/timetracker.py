import time
from .stime import Stime


class Tracker( Stime ):

    def __init__( self, time_str:str="", **kwargs ):
        super().__init__( time_str, **kwargs )
        self.shortL = []
        self.longL = []


    def trackS( self ):
        self.shortL.append( time.time() )     
        
        if len( self.shortL ) > 1:
            t = self.shortL

            stime = Stime( default=False )
            stime.seconds = int( t[1] - t[0] )

            stime.to_str( stime.seconds )
            del t[0]

            return f"{stime.str}"[7:]

        return "N/A"


if __name__=='__main__':
    t = Tracker()
    print(f"[ {t.trackS()} ]")
    time.sleep(1)
    print(f"[ {t.trackS()} ]")
    


