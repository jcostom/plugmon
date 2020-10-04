#!/usr/bin/env python3

import os
import time
import requests
from pyvesync import VeSync

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
TZ = os.getenv('TZ', 'America/New_York')
DEVID = int(os.getenv('DEVID', 0))
IFTTTKEY = os.getenv('IFTTTKEY')
IFTTTWEBHOOK = os.getenv('IFTTTWEBHOOK')

INTERVAL = os.getenv('INTERVAL', 300)
IS_RUNNING = 0

def triggerWebHook():
    webHookURL = "/".join(
        ("https://maker.ifttt.com/trigger",
        IFTTTWEBHOOK,
        "with/key",
        IFTTTKEY)
    )
    headers = {'User-Agent': 'plugmon.py v0.4'}
    response = requests.get(updateURL, headers=headers)
    print(time.strftime("[%d %b %Y %H:%M:%S]", time.localtime()) + " IFTTT Response: {}".format(response.text))

def main():
    manager = VeSync(EMAIL, PASSWORD, TZ)
    manager.login()
    manager.update()
    mysw = manager.outlets[DEVID]
    while True:    
        manager.update()
        manager.update_energy()
        mysw_power = float(mysw.details.get('power',0))
        if mysw_power > 0.5:
            print(time.strftime("[%d %b %Y %H:%M:%S]", time.localtime()) + " Washer is running: {}".format(mysw_power))
            IS_RUNNING = 1
        else:
            print(time.strftime("[%d %b %Y %H:%M:%S]", time.localtime()) + " Washer is stopped: {}".format(mysw_power))
            triggerWebHook()
            IS_RUNNING = 0

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()