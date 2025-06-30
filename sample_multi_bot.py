import time, sys, os
import uiautomator2 as u2
from threading import Thread

from U2 import U2_Device as U2
from U2.U2 import tasktype
from U2.notif import Stime
from U2.actions import adbClickNoUi, vibrate
from U2.U2 import wtype
from U2.debug.log import NotifLog, notiflog
from U2.debug import notif_
from U2.process import start_adb_shell_pipes
from U2.actions import adbClick

from pathlib import Path
path = Path(__file__).resolve().parent.parent

sys.path.append( str(path) )

from cecb.main import CECB
from fbmb.main import FBMB
from mmcb.main import MMCB
from dmcb.main import DMCB

device = u2.connect()

running = True
BotList = []


class Bot_Handler:

    def __init__( self, Bot : U2 ):
        self.bot = Bot
        
        self.name = ""
        self.instance_num = 0

        # Time interval
        self.task1 = 0
        self.task2 = 0

        # Next activity time stamp
        self.next = 0

    def __repr__( self ):
        return self.name


def updatenotif( BotList ):
    # Log future time string
    strings = [] 
    for bot in BotList:

        timestr = time.strftime( "%H:%M:%S", time.localtime( bot.next ) )
        strings.append( f"[ {bot.name} ] [ {timestr} ] [ {bot.bot.points:.2f} ]" )
        
        # Replace notiflog list
        notiflog.list = strings

    NotifLog.title = f'U2 | RC : {NotifLog.recheck} | DR : {NotifLog.total_duration} | RS : {NotifLog.restarts}'

    cm = f'''echo 'cmd notification post -S inbox {notiflog} -t "{NotifLog.title}" notif logs &> /dev/null' > ~/pipes/adbpipe'''
    os.system(cm)


def switchInstance( num = 0, noUi:tuple = None, pressBack = True ):
    global device

    if pressBack: os.system( "echo 'input keyevent 4' > ~/pipes/adbpipe" )
    time.sleep(0.7)

    if noUi:
        adbClickNoUi( noUi )
        return

    return
    ui = None

    while ui is None:
        try:
            # Messenger chat tabs' className is wtype.button
            ui = device( className = wtype.button, instance = num )
        
        except Exception as e:
            print(e)
            continue

    info = None

    while not info:
        try:
            info = ui.info

        except Exception:
            continue

    bounds = info['bounds']
    adbClick( bounds )   


def altRun():
    global running, device, BotList
    
    # Bots
    CECB.task = 1
    CECB.restricted = False

    CECB.points = 52.50
    CECB.points_limit = 100
    CECB.points_increment = 0.50
    # ---------------------

    FBMB.task = 1
    FBMB.restricted = False

    FBMB.points = 25.90
    FBMB.points_limit = 35
    FBMB.points_increment = 0.10
    # ---------------------
    
    MMCB.task = 1
    MMCB.restricted = False
        
    MMCB.points = 43.5
    MMCB.points_limit = 43.55
    MMCB.points_increment = 0.05
    # ---------------------
    
    DMCB.task = 1
    DMCB.restricted = True

    # Random rate will not calc points
    DMCB.points_increment = 0
    # ---------------------
    

    # Handlers
    # Bot 1 --------------
    B1 = Bot_Handler( CECB )

    B1.task1 = 368
    B1.task2 = 369
    B1.name = "💙CECB💙"
    # --------------------

    # Bot 2 --------------
    B2 = Bot_Handler( FBMB )
    
    B2.task1 = 258
    B2.task2 = 259
    B2.name = "🌸FBMB🌸"
    # --------------------

    # Bot 3 --------------
    B3 = Bot_Handler( MMCB )
    
    B3.task1 = 139
    B3.task2 = 139
    B3.name = "💫MMCB💫"
    # --------------------
    
    # Bot 4 --------------
    B4 = Bot_Handler( DMCB )
    
    B4.task1 = 252
    B4.task2 = 302
    B4.name = "🌟DMCB🌟"
    # --------------------

    tmp = [ B1, B2, B3, B4 ]
    BotList = []


    for bot in tmp:
        # Include only non restricted Bots 
        if bot.bot.timeRestricted() or bot.bot.restricted:
            continue

        # Share single device
        bot.d = device

        # Set properties for multi bot
        bot.bot.tag = bot.name
        bot.bot.multi_bot = True
        bot.bot.task_points_add = tasktype.t2

        # Add to botlist if not time restricted
        BotList.append( bot )

    if BotList: Bot = BotList[0]
    del tmp


    while BotList:
        try:
            # Display latest notif update
            updatenotif( BotList )

            # Every bots' self.check self.running will be 
            # disabled to allow others to run 
            Bot.bot.running = True
            Bot.bot.mainloop()

            # Get current task and estimated time wait
            task = Bot.bot.task
            interval = Bot.task1 if Bot.bot.task == 1 else Bot.task2

            allowance = 5
            Bot.next = time.time() + ( interval - allowance )

            # Choose the smallest time wait if all Bot had task and time wait done
            if all( b.next for b in BotList ):
                
                BotList = sorted( BotList, key=lambda b : b.next )
                next_bot = BotList[0]

                # Check next bot time restriction
                if next_bot.bot.restricted:
                    # Remove bot from list
                    BotList.pop( 0 )
                    next_bot = BotList[0]

                    vibrate( 2, 1 )
                    if not BotList: break 
 
                # Check interval limit
                restarted = False
                
                if not Bot.bot.restricted and Bot.bot.intervalExceed():
                    Bot.bot.restartTarget(
                        noUi = Bot.bot.button_instance,
                        click = False if Bot != next_bot else True
                    )
                    restarted = True
                    Bot.bot.interval.reset_avg()

                # Prevents calling switch instance if Bot reference did not change
                if Bot != next_bot:
                    Bot = next_bot 
                     
                    # Switch bot ui focus 
                    switchInstance( 
                        noUi = Bot.bot.button_instance,
                        pressBack = True if not restarted else False
                    )
                continue

            # Switch to other bot that has no next time stamp set
            for b in BotList:
                if not b.next:
                    Bot = b
                    # Switch bot ui focus
                    switchInstance( noUi = Bot.bot.button_instance )
                    break

        except KeyboardInterrupt:
            print("keyinterruot")
            running = False
            break

def main():
    # Start adb shell pipe
    start_adb_shell_pipes()

    NotifLog.capacity = len( BotList )
    altRun()
    
    NotifLog.capacity = 1
    notif_( 1, "No bots running" )
    
    print("No bots running")

if __name__=='__main__':
    main()
