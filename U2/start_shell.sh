tail -f /dev/null > '/data/data/com.termux/files/home/pipes/adbpipe' &
adb shell < '/data/data/com.termux/files/home/pipes/adbpipe' &
