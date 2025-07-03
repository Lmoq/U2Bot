import uiautomator2 as u2
import json as j, traceback, sys
import time, os, subprocess

from .process import start_adb_shell_pipes
from .debug import boxArea
from .actions import adbClick, adbClickNoUi, vibrate, buttonInstance

from threading import Thread
from .notif import notif, Tracker, Stime
from .debug import notif_
from .debug.log import NotifLog


class wtype:
    clickable = "android.widget.TextView"
    text = "android.view.ViewGroup"
    button = "android.widget.Button"

class tasktype:
    t1 = 1
    t2 = 2
    check = 3
    wait = 4


class U2_Device:

    sig_term = False

    def __init__( self, **kwargs ):
        
        self.tag = ""
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
        self.task2_px_max = 0
        self.task2_timeout = 400

        # android.view.ViewGroup
        self.question = ''
        self.question_timeout = 400

        self.check = self.task2
        self.check_timer = time.time()

        # Track points
        self.points = 0
        self.task_points_add = 0

        self.points_increment = 0
        self.points_limit = 99

        # Last click and check ui bounds
        self.lastClick = {}
        self.lastCheckBounds = {}

        # Time trackers
        self.elapsed = Tracker()
        self.interval = Tracker( 40 )
        
        # Restart max time
        self.restart_time = 0
        self.button_instance_num = 3
        self.button_instance = buttonInstance.i3
        
        # Wait gone UiObject
        self.qui = None
        
        # Bool
        self.running = True
        self.multi_bot = False
        
        self.restart = False
        self.restricted = False

        for k,v in kwargs.items():
            setattr( self, k, v )


    def waitElement( self, selector, timeout ):
        # Wait until ui element exists then returns uiobject
        try:            
            ui = self.d( **selector )

            return ui \
            if ui.wait( timeout=timeout ) \
            else None
        
        except Exception as e:
            print(f"waitException : {e}")
            return 'FAILED'


    def getInfo( self, ui ):
        success = False
        
        retries = 0
        info = None
        
        while not info:
            try:
                info = ui.info       
            except Exception:
                retries += 1
                if retries > NotifLog.gInfo:
                    NotifLog.gInfo = retries

        return info


    def doTask1( self ):
        # Search task1 elements
        if self.qui != None:                
            gone = self.qui.wait_gone( timeout=600 )

            if not gone:
                info = self.getInfo( self.qui )
                notif_( 1, f"Last qui persisted[ {info['text']} ]" )
                 
                self.running = False
                self.qui = None

                vibrate( 1, 3 )
                return

        # Find question
        ui = self.waitElement( {"textContains" : self.question, "className" : wtype.text}, timeout=self.question_timeout )
        
        if not ui or ui == "FAILED":
            notif_( 1, f"Question e[ {ui} ] ")
            NotifLog.timeout += 1
            return

        info = self.getInfo( ui )

        # Ignore still visible answered question
        if info.get('bounds').get('top') < 200:
            return

        # Question found
        text = self.task1[info['text']]
        
        start = time.time()
        ui = self.waitElement( {"text" : text, "className" : wtype.clickable}, timeout=6 )
        
        if not ui or ui == "FAILED":
            notif_( 1, f"{text} not found")
            return

        info = self.getInfo( ui )
        
        bounds = info['bounds']
        self.check = info['text']

        if self.check != text:
            notif_(1, f"Diff text[ {self.check} ]")   
            return

        adbClick( bounds )

        # Track time self.interval of each action
        self.elapsed.trackS()
        notif_( 1, f"Clicked[ {text[:9]} ] [ {self.elapsed} ]")
        
        # Update task values
        self.prev_task = self.task
        self.next_task = tasktype.t2

        # Switch to check task
        self.task = tasktype.check
        self.lastClick = bounds


    def doTask2( self ):
        # Search task2 elements
        cui = self.waitElement( {"text" : self.task2, "className" : wtype.clickable }, timeout=self.task2_timeout ) 
        
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

        if bounds['left'] > self.task2_px_max:
            boxArea( bounds, "OB", False )
            print(f"Bounds went off limit :\n{bounds}")
            return

        adbClick( bounds )
        
        # Track cycle duration
        self.interval.trackS()

        # Log average time self.interval per cycle
        NotifLog.total_duration = self.interval.avgTime
        notif_( 1, f"Clicked[ {self.check[:9]} ] [ {self.interval} ]")

        # Update task values
        self.prev_task = self.task
        self.next_task = tasktype.t1

        # Switch to check task
        self.task = tasktype.check
        self.lastClick = bounds


    def doCheck( self ):
        # Wait for ui to exists before switching task
        ui = self.waitElement( {"text" : self.check, "className" : wtype.text}, timeout=3 )
         
        if ui == None:
            NotifLog.recheck += 1
            notif_(1, f"Check failed:{self.check[:9]}")

            self.task = self.prev_task
            return

        elif ui == "FAILED":
            printf("Check element failed")
            return

        self.elapsed.trackS()

        if self.prev_task == 1:
            # Use check ui as waitGone ui
            # to be used as signal to look
            # for new question ui since multiple
            # question ui exists at the instant search action is on 
            self.qui = ui

        # Increment points at specific task cycle
        if self.prev_task == self.task_points_add:
            self.incrementPoints()

        self.task = self.next_task
        notif_( 1, f"Checked[ {self.check[:9]} ] [ {self.elapsed} ]")

        # Avoid self checks with early return for multi bot version
        if self.multi_bot:
            self.running = False
            return

        # Restart app if self.interval take longer than usual
        if self.intervalExceed():
            self.restartTarget( noUi = self.button_instance )


    def incrementPoints( self ):
        # Update points
        self.points = round( self.points + self.points_increment, 2 )


    def pointsReachedLimit( self ):
        if self.points >= self.points_limit:
            return True

        return False


    def intervalExceed( self ) -> bool:
        # Check if average interval takes longer time than usual
        if self.interval.avgTime.seconds > self.restart_time:
            return True
        return False


    def restartTarget( self, instance_number = 0, noUi:tuple = None, click=True ):
        # Force stop and reopen target app
        # when interval time exceeds average time
        os.system( "adb shell am force-stop com.facebook.orca; sleep 0.4; adb shell am start -n com.facebook.orca/.auth.StartScreenActivity &> /dev/null" )
        time.sleep( 1.5 )

        # Reset tracker
        self.interval.reset_avg()
        
        # Log
        NotifLog.restarts += 1

        if not click:
            # Used for multi bot
            return

        if noUi:
            adbClickNoUi( noUi )
            return

        ui = None
        while ui is None:
            try:
                # Messenger chat tabs' className is wtype.button
                ui = self.d( className = wtype.button, instance = instance_number )
            except:
                continue

        info = self.getInfo( ui )
        bounds = info['bounds']

        adbClick( bounds )


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

                # Restriction checks
                if self.pointsReachedLimit() or self.timeRestricted(): 
                    self.restricted = True
                    break

            except Exception as e:

                #tb = traceback.extract_tb(e.__traceback__)[-1]
                #filename, lineno, func, text = tb
                #print(f"error: {e} (line {lineno} in {filename})")
                
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stdout)
                #vibrate(1, 3)
            except KeyboardInterrupt:
                U2_Device.sig_term = True
                break


    def timeRestricted( self ):
        # Checks if runs at vslid time
        stime = Stime()

        if stime.in_range( self.start, self.end ):
            return True
        
        return False


    def run( self ):
        # Only run app on allowed time frame
        if not self.ignoretime and self.timeRestricted():
            
            w = f'App prohibited running between'
            w1 = f'[ {self.start} ] - [ {self.end}] '
            
            notif_( 0, w )
            notif_( 0, w1 )
            
            vibrate( 1, 1 ) 
            return

        # Start adb and pipes
        start_adb_shell_pipes()

        # start main program
        self.mainloop()
        print("Closing app")

if __name__=='__main__':
    u2 = u2_device()
    u2.task = 1
    u2.run()
