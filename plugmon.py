#!/usr/bin/env python3

import os
import time
import requests
import random
import hashlib
import json
import telegram

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
MD5PASSWORD = hashlib.md5(PASSWORD.encode('utf-8')).hexdigest()
TZ = os.getenv('TZ', 'America/New_York')
UUID = os.getenv('UUID')
OFFPOWER = float(os.getenv('OFFPOWER', 1.2))
ONPOWER = float(os.getenv('ONPOWER', 3.0))
INTERVAL = os.getenv('INTERVAL', 300)
TRACEID = str(random.uniform(1, 1000000000))
CHATID = int(os.getenv('CHATID'))
MYTOKEN = os.getenv('MYTOKEN')

VER = "3.1"
USER_AGENT = "plugmon.py/" + VER


def sendNotification(msg, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)
    writeLogEntry("Telegram Group Message Sent", "")


def writeLogEntry(message, status):
    print(time.strftime("[%d %b %Y %H:%M:%S %Z]",
          time.localtime()) + " {}: {}".format(message, status))


def loginAPI(email, md5pass, tz, traceid):
    headers = {'Content-Type': 'application/json', 'User-Agent': USER_AGENT}
    body = {
        "timeZone": tz,
        "acceptLanguage": "en",
        "appVersion": VER,
        "traceId": traceid,
        "phoneBrand": "HappyFunBall",
        "phoneOS": "HappyFunOS",
        "email": email,
        "password": md5pass,
        "devToken": "",
        "userType": "1",
        "method": "login"
    }
    url = "https://smartapi.vesync.com/cloud/v1/user/login"
    r = requests.post(url, headers=headers, json=body)
    accountID = r.json()['result']['accountID']
    token = r.json()['result']['token']
    return([accountID, token])


def turnSwitchOn(accountID, token, tz, traceid):
    url = "https://smartapi.vesync.com/10a/v1/device/devicestatus"
    headers = {'Content-Type': 'application/json', 'User-Agent': USER_AGENT}
    body = {
       'accountID': accountID,
       'timeZone': tz,
       'token': token,
       'status': 'on',
       'uuid': UUID,
       'traceId': traceid
    }
    r = requests.put(url, headers=headers, data=json.dumps(body))
    if r.json()['code'] == 0:
        writeLogEntry('Plug turned on', '')


def main():
    writeLogEntry('Initiated', '')
    [ACCOUNTID, TOKEN] = loginAPI(EMAIL, MD5PASSWORD, TZ, TRACEID)

    # Make sure the switch is on!
    turnSwitchOn(ACCOUNTID, TOKEN, TZ, TRACEID)

    IS_RUNNING = 0

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Language': 'en',
        'accountId': ACCOUNTID,
        'appVersion': VER,
        'tk': TOKEN,
        'tz': TZ,
        'traceid': TRACEID
    }

    url = "/".join(
        ("https://smartapi.vesync.com/v1/device",
         UUID,
         "detail")
    )

    while True:
        r = requests.get(url, headers=headers)
        mysw_power = float(r.json()['power'])
        if IS_RUNNING == 0:
            if mysw_power > ONPOWER:
                writeLogEntry('Washer changed from stopped to running',
                              mysw_power)
                IS_RUNNING = 1
            else:
                writeLogEntry('Washer remains stopped', mysw_power)
        else:
            if mysw_power < OFFPOWER:
                writeLogEntry('Washer changed from running to stopped',
                              mysw_power)
                notificationText = "".join(
                    ("Washer finished on ",
                     time.strftime("%B %d, %Y at %H:%M"),
                     ". Go switch out the laundry!")
                )
                sendNotification(notificationText, CHATID, MYTOKEN)
                IS_RUNNING = 0
            else:
                writeLogEntry('Washer remains running', mysw_power)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
