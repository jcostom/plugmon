# plugmon

[![Docker Stars](https://img.shields.io/docker/stars/jcostom/plugmon.svg)](https://hub.docker.com/r/jcostom/plugmon/)
[![Docker Pulls](https://img.shields.io/docker/pulls/jcostom/plugmon.svg)](https://hub.docker.com/r/jcostom/plugmon/)
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fjcostom%2Fplugmon.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fjcostom%2Fplugmon?ref=badge_shield)

Lightweight python-based monitoring Etekcity Smart Plug via the VeSync API and activating an IFTTT webhook that triggers sending a Telegram message.

## Pull the image

`docker pull jcostom/plugmon`

## Run the container

Sort out your optional parameters (the ENV vars), and you're off to the races...

```bash
docker run -d \
    --name=washermon \
    --restart=unless-stopped \
    --user=1000:1000 \
    -e EMAIL='Your VeSync Email' \
    -e PASSWORD='Your VeSync Password' \
    -e TZ='America/New_York' \
    -e DEVNAME='Name of Your Plug Device' \
    -e IFTTTKEY='Your IFTTT Webhook Key' \
    -e IFTTTWEBHOOK='Your IFTTT Webhook Name' \
    -e OFFPOWER=1.2 \
    -e ONPOWER=3.0 \
    jcostom/plugmon
```

The --user parameter consists of the UID:GID pair you'd like to run the container as.

The OFFPOWER and ONPOWER values are the high and low watermarks in Watts to activate the indicated state. In other words, in the above example, when you drop below 1.2W being pulled, the device is considered to be off. Conversely, when you go above 3.0W, the device is considered to be on.

Versions 1.5 and later have gotten rid of the DEVID variable, in favor of the DEVNAME variable. This removes the need to figure out in advance what position your intended device occurs in the list of devices.

## Available Parameters

| Variable | Default Value | Required to Launch? |
|---|---|---|
| EMAIL | [EMPTY] | YES! |
| PASSWORD | [EMPTY] | YES! |
| TZ | America/New_York | NO |
| DEVNAME | [EMPTY] | YES! |
| OFFPOWER | 1.2 | NO |
| ONPOWER | 3.0 | NO |
| IFTTTKEY | [EMPTY] | YES! |
| IFTTTWEBHOOK | [EMPTY] | YES! |
| INTERVAL (in seconds) | 300 | NO |

## License

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fjcostom%2Fplugmon.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fjcostom%2Fplugmon?ref=badge_large)
