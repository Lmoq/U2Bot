import subprocess, os
from pathlib import Path

os.system("adb devices")

cm = ["pgrep", "-fa", "adb shell|tail -f"]
result = subprocess.run( cm, stdout=subprocess.PIPE ).stdout.decode()

print( "Checking pipes..\n" )
print(result if result else "N/A")

if "adb shell" not in result and "tail -f" not in result:  
    print("Pipes not found")

    print("Starting pipes\n")

    p = Path(__file__).parent.parent
    os.system( p / "start_shell.sh")
    
    result = subprocess.run( cm, stdout=subprocess.PIPE ).stdout.decode()
    print(result)
else:
    print("Pipes found\n")

