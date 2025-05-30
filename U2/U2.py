import uiautomator2 as u2
import json as j, traceback
import time, os, subprocess

from .process import start_adb_shell_pipes
from .debug import boxArea
from .actions import adbClick

from threading import Thread
from .notif import notif, Tracker
from .debug import notif_


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

        # UiObject
        self.qui = None
        
        # Bool
        self.running = True
        self.restart = False

        self.thread = None

        for k,v in kwargs.items():
            setattr( self, k, v )


    def waitElement( self, selector, timeout ):
        ui = self.d( **selector )

        return ui \
        if ui.wait( timeout=timeout ) \
        else None


    def doTask1( self ):
        # Search task1 elements
        try:
            if self.qui != None: 
                
                gone = self.qui.wait_gone( timeout=300 )

                if not gone:
                    boxArea( self.qui.info['bounds'] )
                    notif_( 1, f"Last qui persisted[ {self.qui} ]" )
                    
                    self.running = False
                    self.qui = None
                    return

        except Exception as e:
            # print("WaitObject out of visibility\n")
            pass
        # Find question
        ui = self.waitElement( {"textContains" : self.question, "className" : wtype.text}, timeout=400 )
        
        if not ui:
            notif_( 1, "Find element timedout\n")
            return

        info = ui.info

        # Ignore still visible answered question
        if info.get('bounds').get('top') < 200:
            return

        # Question found
        text = self.task1[info['text']]
        
        start = time.time()
        ui = self.waitElement( {"text" : text, "className" : wtype.clickable}, timeout=4 )
        
        if not ui:
            return

        info = ui.info
        
        bounds = info['bounds']
        self.check = info['text']

        if self.check != text:
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
        try:
            cui = self.waitElement( {"text" : self.task2, "className" : wtype.clickable }, timeout=410 ) 
            
            if not cui:
                notif_(1, f"[ {self.task2} ] timedout")
                return

        except Exception:
            print("T2 Clikable Not found")
            time.sleep(2)

        info = cui.info

        bounds = info['bounds']
        self.check = info['text']

        if self.check != self.task2:
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


    def doCheck( self ):
        # Wait for ui to exists before switching task
        ui = self.waitElement( {"text" : self.check, "className" : wtype.text}, timeout=10 )
        
        if not ui:
            # Double check
            ui = self.waitElement( {"text" : self.check, "className" : wtype.text}, timeout=0.1 )
        
        if not ui:
            boxArea( None )
            self.task = self.prev_task 
            return

        # Used check ui as wait ui due to immediate question appearance
        if self.prev_task == 1:
            self.qui = ui

        notif_( 1, f"Checked[ {self.check} ] [ {elapsed.trackS()} ]")
        self.task = self.next_task


    def pipethread( self ):
        # Reads from pipe controlled by termux-notification
        pPath = "/data/data/com.termux/files/home/pipes/pipe"
        with open( pPath, 'r' ) as pipe:

            while True:
                print("Receiving pipe")
                string = pipe.readline().strip()

                if string == '-1':
                    print("Received Exit signal")
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

                tb = traceback.extract_tb(e.__traceback__)[-1]
                filename, lineno, func, text = tb
                
                # print(f"Error: {e} (line {lineno} in {filename})")
                time.sleep(2)


    def run( self ):
        # Start adb and pipes
        start_adb_shell_pipes()
        
        # Run termux-notification with default args
        notif()

        # Start main program
        pipe_t = Thread(target = self.pipethread)
        pipe_t.start()

        self.thread = Thread(target=self.mainloop, daemon=True)
        self.thread.start()

        # Clean up external processes
        print(f"Running[ {self.running} ]")
        pipe_t.join()
         
        print("Closing notif")
        os.system("termux-notification-remove 21")

if __name__=='__main__':
    u2 = U2_Device()
    u2.task = 1
    u2.run()
