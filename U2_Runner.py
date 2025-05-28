import os, subprocess, time
import uiautomator2 as u2

from U2.U2 import U2Run, tasktype
from .notif.notif import notif

from multiprocessing import Queue, Process
from threading import Thread


class U2_Runner:

    def __init__( self, **kwargs ):
       
        self.question = ""
        self.task1 = {}

        self.task2 = ""
        self.queue = Queue( maxsize=1 )
        
        self.taskQueue = Queue( maxsize=1 )
        self.restart = False

        self.taskD = {}
        self.task = 1

        for k,v in kwargs.items():
            setattr( self, k, v )
    

    def pipethread( self ):
        # Reads from pipe controlled by termux-notification
        pPath = "/data/data/com.termux/files/home/pipes/pipe"
        with open( pPath, 'r' ) as pipe:
            
            while True:
                string = pipe.readline().strip()

                if string == '-1':
                    self.restart = False
                    self.queue.put( True )
                    break

                elif string == '10':
                    self.restart = True
                    self.queue.put( "switch" )
            

    def start( self ):
        # Run termux-notification with default args
        notif()
        device = u2.connect()

        thread = Thread( target=self.pipethread )
        thread.start()

        while True:
            print(f"Restarting proc with task{self.task}")
            data = (
                device, self.task, self.task1,
                self.task2, self.question,
                self.queue, self.taskQueue
            )

            proc = Process( target=U2Run, args=(data,) )
            proc.start()
            
            self.taskD = self.taskQueue.get()

            if not self.restart:
                break

            print("Received switch signal")
            task = self.taskD['task']
            
            if task == tasktype.check:
                self.task = self.taskD['next_task']
            else:
                self.task = 1 if task == 2 else 2
            
            notif( b2 = f"'Switch Task[ {self.task} ]'" )

        thread.join()

        os.system("termux-notification-remove 21")
        pass

if __name__=='__main__':
    pass
