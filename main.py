import RPi.GPIO as GPIO
import time
import subprocess
import json
#from libs.dos_bluetooth import *
from libs.wifinetworks import *
from libs.mojstd import *
from libs.netstd import *

version = "M00N v1.0"
handshakes = 1
info = 0
INTERFACE = json.load(open("/root/M00N/settings/settings.json", "r"))["interface"]
interface = None
selected_index = 0

def bk():
    if GPIO.input(KEY3_PIN) == 0:
        time.sleep(0.2)
        return True

#MAX visible len messages = 18 letters
def draw_menu(selected_index=0, color=(100, 40, 237), offset=20):
    # Clear screen
    draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
    draw.text((5, 0), version, font=font, fill=(255, 0, 0))
    draw.rectangle((0, 12, width, 14), outline=0, fill=(2, 92, 72)) #bottom bar

    #IMPORTANT
    max_visible_options = 6

    # Offset
    scroll_offset = max(0, min(selected_index - max_visible_options + 1, len(menu_options) - max_visible_options))

    #IMPORTANT
    visible_options = menu_options[scroll_offset:scroll_offset + max_visible_options]

    # DRAW OPTIONS
    menu_offset = 16  # Offset
    for i, option in enumerate(visible_options):
        y = (i * 20) + menu_offset  # Space

        # highlight
        if scroll_offset + i == selected_index:
            text_size = draw.textbbox((0, 0), option, font=font)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]
            draw.rectangle((0, y, width, y + text_height+5), fill=color) #highlight
            draw.text((1, y), option, font=font, fill=(0, 0, 0))  # black text
        else:
            draw.text((1, y), option, font=font, fill=(255,255,255))# white text

    # Display the updated image
    disp.LCD_ShowImage(image, 0, 0)

def wifi_det(data, selected_ssid):
    for dict in data:
        if dict['ssid'] == selected_ssid:
            return {
                "Ssid": dict['ssid'],
                "Bssid": dict['bssid'],
                "Chan": dict['chan'],
                "Rate": dict['rate'],
                "Signal": dict['signal'],
                "Security": dict['security']
            }

#############################################################################################

                                        # THE WHILE#

#############################################################################################
show_image(r"/root/M00N/images/logo.png")
try:
    subprocess.run("sudo rm -rf /root/M00N/logs/*", shell=True)
    subprocess.run(f"sudo ifconfig {INTERFACE} up", shell=True)
except:
    pass
while True:
    menu_options = ["Wifi", "Bluetooth", "Settings", "Reboot", "Shutdown"]
    draw_menu(selected_index)
    if GPIO.input(KEY_UP_PIN) == 0:
        selected_index = (selected_index - 1) % len(menu_options)
        draw_menu(selected_index)
    elif GPIO.input(KEY_DOWN_PIN) == 0:
        selected_index = (selected_index + 1) % len(menu_options)
        draw_menu(selected_index)
    elif GPIO.input(KEY_PRESS_PIN) == 0:
        selected_option = menu_options[selected_index]
        if selected_option == "Wifi":

