#!/usr/bin/env python3

import os
from pyvesync import VeSync

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
TZ = os.getenv('TZ', 'America/New_York')

manager = VeSync(EMAIL, PASSWORD, time_zone=TZ)
manager.login()
manager.update()
for device in manager.outlets:
    device.display()
    print("--------------------------------------")
    