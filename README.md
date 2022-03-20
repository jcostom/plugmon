# plugmon

Lightweight python-based monitoring Etekcity Smart Plug via the VeSync API that fires of a Telegram message when power use drops below a certain level. As of v3.0 removes the dependency on IFTTT!

## Pull the image

`docker pull jcostom/plugmon`

## Find your target UUID value

Each plug device has a unique identifier (the UUID). This is how we identify which device to pull power metrics from as we monitor the device. I've included a script in the container to assist you in locating the UUID you want to monitor. To find the UUID, invoke the container as (and don't worry, the container will self-delete and clean up after itself when you do this!)..

```bash
docker run \
    --rm \
    --user=1000:1000 \
    -e EMAIL='Your VeSync Email' \
    -e PASSWORD='Your VeSync Password' \
    -e TZ='America/New_York' \
    --entrypoint /app/finduuid.py \
    jcostom/plugmon
```

## Run the container

Sort out your optional parameters (the ENV vars), and you're off to the races... You'll need to find your Telegram Chat ID and Bot Token on your own. Those are outside the scope of this document. If you're this far, you should be able to work that out though!

```bash
docker run -d \
    --name=washermon \
    --restart=unless-stopped \
    --user=1000:1000 \
    -e EMAIL='Your VeSync Email' \
    -e PASSWORD='Your VeSync Password' \
    -e TZ='America/New_York' \
    -e UUID='UUID of Your Plug Device' \
    -e CHATID=TELEGRAM-CHAT-ID-VALUE \
    -e MYTOKEN=TELEGRAM-BOT-TOKEN-VALUE \
    -e OFFPOWER=1.2 \
    -e ONPOWER=3.0 \
    jcostom/plugmon
```

The --user parameter consists of the UID:GID pair you'd like to run the container as.

The OFFPOWER and ONPOWER values are the high and low watermarks in Watts to activate the indicated state. In other words, in the above example, when you drop below 1.2W being pulled, the device is considered to be off. Conversely, when you go above 3.0W, the device is considered to be on.

As of version 2.0, there's no more fooling around with DEVID or DEVNAME variables, which are too easy to change and break your monitoring app. As of 2.0, we rely on the device UUID. See above for how to locate the UUID you want.

## Available Parameters

| Variable | Default Value | Required to Launch? |
|---|---|---|
| EMAIL | [EMPTY] | YES! |
| PASSWORD | [EMPTY] | YES! |
| TZ | America/New_York | NO |
| UUID | [EMPTY] | YES! |
| OFFPOWER | 1.2 | NO |
| ONPOWER | 3.0 | NO |
| CHATID | [EMPTY] | YES! |
| MYTOKEN | [EMPTY] | YES! |
| INTERVAL (in seconds) | 300 | NO |
