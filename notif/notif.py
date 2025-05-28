import os

def termux_notif( follow_default=True, **kwargs ):
    k_args = kwargs
    
    if follow_default:
        dict_ = {
            "--id"      : "'21'",
            "--title"   : "'U2 Running'",
            "--button1" : "'Exit'",
            "--button1-action" : "'echo -1 > ~/pipes/pipe'",
            "--priority" : "'high'",
            "-c"         : "'Log details'"
        }
        dict_.update(kwargs)
        #k_args = dict_

    cm = "termux-notification "

    for k,v in dict_.items():
        cm += f"{k} {v} "

    #print(cm)
    os.system(cm)


def notif( pin=True, fd=True, **d ):
    global follow_default
    
    follow_default = fd
    d=d
    
    d_sub = {
        "title" : "--title",
        "content" : "-c",
        "id" : "-id",
        "b1" : "--button1",
        "b2" : "--button2",
        "b3" : "--button3",
        "b1_action" : "--button1-action",
        "b2_action" : "--button2-action",
        "b3_action" : "--button3-action",
        "img" : "--image-path",
    }

    # mapKey converts the keys to
    # the coresponding termux notification arg
    # then set its value
    result = {}
    def mapKey( key, sub ):
        value = d.get( key )
        if value: result[sub] = value

    for k,v in d_sub.items():
        mapKey(k, v)

    if pin : result['--ongoing'] = ''
    
    termux_notif( fd, **result )

if __name__=='__main__':
    path = "/storage/emulated/0/VSCODE/CV/needle.png"
    notif(
        content="'Debug logs'",
        title = "Lmao",
        b1_action = "'termux-notification-removeb21'"
    )



    
