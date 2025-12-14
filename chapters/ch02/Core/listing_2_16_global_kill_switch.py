import threading, time

class KillSwitch:
    def __init__(self):
        self.active = False
    def monitor(self):
        while True:
            cmd = input("[KillSwitch] Type 'STOP' to abort: ")
            if cmd.strip().upper() == "STOP":
                self.active = True
                print("[KillSwitch] Aborting all agents.")
                break
