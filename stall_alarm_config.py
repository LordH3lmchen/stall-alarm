"""Main configuraion file for the alarm script."""

# General Settings
###############################################################################
# Numbers that should receive Alarms
# recipients = ['+4367687654321']
recipients = ['+4367687654321', '+4367611111111111', '+4367622222222222']
gpio_pin_nr = 17


# smstools
###############################################################################
smstools_enabled = True
outgoing_directory = '/var/spool/sms/outgoing'

# Twilio
###############################################################################
# Enable Twilio
twilio_enabled = False
# Your Account SID from twilio.com/console
account_sid = "Paste your Twilio account_sid HERE"
# Your Auth Token from twilio.com/console
auth_token = "Paste your Twilio auth_token HERE"
# Twilio from_ Number
twilio_sender_number = '+4367612345678'
