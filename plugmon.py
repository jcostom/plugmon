#!/usr/bin/env python3

import asyncio
import os
from time import sleep, strftime
import requests
import random
import hashlib
import logging
import json
import telegram

# --- To be passed in to container ---
# Mandatory vars
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
TZ = os.getenv('TZ', 'America/New_York')
UUID = os.getenv('UUID')
OFFPOWER = float(os.getenv('OFFPOWER', 1.2))
ONPOWER = float(os.getenv('ONPOWER', 3.0))
INTERVAL = os.getenv('INTERVAL', 300)
CHATID = int(os.getenv('CHATID'))
MYTOKEN = os.getenv('MYTOKEN')

# Optional Vars
DEBUG = int(os.getenv('DEBUG', 0))

# --- Other Globals ---
TRACEID = str(random.uniform(1, 1000000000))
MD5PASSWORD = hashlib.md5(PASSWORD.encode('utf-8')).hexdigest()

VER = '3.9'
USER_AGENT = f"plugmon.py/{VER}"

# Setup logger
LOG_LEVEL = 'DEBUG' if DEBUG else 'INFO'
logging.basicConfig(level=LOG_LEVEL,
                    format='[%(levelname)s] %(asctime)s %(message)s',
                    datefmt='[%d %b %Y %H:%M:%S %Z]')
logger = logging.getLogger()


async def send_notification(msg: str, chat_id: int, token: str) -> None:
    bot = telegram.Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=msg)
    logger.info('Telegram Group Message Sent')


def login_api(email: str, md5pass: str, time_zone: str, trace_id: str) -> list:
    headers = {'Content-Type': 'application/json', 'User-Agent': USER_AGENT}
    body = {
        "timeZone": time_zone,
        "acceptLanguage": "en",
        "appVersion": VER,
        "traceId": trace_id,
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
    return [account_id, token]


def turn_switch_on(account_id: str, token: str, time_zone: str, trace_id: str) -> None:  # noqa: E501
    url = "https://smartapi.vesync.com/10a/v1/device/devicestatus"
    headers = {'Content-Type': 'application/json', 'User-Agent': USER_AGENT}
    body = {
       'accountID': account_id,
       'timeZone': time_zone,
       'token': token,
       'status': 'on',
       'uuid': UUID,
       'traceId': trace_id
    }
    r = requests.put(url, headers=headers, data=json.dumps(body))
    if r.json()['code'] == 0:
        logger.info("Plug turned on.")
        return True
    else:
        logger.info("FATAL: Plug wouldn't turn on!")
        raise SystemExit("Plug did not turn on, exiting.")


def main() -> None:
    logger.info(f"Initiated: {USER_AGENT}")
    [account_id, token] = login_api(EMAIL, MD5PASSWORD, TZ, TRACEID)

    # Make sure the switch is on!
    turn_switch_on(account_id, token, TZ, TRACEID)

    is_running = 0

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': USER_AGENT,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Language': 'en',
        'accountId': account_id,
        'appVersion': VER,
        'tk': token,
        'tz': TZ,
        'traceid': TRACEID
    }

    url = f"https://smartapi.vesync.com/v1/device/{UUID}/detail"

    while True:
        r = requests.get(url, headers=headers)
        mysw_power = float(r.json()['power'])
        if is_running == 0:
            if mysw_power > ONPOWER:
                logger.info(f"Washer changed from stopped to running: {mysw_power}")  # noqa: E501
                is_running = 1
            else:
                logger.info(f"Washer remains stopped: {mysw_power}")
        else:
            if mysw_power < OFFPOWER:
                logger.info(f"Washer changed from running to stopped: {mysw_power}")  # noqa: E501
                now = strftime("%B %d, %Y at %H:%M")
                notification_text = f"Washer finished on {now}. Go switch out the laundry!"  # noqa: E501
                asyncio.run(send_notification(notification_text, CHATID, MYTOKEN))  # noqa: E501
                is_running = 0
            else:
                logger.info(f"Washer remains running: {mysw_power}")

        sleep(INTERVAL)


if __name__ == "__main__":
    main()
