import os
import subprocess
import json

MOUNT_DIR = "/mnt/usb"
WPA_SUPPLICANT_FILE = "/etc/wpa_supplicant/wpa_supplicant.conf"


def mount_usb():
    if not os.path.exists(MOUNT_DIR):
        os.makedirs(MOUNT_DIR)
    cmd = "mount /dev/sda1 /mnt/usb"
    subprocess.call(cmd, shell=True)


def get_creds():
    wifi_path = os.path.join(MOUNT_DIR, "wifi.json")
    if os.path.exists(wifi_path):
        with open(wifi_path) as f:
            wifi_json = json.loads(f.read())
            return wifi_json["ssid"], wifi_json["psk"]
    return None, None



def already_has_creds(ssid, psk):
    with open(WPA_SUPPLICANT_FILE) as f:
        existing = f.read()
    return  ssid in existing and psk in existing


def add_creds(ssid, psk):
    cmd = 'wpa_passphrase "%s" "%s" >> /etc/wpa_supplicant/wpa_supplicant.conf' % (ssid, psk)
    subprocess.call(cmd, shell=True)
    cmd = "sudo wpa_cli reconfigure"
    subprocess.call(cmd, shell=True)



if __name__ == '__main__':
    mount_usb()
    ssid, psk = get_creds()
    if ssid is not None and not already_has_creds(ssid, psk):
        add_creds(ssid, psk)
