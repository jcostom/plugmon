#!/usr/bin/env python3

from pyvesync_v2 import VeSync

manager = VeSync("EMAIL", "PASSWORD", time_zone=TZ)
manager.login()
manager.update()
for device in manager.outlets:
    device.display()