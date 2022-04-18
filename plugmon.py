#!/usr/bin/env python3

import os
from time import sleep, strftime
import requests
import random
import hashlib
import logging
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
DEBUG = int(os.getenv('DEBUG', 0))

VER = "3.4"
USER_AGENT = f"plugmon.py/{VER}"

# Setup logger
logger = logging.getLogger()
ch = logging.StreamHandler()
if DEBUG:
    logger.setLevel(logging.DEBUG)
    ch.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)

formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s',
                              datefmt='[%d %b %Y %H:%M:%S %Z]')
ch.setFormatter(formatter)
logger.addHandler(ch)


def send_notification(msg, chat_id, token):
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=msg)
    logger.info('Telegram Group Message Sent')


def login_api(email, md5pass, tz, traceid):
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
    account_id = r.json()['result']['accountID']
    token = r.json()['result']['token']
    return([account_id, token])


def turn_switch_on(accountID, token, tz, traceid):
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
        logger.info("Plug turned on.")


def main():
    logger.info(f"Initiated: {USER_AGENT}")
    [ACCOUNTID, TOKEN] = login_api(EMAIL, MD5PASSWORD, TZ, TRACEID)

    # Make sure the switch is on!
    turn_switch_on(ACCOUNTID, TOKEN, TZ, TRACEID)

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

    url = f"https://smartapi.vesync.com/v1/device/{UUID}/detail"

    while True:
        r = requests.get(url, headers=headers)
        mysw_power = float(r.json()['power'])
        if IS_RUNNING == 0:
            if mysw_power > ONPOWER:
                logger.info(f"Washer changed from stopped to running: {mysw_power}")  # noqa: E501
                IS_RUNNING = 1
            else:
                logger.info(f"Washer remains stopped: {mysw_power}")
        else:
            if mysw_power < OFFPOWER:
                logger.info(f"Washer changed from running to stopped: {mysw_power}")  # noqa: E501
                notificationText = "".join(
                    ("Washer finished on ",
                     strftime("%B %d, %Y at %H:%M"),
                     ". Go switch out the laundry!")
                )
                send_notification(notificationText, CHATID, MYTOKEN)
                IS_RUNNING = 0
            else:
                logger.info(f"Washer remains running: {mysw_power}")

        sleep(INTERVAL)


if __name__ == "__main__":
    main()
