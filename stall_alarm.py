"""mobilstall alarm script.

This script can be used to send alarm messages. To configure it use the
stall_alarm_config.py
"""

from gpiozero import Button
from signal import pause
from twilio.rest import Client
import stall_alarm_config as cfg
import datetime

client = Client(cfg.account_sid,
                cfg.auth_token)


def send_smstools_msg(message_text='ALARM @Stall (smstools)',
                      recipient=''):
    """Send a short message via a local smstools service."""
    recipient = recipient.replace('+', '')
    msg_file_name = cfg.outgoing_directory + '/' +\
        recipient + str(datetime.datetime.utcnow())
    with open(msg_file_name, 'w') as msg_file:
        print(str(datetime.datetime.utcnow()) +
              ' sending \'' + message_text +
              '\' via smstools' +
              ' to ' + recipient)
        msg_file.write("To: " + recipient + "\n\n" + message_text)
        msg_file.close()


def send_twilio_message(message_text='ALARM @Stall (twillio)',
                        recipient=''):
    """Send a short message via twilio account."""
    message = client.messages.create(
            to=recipient,
            from_=cfg.twilio_sender_number,
            body=message_text)
    print(str(datetime.datetime.utcnow()) +
          ' sending \'' + message_text +
          '\' via twilio with message.sid' + message.sid +
          ' to ' + recipient)


def send_sms_msg(msg_text):
    """Send a short message via configured SMS."""
    for recipient in cfg.recipients:
        if cfg.twilio_enabled:
            send_twilio_message(msg_text, recipient)
        if cfg.smstools_enabled:
            send_smstools_msg(msg_text, recipient)


def send_sms_clear():
    """Send a clear notification via SMS."""
    clear_text = 'EVERYTHING OK AGAIN! @Stall'
    send_sms_msg(clear_text)


def send_sms_alarm():
    """Send a alarm message via SMS."""
    alarm_text = 'ALARM @Stall'
    send_sms_msg(alarm_text)


if __name__ == '__main__':
    btn = Button(cfg.gpio_pin_nr)
    btn.when_pressed = send_sms_clear
    btn.when_released = send_sms_alarm
    pause()
