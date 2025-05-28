import uiautomator2 as u2
import json as j, traceback
import time, os, subprocess

from .process import pipes # Start adb and pipes
from .debug.snip import boxArea
from .actions.actions import adbClick

from threading import Thread
from .notif.notif import notif
from .debug.log import printf


class wtype:
    clickable = "android.widget.TextView"
    text = "android.view.ViewGroup"

class tasktype:
    t1 = 1
    t2 = 2
    check = 3
    wait = 4


class U2_Device:

    def __init__( self ):

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


    def waitElement( self, selector, timeout ):
        ui = self.d( **selector )

        return ui \
        if ui.wait( timeout=timeout ) \
        else None


    def doTask1( self ):
        # Search task1 elements
        try:
            if self.qui != None:
                
                print(f"Wait gone[{self.qui.info['text']}]")
                gone = self.qui.wait_gone( timeout=50 )

                if not gone:
                    boxArea( self.qui.info['bounds'] )
                    printf(f"Last qui persisted\n{self.qui.info}")
                    running = False

                    return

        except Exception as e:
            print("WaitObject out of visibility\n")        

        print(f"Finding question")
        
        ui = self.waitElement( {"textContains" : self.question, "className" : wtype.text}, timeout=60 )
        
        if not ui:
            print("Find element timedout\n")
            return

        info = ui.info

        if info.get('bounds').get('top') < 200:
            print("Wrong q found")
            return

        text = self.task1[info['text']]
        print(f"Found question for[ {text} ]\nQuestion:{ui.info['text']}")
        
        start = time.time()
        ui = self.waitElement( {"text" : text, "className" : wtype.clickable}, timeout=4 )
        
        if not ui:
            print(f"Clickable not found[ {text} ]\n")
            return

        info = ui.info
        
        bounds = info['bounds']
        self.check = info['text']

        if self.check != text:
            print(f"Wrong element found[{self.check}]\n")
            return

        #boxArea( bounds )   
        adbClick( bounds )

        printf(f"Clicked[ {text} ]")
        
        # Update task values
        self.prev_task = self.task
        self.next_task = tasktype.t2

        # Switch to check task
        self.task = tasktype.check


    def doTask2( self ):
        # Search task2 elements
        try:
            print(f"Finding {self.task2} clickable")
            cui = self.waitElement( {"text" : self.task2, "className" : wtype.clickable }, timeout=60 ) 
            
            if not cui:
                printf(f"[ {self.task2} ] timedout")
                return

        except Exception:
            print("T2 Clikable Not found")
            time.sleep(2)

        info = cui.info

        bounds = info['bounds']
        self.check = info['text']

        #boxArea(bounds)
        print(f"Found clickable[{info['text']}]\n")

        if self.check != self.task2:
            print(f"Wrong element found[{self.check}]\n")
            cui = None
            return
        
        # Click and update values
        #boxArea( bounds )
        adbClick( bounds )
        printf(f"Clicked[ {self.check} ]")

        # Update task values
        self.prev_task = self.task
        self.next_task = tasktype.t1

        # Switch to check task
        self.task = tasktype.check


    def doCheck( self ):
        # Wait for ui to exists before switching task        
        ui = self.waitElement( {"text" : self.check, "className" : wtype.text}, timeout=20 )
        
        if not ui:
            printf("Check element not found[ {self.check} ]\nSwitched to task{self.prev_task}")
            self.task = self.prev_task
            return

        # Used check ui as wait ui due to immediate question appearance
        if self.prev_task == 1:
            self.qui = ui

        printf(f"Checked[ {self.check} ]\n")
        self.task = self.next_task


    def pipethread( self ):
        # Reads from pipe controlled by termux-notification
        while True:
            print("Receiving pipe")

            result = subprocess.run([
                "cat", "/data/data/com.termux/files/home/pipes/pipe"],
                stdout=subprocess.PIPE
            )
            string = result.stdout.decode().strip()

            if string == '-1':
                print("Received ping")
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
                
                print(f"Error: {e} (line {lineno} in {filename})")
                time.sleep(2)


    def start( self ):
        # Start main program
        pipe_t = Thread(target = self.pipethread)
        pipe_t.start()

        self.thread = Thread(target=self.mainloop, daemon=True)
        self.thread.start()

        # Clean up external processes
        print("Mainloop started")
        pipe_t.join()

    def run( self ):
        # Run termux-notification with default args
        notif()

        self.start() 
        print("Closing notif")

        os.system("termux-notification-remove 21")

if __name__=='__main__':
    u2 = U2_Device()
    u2.task = 1
    u2.run()
