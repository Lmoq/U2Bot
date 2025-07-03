import time, sys, os, json
import uiautomator2 as u2
from threading import Thread

from U2 import U2_Device as U2
from U2.U2 import tasktype
from U2.notif import Stime
from U2.actions import adbClickNoUi, vibrate, buttonInstance

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
BotDis = []
BotJson = {}


class Bot_Handler:

    def __init__( self, Bot : U2 ):
        self.bot = Bot
        
        self.name = ""
        self.key_name = ""
        self.instance_num = 0

        # Time interval
        self.task1 = 0
        self.task2 = 0

        # Next activity time stamp
        self.next = 0

    def __repr__( self ):
        return self.name


def getJsonInfo( botList, botJson ):
    # Extract runtime info from bots
    key_json = {
        "task" : 0.0,
        "points" : 0.0,
        "points_limit" : (1,2),
        "restricted" : False,
    }
    for b in botList:
        key = b.key_name
        
        # Fill dict value of unassigned key
        if not key in botJson:
            botJson[ key ] = {}
            
        contents = botJson[ key ]
        contents |= key_json

        # Update
        for k in contents.keys():
            contents[ k ] = b.bot.__dict__[ k ]


def saveJson( botList ):
    # Save updated data base
    global BotJson

    # Use dict.update so keys stays in place
    getJsonInfo( botList, BotJson ) 
    with open( 'data.json', 'w' ) as f:
        json.dump( BotJson, f, indent=4 )

    print( "\n", BotJson )


def loadJson( BotList ):
    # Load data base
    global BotJson

    if not os.path.exists( 'data.json' ):
        # Fill data base contents
        saveJson( BotList )
        print( 'Created data.json' )
    else:
        with open( 'data.json', 'r' ) as f:
            BotJson = json.load( f )
        print( 'Existing data loaded' )


def updatenotif( BotList, ext="" ):
    # Log future time string
    strings = []
    for bot in BotList:

        timestr = time.strftime( "%H:%M:%S", time.localtime( bot.next ) )
        strings.append( f"{bot.name} • {timestr} • {bot.bot.interval.avgTime} • {bot.bot.points:.2f} • {bot.bot.task}" )
    
    # Replace notiflog list 
    notiflog.list = strings
    NotifLog.title = f'U2 | RC : {NotifLog.recheck} | GI : {NotifLog.gInfo} | RS : {NotifLog.restarts}'

    cm = f'''echo 'cmd notification post -S inbox {notiflog} -t "{NotifLog.title}" notif logs &> /dev/null' > ~/pipes/adbpipe'''
    os.system(cm)


def switchInstance( num = 0, noUi:tuple = None, pressBack = True ):
    global device

    if pressBack: os.system( "echo 'input keyevent 4' > ~/pipes/adbpipe" )
    time.sleep(0.7)

    if noUi:
        adbClickNoUi( noUi )
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
    global running, device, BotList, BotJson, BotDis
    
    # Bots classes 
    CECB.points_increment = 0.50 
    CECB.points_limit = 100 
    # ---------------------

    FBMB.points_increment = 0.10
    FBMB.points_limit = 35 
    # ---------------------
    
    MMCB.points_increment = 0.05 
    MMCB.points_limit = 50
    # ---------------------
    
    # Random rate will not calc points
    DMCB.points_increment = 0
    DMCB.points_limit = 50
    # ---------------------
    

    # Handlers
    # Bot 1 --------------
    B1 = Bot_Handler( CECB )

    B1.task1 = 368
    B1.task2 = 369
    B1.name = "💙CECB💙"
    B1.key_name = "CECB"
    # --------------------

    # Bot 2 --------------
    B2 = Bot_Handler( FBMB )
    
    B2.task1 = 258
    B2.task2 = 259
    B2.name = "🌸FBMB🌸"
    B2.key_name = "FBMB"
    # --------------------

    # Bot 3 --------------
    B3 = Bot_Handler( MMCB )
    
    B3.task1 = 139
    B3.task2 = 139
    B3.name = "💫MMCB💫"
    B3.key_name = "MMCB"
    # --------------------
    
    # Bot 4 --------------
    B4 = Bot_Handler( DMCB )
    
    B4.task1 = 252
    B4.task2 = 302
    B4.name = "🌟DMCB🌟"
    B4.key_name = "DMCB"
    # --------------------

    tmp = [ B1, B2, B4 ]

    tmp[0].bot.button_instance = buttonInstance.i3
    tmp[1].bot.button_instance = buttonInstance.i4
    tmp[2].bot.button_instance = buttonInstance.i5

    BotList = []

    # Load data base
    loadJson( tmp )

    for bot in tmp:
        # Set bot atrributes based from db
        jsonInfo = BotJson[ bot.key_name ]
        bot.bot.__dict__ |= jsonInfo

    # Setup bots to run
    for bot in tmp:
        # Include only non restricted Bots 
        if bot.bot.timeRestricted() or bot.bot.restricted:
            continue

        # Share single device
        bot.d = device

        # Set universal properties for multi bot
        bot.bot.tag = bot.name
        
        bot.bot.multi_bot = True
        bot.bot.task_points_add = tasktype.t1

        # Add to botlist if not time restricted
        BotList.append( bot )

    if BotList: Bot = BotList[0]
    del tmp

    # Main loop
    while BotList and not U2.sig_term:
        try:
            # Display latest notif update
            updatenotif( BotList )

            # Every bots' self.check self.running will be 
            # disabled to allow others to run 
            Bot.bot.running = True
            Bot.bot.mainloop()
 
            if U2.sig_term:
                print("Sigterm")
                continue

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
                    
                    # Move bot from discarded list
                    BotDis.append( BotList.pop( 0 ) )
                    next_bot = BotList[0]

                    vibrate( 2, 1 )
                    if not BotList: break 
 
                # Check interval limit
                restarted = False
                
                if not Bot.bot.restricted and Bot.bot.intervalExceed():
                    # Restart app w/o click depending on next bot
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
            running = False
            break

def main():
    global BotList, BotDis
    
    # Start adb shell pipe
    start_adb_shell_pipes()

    NotifLog.capacity = 7
    altRun()
    
    #start_adb_shell_pipes()
    notif_( 1, "No bots running" )

    # Save data base
    BotList.extend( BotDis )
    saveJson( BotList )

if __name__=='__main__':
    main()
