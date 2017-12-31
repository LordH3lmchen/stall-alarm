#!/usr/bin/sh
# This script deploys everything on the Production System


scp stall_alarm.py pi@192.168.1.110:~/
scp test_sms_hardware.py pi@192.168.1.110:~/
scp stall_alarm_config.py pi@192.168.1.110:~/
