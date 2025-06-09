import uiautomator2 as u2
import json as j, traceback, sys
import time, os, subprocess

from .process import start_adb_shell_pipes
from .debug import boxArea
from .actions import adbClick, vibrate

from threading import Thread
from .notif import notif, Tracker, Stime
from .debug import notif_
from .debug.log import NotifLog


class wtype:
    clickable = "android.widget.TextView"
    text = "android.view.ViewGroup"

class tasktype:
    t1 = 1
    t2 = 2
    check = 3
    wait = 4

elapsed = Tracker()
interval = Tracker()

class U2_Device:

    def __init__( self, **kwargs ):

        self.d = u2.connect()
        self.task = tasktype.t1

        self.prev_task = 1
        self.next_task = 1

        # App will not run on given time frame
        self.start: Stime = None
        self.end: Stime = None
        self.ignoretime = False

        # android.widget.TextView
        self.task1 = {
            # Dictionary containing questions as keys
            # and value as corresponding button name
        }
        # android.widget.TextView
        self.task2 = ""

        # android.view.ViewGroup
        self.question = ''
        self.check = self.task2
        self.check_timer = time.time()

        self.lastClick = {}
        self.lastCheckBounds = {}

        # UiObject
        self.qui = None
        
        # Bool
        self.running = True
        self.restart = False

        self.thread = None

        for k,v in kwargs.items():
            setattr( self, k, v )


    def waitElement( self, selector, timeout ):
        
        try:            
            ui = self.d( **selector )

            return ui \
            if ui.wait( timeout=timeout ) \
            else None
        
        except Exception as e:
            print(f"waitException : {e}")
            return 'FAILED'


    def getInfo( self, ui, log=False, text="" ):
        success = False
        
        retries = 0
        info = None
        
        while not success:
            try:
                info = ui.info
                success = True          
            except Exception:
                retries += 1
                if retries > NotifLog.gInfo:
                    NotifLog.gInfo = retries

        if log: notif_( 1, f"{text} info in {retries} retries" )
        return info


    def doTask1( self ):
        # Search task1 elements
        if self.qui != None:                
            gone = self.qui.wait_gone( timeout=500 )

            if not gone:
                info = self.getInfo( self.qui )

                notif_( 1, f"Last qui persisted[ {info['text'} ]" )
                vibrate( 1, 3 )

                boxArea( self.lastClick, "click" )
                time.sleep(1)
                boxArea( self.lastCheckBounds, "check" )
                time.sleep(1)
                boxArea( info['bounds'], "qui" )
                
                self.running = False
                self.qui = None

                return

        # Find question
        ui = self.waitElement( {"textContains" : self.question, "className" : wtype.text}, timeout=80 )
        
        if not ui or ui == "FAILED":
            notif_( 1, f"Find element timedout ui[ {ui}] ")
            NotifLog.timeout += 1
            return

        info = self.getInfo( ui )

        # Ignore still visible answered question
        if info.get('bounds').get('top') < 200:
            return

        # Question found
        text = self.task1[info['text']]
        
        start = time.time()
        ui = self.waitElement( {"text" : text, "className" : wtype.clickable}, timeout=4 )
        
        if not ui or ui == "FAILED":
            notif_( 1, f"{text} not found")
            return

        info = self.getInfo( ui )
        
        bounds = info['bounds']
        self.check = info['text']

        if self.check != text:
            notif_(1, f"Diff text[ {self.check} ]")   
            vibrate( 1, 2 )
            return

        adbClick( bounds )
        notif_( 1, f"Clicked[ {text} ] [ {elapsed.trackS()} ]")
        
        # Update task values
        self.prev_task = self.task
        self.next_task = tasktype.t2

        # Switch to check task
        self.task = tasktype.check


    def doTask2( self ):
        # Search task2 elements
        cui = self.waitElement( {"text" : self.task2, "className" : wtype.clickable }, timeout=80 ) 
        
        if not cui or cui == "FAILED":
            notif_(1, f"[ {self.task2} ] timedout")
            NotifLog.timeout += 1
            return

        info = self.getInfo( cui )

        bounds = info['bounds']
        self.check = info['text']

        if self.check != self.task2:
            notif_(1, f"Diff text[ {self.check} ]") 
            cui = None
            return

        # Click and update values
        adbClick( bounds )
        notif_( 1, f"Clicked[ {self.check} ] [ {interval.trackS()} ]")

        # Update task values
        self.prev_task = self.task
        self.next_task = tasktype.t1

        # Switch to check task
        self.task = tasktype.check
        self.lastClick = bounds


    def doCheck( self ):
        # Wait for ui to exists before switching task
        ui = self.waitElement( {"text" : self.check, "className" : wtype.text}, timeout=5 )
         
        if ui == None:
            NotifLog.recheck += 1
            notif_(1, f"Check failed:{self.check}")
            self.task = self.prev_task
            return

        elif ui == "FAILED":
            printf("Check element failed")
            return

        # Used check ui as wait ui due to immediate question appearance
        if self.prev_task == 1:
            self.qui = ui

        elif self.prev_task == 2:
            info = self.getInfo( ui )
            self.lastCheckBounds = info['bounds']
        
        notif_( 1, f"Checked[ {self.check} ] [ {elapsed.trackS()} ]")
        self.task = self.next_task


    def pipethread( self ):
        # Reads from pipe controlled by termux-notification
        pPath = "/data/data/com.termux/files/home/pipes/pipe" 
        while True:
            result = subprocess.run( f"cat {pPath}", shell=True, text=True, stdout=subprocess.PIPE ).stdout.strip()

            if result == '-1':
                notif_( 1, "Received exit signal")
                self.running = False
                break


    def mainloop( self ):
        while self.running:
            #if d.device_info.get('package') != 'com.facebook.orca':
                #continue
            try:
                match self.task: 
                    case tasktype.t1:
                        self.doTask1()

                    case tasktype.t2:
                        self.doTask2()

                    case tasktype.check:
                        self.doCheck()

            except Exception as e:

                #tb = traceback.extract_tb(e.__traceback__)[-1]
                #filename, lineno, func, text = tb
                #print(f"error: {e} (line {lineno} in {filename})")
                
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stdout)
                #vibrate(1, 3)


    def run( self ):
        # Only run app on allowed time frame
        if not self.ignoretime:
            stime = stime() 
            
            if stime.in_range( self.start, self.end ):
                w = f"'App prohibited running between\n[ {self.start} ] - [ {self.end}] '"
                
                print(w) 
                notif( content=w, pin=False, b1="''" )

                vibrate( 1, 1 )
                return

        # Start adb and pipes
        start_adb_shell_pipes()

        # run termux-notification with default args
        notif()

        # start main program
        pipe_t = Thread(target = self.pipethread)
        pipe_t.start()

        self.thread = Thread(target=self.mainloop, daemon=True)
        self.thread.start()

        # clean up external processes
        print(f"running[ {self.running} ]")
        pipe_t.join()
         
        print("Closing notif")
        os.system("termux-notification-remove 21")

if __name__=='__main__':
    u2 = u2_device()
    u2.task = 1
    u2.run()
