"""This is a small script to test the reliabiliy of the hardware.

This can be run as a cronjob to verifiy everything works as expected.
"""


import stall_alarm as ma
import stall_alarm_config as cfg

if __name__ == '__main__':
    for recipient in cfg.recipients:
        ma.send_smstools_msg('Probe Alarm! Reliability test message!',
                             recipient=recipient)
