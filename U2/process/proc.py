from multiprocessing import Process, Queue
from threading import Thread as T

def watcher( wq ):
    flag = wq.get()
    if flag:
        print("One of threads done")

def split_task( _dict, func, queue ):
    wq = Queue( maxsize=1 )
    ths = []

    wThread = T( target=watcher, args=(wq,), daemon=True )
    wThread.start()

    for k in _dict.keys():
        t = T( target=func, args=(k, queue, wq), daemon=True )
        ths.append( t )
        t.start()

    for t in ths:
        t.join()
    
    # Signal exit for watcher
    wq.put( True )
    queue.put( None )

    wThread.join()

def proc_waitElement( _dict, func, queue ):
    p = Process( 
        target=split_task,
        args=( _dict, func, queue )
    )
    p.start()
    p.join()

    print("Process done")