#WIFI
            time.sleep(0.20)
            while True:
                handshakes = 1
                menu_options = ["Sniffers", "Attacks", "Deauth", "Wps", "Connect"]
                draw_menu(selected_index)
                if GPIO.input(KEY_UP_PIN) == 0:
                    selected_index = (selected_index - 1) % len(menu_options)
                    draw_menu(selected_index)
                elif GPIO.input(KEY_DOWN_PIN) == 0:
                    selected_index = (selected_index + 1) % len(menu_options)
                    draw_menu(selected_index)
                elif bk():
                    break
                elif GPIO.input(KEY_PRESS_PIN) == 0:
                    selected_option = menu_options[selected_index]


    #HANDSHAKES INIZIALIZATION
                    if selected_option == "Connect":
                        ui_print("Connecting...")
                        with open("settings/settings.json", "r") as file:
                            data = json.load(file)
                            wifi = data["wifi"]
                            password = data["password"]
                        try:
                            time.sleep(1)
                            subprocess.run(f'sudo systemctl disable ssh.service && sudo systemctl enable ssh.socket', shell=True)
                            time.sleep(1)
                            subprocess.run(f'sudo nmcli device wifi connect {wifi} password {password}', shell=True)
                            ui_print("Connected", 2, (0, 255, 142))
                        except subprocess.CalledProcessError:
                            ui_print("""Error:
Unable to connect""", 2, (255, 0, 0))
                        break

                    elif selected_option == "Sniffers":
                        time.sleep(0.20)
                        while True:
                            menu_options = ["4-way handshake", "AP scan", "Raw Sniff"]
                            draw_menu(selected_index)
                            if GPIO.input(KEY_UP_PIN) == 0:
                                selected_index = (selected_index - 1) % len(menu_options)
                                draw_menu(selected_index)
                            elif GPIO.input(KEY_DOWN_PIN) == 0:
                                selected_index = (selected_index + 1) % len(menu_options)
                                draw_menu(selected_index)
                            elif bk():
                                break
                            elif GPIO.input(KEY_PRESS_PIN) == 0:
                                selected_option = menu_options[selected_index]
                                handshake = 1
                                if selected_option == "4-way handshake":
                                    ui_print("Loading...", "unset")
                                    wifi_info(INTERFACE).main()
                                    menu_options = []
                                    with open("wifiinfo.json", mode="r") as a:
                                        data = json.load(a)
                                    while handshakes == 1:
                                        for dict in data:
                                            menu_options.append(dict['ssid'])
                                        draw_menu(selected_index)
                                        if GPIO.input(KEY_UP_PIN) == 0:
                                            selected_index = (selected_index - 1) % len(menu_options)
                                            draw_menu(selected_index)

                                        elif GPIO.input(KEY_DOWN_PIN) == 0:
                                            selected_index = (selected_index + 1) % len(menu_options)
                                            draw_menu(selected_index)

                                        elif bk():
                                            break
                                        elif GPIO.input(KEY2_PIN) == 0:
                                            selected_ssid = menu_options[selected_index]
                                            wifi_details = wifi_det(data, selected_ssid)
                                            menu_options = [
                                                'Ssid:',
                                                f'{wifi_details["Ssid"]}',
                                                'Bssid:',
                                                f'{wifi_details["Bssid"]}',
                                                f'Channel: {wifi_details["Chan"]}',
                                                f'Rate: {wifi_details["Rate"]}',
                                                f'Signal: {wifi_details["Signal"]}',
                                                f'Security: {wifi_details["Security"]}',
                                                "Save info"
                                            ]
                                            while True:
                                                draw_menu(selected_index)
                                                if GPIO.input(KEY_UP_PIN) == 0:
                                                    selected_index = (selected_index - 1) % len(menu_options)
                                                    draw_menu(selected_index)
                                                elif GPIO.input(KEY_DOWN_PIN) == 0:
                                                    selected_index = (selected_index + 1) % len(menu_options)
                                                    draw_menu(selected_index)
                                                elif bk():
                                                    menu_options = []
                                                    selected_index = 0
                                                    break

                                        elif GPIO.input(KEY_PRESS_PIN) == 0:
                                            selected_ssid = menu_options[selected_index]
                                            wifi_details = wifi_det(data, selected_ssid)
                    #HANDSHAKE CAPTURE
                                            ui_print("Checking interface...", "unset")
                                            if netstd(INTERFACE).interface_select(INTERFACE) == 0:
                                                pass
                                            else:
                                                print(process)
                                                ui_print("""Error:
            Interface not Found
            Try to reboot M00N
            if the problem persist.""")
                                                break

                                            if netstd(INTERFACE).interface_start(INTERFACE) == 1:
                                                #ui_print("Going back...", 0.5)
                                                break

                                            time.sleep(1)
                                            ui_print(f"{INTERFACE} ready!", color=(0,255,142))
                                            ui_print("Loading...", "unset")
                                            menu_options = []
                                            selected_index = 0
                                            if bk() == True:
                                                netstd(INTERFACE).interface_stop(INTERFACE)
                                                #ui_print("Going back...", 0.5)
                                                break

                                            else:
                                                process = netstd(INTERFACE).initialization(wifi_details["Chan"], selected_ssid ,wifi_details["Bssid"], INTERFACE)
                                                while True:
                                                    time.sleep(0.5)
                                                    if process == 2:
                                                        ui_print("Error: Timeout", 2)
                                                        #ui_print("Going back...", 0.5)
                                                        handshakes = 0
                                                        break

                                                    elif process == 1:
                                                        ui_print("Going back...", 0.5)
                                                        menu_options = []
                                                        handshakes = 0
                                                        break

                                                    else:
                                                        handshakes = 0
                                                        break

                                elif selected_option == "AP scan":
                                    info = 0
                                    ui_print("Scanning APs...", "unset")
                                    wifi_info(INTERFACE).main()
                                    with open("wifiinfo.json", mode="r") as a:
                                        data = json.load(a)
                                    menu_options = []
                                    for dict in data:
                                        menu_options.append(dict['ssid'])
                                    while info == 0:
                                        draw_menu(selected_index)
                                        if GPIO.input(KEY_UP_PIN) == 0:
                                            selected_index = (selected_index - 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif GPIO.input(KEY_DOWN_PIN) == 0:
                                            selected_index = (selected_index + 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif bk():
                                            break
                                        elif GPIO.input(KEY_PRESS_PIN) == 0:
                                            selected_ssid = menu_options[selected_index]
                                            wifi_details = wifi_det(data, selected_ssid)
                                            menu_options = [
                                                f'Ssid: {wifi_details["Ssid"]}',
                                                f'Bssid: {wifi_details["Bssid"]}',
                                                f'Channel: {wifi_details["Chan"]}',
                                                f'Rate: {wifi_details["Rate"]}',
                                                f'Signal: {wifi_details["Signal"]}',
                                                f'Security: {wifi_details["Security"]}',
                                                "Save info"
                                            ]
                                            while True:
                                                draw_menu(selected_index)
                                                if GPIO.input(KEY_UP_PIN) == 0:
                                                    selected_index = (selected_index - 1) % len(menu_options)
                                                    draw_menu(selected_index)
                                                elif GPIO.input(KEY_DOWN_PIN) == 0:
                                                    selected_index = (selected_index + 1) % len(menu_options)
                                                    draw_menu(selected_index)
                                                elif bk():
                                                    info = 1
                                                    break
                                                elif GPIO.input(KEY_PRESS_PIN) == 0 and menu_options[selected_index] == "Save info":
                                                    ui_print("Saving info...", "unset")
                                                    with open(f'/root/M00N/Info/{wifi_details["Ssid"]}.txt', "w") as info:
                                                        info.write(str(menu_options))
                                                    ui_print("Info saved", 2, (0, 255, 142))
                                                    info = 1
                                                    break

                                elif selected_option == "Raw Sniff":
                                    ui_print("Loading...", "unset")
                                    wifi_info(INTERFACE).main()
                                    menu_options = []
                                    with open("wifiinfo.json", mode="r") as a:
                                        data = json.load(a)
                                    for dict in data:
                                        menu_options.append(dict['ssid'])
                                    while True:
                                        draw_menu(selected_index)
                                        if GPIO.input(KEY_UP_PIN) == 0:
                                            selected_index = (selected_index - 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif GPIO.input(KEY_DOWN_PIN) == 0:
                                            selected_index = (selected_index + 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif bk():
                                            break
                                        elif GPIO.input(KEY_PRESS_PIN) == 0:
                                            selected_ssid = menu_options[selected_index]
                                            wifi_details = wifi_det(data, selected_ssid)
                    #SNIFFING
                                            ui_print("Checking interface...", "unset")
                                            if netstd(INTERFACE).interface_select(INTERFACE) == 0:
                                                pass
                                            else:
                                                print(process)
                                                ui_print("""Error:
            Interface not Found
            Try to reboot M00N
            if the problem persist.""")
                                                break
                                            if netstd(INTERFACE).interface_start(INTERFACE) == 1:
                                                #ui_print("Going back...", 0.5)
                                                break

                                            time.sleep(1)
                                            ui_print(f"{INTERFACE} ready!", color=(0,255,142))
                                            ui_print("Loading...", 1)
                                            menu_options = []
                                            selected_index = 0
                                            if bk() == True:
                                                netstd(INTERFACE).interface_stop(INTERFACE)
                                                #ui_print("Going back...", 0.5)
                                                break

                                            else:
                                                process = netstd(INTERFACE).raw_sniff(selected_ssid, wifi_details["Bssid"], wifi_details["Chan"], INTERFACE)
                                                while True:
                                                    if process == 1:
                                                        ui_print("Going back...", 0.5)
                                                        handshakes = 0
                                                        break


    #DEAUTH ALL --> works
                    elif selected_option == "Deauth all":
                        pass


                #FAKE AP --> To improve
                    elif selected_option == 'Fake AP':
                        selected_index = 0
                        menu_options = ["Rickroll", "Evil Twin"]
                        time.sleep(0.20)
                        while True:
                            draw_menu(selected_index)
                            if GPIO.input(KEY_UP_PIN) == 0:
                                selected_index = (selected_index - 1) % len(menu_options)
                                draw_menu(selected_index)
                            elif GPIO.input(KEY_DOWN_PIN) == 0:
                                selected_index = (selected_index + 1) % len(menu_options)
                                draw_menu(selected_index)
                            elif bk():
                                break
                            elif GPIO.input(KEY_PRESS_PIN) == 0:
                                selected_option = menu_options[selected_index]
                    #RICKROLL
                                if selected_option == "Rickroll":
                                    ui_print("Wait please...")
                                    if netstd(INTERFACE).interface_select(INTERFACE) == 1:
                                        ui_print("""Error:
    Interface not Found""", 2 , (255,0,0))
                                    ui_print("Loading...", "unset")
                                    if netstd(INTERFACE).interface_start(INTERFACE) == 1: break
                                    ui_print(f"{INTERFACE} ready!", "unset", (0, 255, 142))
                                    nggup = netstd(INTERFACE).rickroll(INTERFACE)

                                    while True:
                                        if nggup == 1:
                                            ui_print("Going back...")
                                            break
                                        elif nggup == 2:
                                            ui_print("Error",2 ,(255,0,0))
                                            break


#EVIL TWIN
                    elif selected_option == "Evil Twin":
                        wifi_info(INTERFACE).main()
                        menu_options = []
                        with open("wifiinfo.json", mode="r") as a:
                            data = json.load(a)

                        dictdionary = {}

                        for item in data:
                            menu_options.append(item['ssid'])
                            dictdionary[item['ssid']] = item['bssid']
                            dictdionary[item['bssid']] = item['chan']
                        ui_print("Loading...", 0.5)
                        selected_index = 0
                        while True:
                            draw_menu(selected_index)
                            if GPIO.input(KEY_UP_PIN) == 0:
                                selected_index = (selected_index - 1) % len(menu_options)
                                draw_menu(selected_index)

                            elif GPIO.input(KEY_DOWN_PIN) == 0:
                                selected_index = (selected_index + 1) % len(menu_options)
                                draw_menu(selected_index)

                            elif bk():
                                break

                            elif GPIO.input(KEY_PRESS_PIN) == 0:
                                selected_option = menu_options[selected_index]
                                selected_bssid = dictdionary[selected_option]
                                selected_chan = dictdionary[selected_bssid]

                            ui_print("Wait please...", 0.5)

                            if netstd(INTERFACE).interface_select(INTERFACE) == 0:
                                pass

                            else:
                                ui_print(f"Error: Interface {INTERFACE} not found", 2)
                                if netstd(INTERFACE).interface_start1(INTERFACE) == 1:
                                    #ui_print("Going back...", 0.5)
                                    break

                            ui_print(f"{INTERFACE} ready!", 1, (0, 255, 142))
                            ui_print(f"""{selected_option}
    -
Evil Twin loading...""", 1)
                            ui_print(f"""Sniffing the real
{selected_option}""", 1)
                            while True:
                                ui_print("Press Key 3 to stop...")
                                if netstd(INTERFACE).evil_twin(INTERFACE, selected_option, selected_bssid, selected_chan) == 0:
                                    ui_print("""Evil Twin
            _
    Spoofing and Sniffing
        Stopped...""", 1)
                                    break


                    elif selected_option == "Attacks":
                        selected_index = 0
                        time.sleep(0.20)
                        menu_options = ["Deauth", "Wps"]
                        while True:
                            draw_menu(selected_index)
                            if GPIO.input(KEY_UP_PIN) == 0:
                                selected_index = (selected_index - 1) % len(menu_options)
                                draw_menu(selected_index)
                            elif GPIO.input(KEY_DOWN_PIN) == 0:
                                selected_index = (selected_index + 1) % len(menu_options)
                                draw_menu(selected_index)
                            elif bk():
                                break
                            elif GPIO.input(KEY_PRESS_PIN) == 0:
                                selected_option = menu_options[selected_index]
    #WPS ATTACKS --> To improve
                                if selected_option == "Deauth":
                                    ui_print("Loading...", "unset")
                                    wifi_info(INTERFACE).main()
                                    menu_options = []
                                    with open("wifiinfo.json", mode="r") as a:
                                        data = json.load(a)

                                    while True:
                                        for dict in data:
                                            menu_options.append(dict['ssid'])
                                        draw_menu(selected_index)
                                        if GPIO.input(KEY_UP_PIN) == 0:
                                            selected_index = (selected_index - 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif GPIO.input(KEY_DOWN_PIN) == 0:
                                            selected_index = (selected_index + 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif bk():
                                            break
                                        elif GPIO.input(KEY2_PIN) == 0:
                                            selected_ssid = menu_options[selected_index]
                                            wifi_details = wifi_det(data, selected_ssid)
                                            menu_options = [
                                                'Ssid:',
                                                f'{wifi_details["Ssid"]}',
                                                'Bssid:',
                                                f'{wifi_details["Bssid"]}',
                                                f'Channel: {wifi_details["Chan"]}',
                                                f'Rate: {wifi_details["Rate"]}',
                                                f'Signal: {wifi_details["Signal"]}',
                                                f'Security: {wifi_details["Security"]}',
                                                "Save info"
                                            ]

                                            while True:
                                                draw_menu(selected_index)
                                                if GPIO.input(KEY_UP_PIN) == 0:
                                                    selected_index = (selected_index - 1) % len(menu_options)
                                                    draw_menu(selected_index)
                                                elif GPIO.input(KEY_DOWN_PIN) == 0:
                                                    selected_index = (selected_index + 1) % len(menu_options)
                                                    draw_menu(selected_index)
                                                elif bk():
                                                    menu_options = []
                                                    selected_index = 0
                                                    break

                                        elif GPIO.input(KEY_PRESS_PIN) == 0:
                                            selected_ssid = menu_options[selected_index]
                                            wifi_details = wifi_det(data, selected_ssid)
                                            ui_print("Checking interface...", "unset")
                                            if netstd(INTERFACE).interface_select(INTERFACE) == 0:
                                                pass
                                            else:
                                                print(process)
                                                ui_print("""Error:
Interface not Found!""", 2 , (255,0,0))
                                                ui_print("""
Try to reboot M00N""", 1.5 , (255,0,0))
                                                break

                                            if netstd(INTERFACE).interface_start(INTERFACE) == 1:
                                                break

                                            time.sleep(1)
                                            ui_print(f"{INTERFACE} ready!", color=(0,255,142))
                                            ui_print("Loading...", "unset")
                                            menu_options = []
                                            selected_index = 0
                                            if bk() == True:
                                                netstd(INTERFACE).interface_stop(INTERFACE)
                                                break
                                            deauth = netstd(INTERFACE).deauth(wifi_details["Bssid"], INTERFACE)
                                            while True:
                                                if deauth == 1:
                                                    ui_print("Deauth stopped", 1)
                                                    break

                                elif selected_option == "Wps":
                                    selected_index = 0
                                    time.sleep(0.20)
                                    menu_options = ["Wps Pin Bruteforce", "Wps Pixie Dust"]
                                    while True:
                                        draw_menu(selected_index)
                                        if GPIO.input(KEY_UP_PIN) == 0:
                                            selected_index = (selected_index - 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif GPIO.input(KEY_DOWN_PIN) == 0:
                                            selected_index = (selected_index + 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif bk():
                                            break

                                        elif GPIO.input(KEY_PRESS_PIN) == 0:
                                            selected_option = menu_options[selected_index]
                                            ui_print("Wait please...", 0.5)

                                            if selected_option == "Wps Pin Bruteforce":
                                                wifi_info(INTERFACE).main()
                                                menu_options = []

                                                with open("wifiinfo.json", mode="r") as a:
                                                    data = json.load(a)

                                                dictdionary = {}

                                                for item in data:
                                                    menu_options.append(item['ssid'])
                                                ui_print("Loading...", 1)
                                                selected_index = 0
                                                while True:
                                                    draw_menu(selected_index)
                                                    if GPIO.input(KEY_UP_PIN) == 0:
                                                        selected_index = (selected_index - 1) % len(menu_options)
                                                        draw_menu(selected_index)
                                                    elif GPIO.input(KEY_DOWN_PIN) == 0:
                                                        selected_index = (selected_index + 1) % len(menu_options)
                                                        draw_menu(selected_index)
                                                    elif bk():
                                                        break
                                                    elif GPIO.input(KEY_PRESS_PIN) == 0:
                                                        selected_option = menu_options[selected_index]

                                                        ui_print("Wait please...", 0.75)
                                                        while True:
                                                            if netstd(INTERFACE, selected_option, 0).brute_force_wps(selected_option, INTERFACE) == 0:
                                                                pass


#################################################################################################################
#################################################################################################################
#################################################################################################################


#BLUETOOTH
#sudo systemctl enable bluetooth.service
#REBOOT
        elif selected_option == "Reboot":
            safe = time.time()
            while True:
                ui_print("""Hold KEY2
for 3 sec to
reboot.""", "unset")
                if GPIO.input(KEY2_PIN) == 0:
                    start_time = time.time()
                    while GPIO.input(KEY2_PIN) == 0:
                        if time.time() - start_time >= 3:
                            ui_print("Rebooting...", 1.5)
                            show_image(r"images/logo.png", "unset")
                            subprocess.run("sudo reboot", shell=True)
                            time.sleep(20)
                            break
                elif bk():
                    disp.LCD_Clear()
                    #ui_print("Going back...", 0.5)
                    break

                elif time.time() - safe >= 10:
                    ui_print("Timeout", 2 , (255, 0, 0))
                    disp.LCD_Clear()
                    #ui_print("Going back...", 0.5)
                    safe = None
                    break

#SHUTDOWN
        elif selected_option == "Shutdown":
            safe = time.time()
            while True:
                ui_print("""Hold KEY2
for 3 sec to
shutdown.""", "unset")
                if GPIO.input(KEY2_PIN) == 0:
                    start_time = time.time()
                    while GPIO.input(KEY2_PIN) == 0:
                        if time.time() - start_time >= 3:
                            ui_print("Shutting down...", 1.5)
                            disp.LCD_Clear()
                            show_image(r"images/logo.png", "unset")
                            subprocess.run("sudo shutdown now", shell=True)
                            time.sleep(20)
                            break

                elif bk():
                    disp.LCD_Clear()
                    #ui_print("Going back...", 0.5)
                    break

                elif time.time() - safe >= 10:
                    ui_print("Timeout", 2 , (255, 0, 0))
                    disp.LCD_Clear()
                    #ui_print("Going back...", 0.5)
                    safe = None
                    break


#SETTINGS --> To improve
        elif selected_option == "Settings":
            selected_index = 0

            time.sleep(0.20)
            while True:
                menu_options = ["Interface", "Ssh", "System"]
                draw_menu(selected_index)
                if GPIO.input(KEY_UP_PIN) == 0:
                    selected_index = (selected_index - 1) % len(menu_options)
                    draw_menu(selected_index)

                elif GPIO.input(KEY_DOWN_PIN) == 0:
                    selected_index = (selected_index + 1) % len(menu_options)
                    draw_menu(selected_index)

                elif bk():
                    #ui_print("Going back...", 0.5)
                    break

                elif GPIO.input(KEY_PRESS_PIN) == 0:
                    selected_option = menu_options[selected_index]

                    if selected_option == "Interface":
                        sys_class_net_ = subprocess.run(["ls", "/sys/class/net/"], text=True, capture_output=True)
                        if sys_class_net_.returncode != 0:
                            ui_print("""Error: Unable to
find ANY network
interfaces""")

                        else:
                            interface = sys_class_net_.stdout.splitlines()
                            selected_index = 0
                            time.sleep(0.20)
                            while True:
                                menu_options = interface
                                draw_menu(selected_index)
                                if GPIO.input(KEY_UP_PIN) == 0:
                                    selected_index = (selected_index - 1) % len(menu_options)
                                    draw_menu(selected_index)
                                elif GPIO.input(KEY_DOWN_PIN) == 0:
                                    selected_index = (selected_index + 1) % len(menu_options)
                                    draw_menu(selected_index)
                                elif bk():
                                    break
                                elif GPIO.input(KEY_PRESS_PIN) == 0:
                                    selected_interface = menu_options[selected_index]
                                    selected_index = 0
                                    menu_options = ["Restart", "Select"]
                                    time.sleep(0.2)
                                    while True:
                                        draw_menu(selected_index)
                                        if GPIO.input(KEY_UP_PIN) == 0:
                                            selected_index = (selected_index - 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif GPIO.input(KEY_DOWN_PIN) == 0:
                                            selected_index = (selected_index + 1) % len(menu_options)
                                            draw_menu(selected_index)
                                        elif bk():
                                            break

                                        elif GPIO.input(KEY_PRESS_PIN) == 0:
                                            selected_option = menu_options[selected_index]
                                            if selected_option == "Select":
                                                INTERFACE = selected_interface
                                                ui_print("Wait please...", 0.5)
                                                with open("settings/settings.json", "r+") as file:
                                                    data = json.load(file)
                                                    data["interface"] = INTERFACE
                                                    file.seek(0)  #start from the beginning of the file
                                                    json.dump(data, file, indent=2)
                                                    file.truncate() #remove any leftover data
                                                ui_print(f"""Selected Interface:
{selected_interface}""", 2, (0, 255, 142))
                                                break
                                            else:
                                                ui_print("""Restarting
interface...""", "unset")
                                                subprocess.run(f"sudo airmon-ng stop {selected_interface}", shell=True)
                                                time.sleep(0.5)
                                                subprocess.run(f"sudo ifconfig {selected_interface} down", shell=True)
                                                time.sleep(0.5)
                                                subprocess.run(f"sudo ifconfig {selected_interface} up", shell=True)
                                                ui_print(f"{selected_interface} restarted", 1, (0, 255, 142))
                                                break


                    elif selected_option == "Ssh":
                        selected_index = 0
                        menu_options = ["Enable", "Disable"]
                        time.sleep(0.20)
                        while True:
                            draw_menu(selected_index)
                            if GPIO.input(KEY_UP_PIN) == 0:
                                selected_index = (selected_index - 1) % len(menu_options)
                                draw_menu(selected_index)

                            elif GPIO.input(KEY_DOWN_PIN) == 0:
                                selected_index = (selected_index + 1) % len(menu_options)
                                draw_menu(selected_index)

                            elif bk():
                                #ui_print("Going back...", 0.5)
                                break

                            elif GPIO.input(KEY_PRESS_PIN) == 0:
                                selected_option = menu_options[selected_index]
                                if selected_option == "Enable":
                                    ui_print("Enabling SSH...", "unset")
                                    subprocess.run("sudo systemctl enable ssh.socket", shell=True)
                                    subprocess.run("sudo systemctl start ssh.socket", shell=True)
                                    ui_print("SSH enabled", 2, (0, 255, 142))
                                    break

                                else:
                                    ui_print("Disabling SSH...", "unset")
                                    #os.system("sudo systemctl stop ssh")
                                    #os.system("sudo systemctl disable ssh")
                                    ui_print("SSH disabled", 2, (255, 0, 0))
                                    break

                    else:
                        selected_index = 0
                        menu_options = ["Version", "Uninstall"]
                        time.sleep(0.20)
                        while True:
                            draw_menu(selected_index)
                            if GPIO.input(KEY_UP_PIN) == 0:
                                selected_index = (selected_index - 1) % len(menu_options)
                                draw_menu(selected_index)
                            elif GPIO.input(KEY_DOWN_PIN) == 0:
                                selected_index = (selected_index + 1) % len(menu_options)
                                draw_menu(selected_index)
                            elif bk():
                                #ui_print("Going back...", 0.5)
                                break
                            elif GPIO.input(KEY_PRESS_PIN) == 0:
                                selected_option = menu_options[selected_index]
                                if selected_option == "Uninstall":
                                    ui_print("Uninstalling M00N...", 0.5)
                                    #os.system("sudo rm -rf /root/M00N")
                                    #os.system("sudo rm -rf /usr/local/bin/m00n")
                                    #os.system("sudo rm -rf /usr/local/bin/m00n.py")
                                    ui_print("M00N uninstalled", 2, (255, 0, 0))
                                    break
                                else:
                                    ui_print(version, "unset", (100, 40, 237))
                                    while True:
                                        if bk() == True:
                                            #ui_print("Going back...", 0.5)
                                            break
