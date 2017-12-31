# RaspberryPi als Alarmanlage

Die Alarmanlage basiert auf einem Raspberry Pi der einen Alarmkontakt.

Die Gesamtkosten dieser Alarmanlage sind sehr überschaubar.

 - RaspberryPi Zero W, rPi3 ... also zwischen 8-35€ je nach Model
 - Huawei Stick 5-10€ (gebraucht), 20€ Neu
 - Netzteil 5V 2A 0€ (altes Handyladegerät)
 - Powerbank 15€-80€

Jemand from Scratch so was baut und nix altes rum liegen hat. Nimmt am besten
ein RaspberryPi Starter Set (ca. 70-80€)

Gesamt sollte das Projekt mit ca 150€ realisierbar sein.

# RaspberryPi Setup

Installiert wird am besten Raspbian(Lite) ohne GUI/Desktop

Benötigt für das Skript werden
 - python3
 - python3-pip
 - python3-gpiozero


# Message Providers

Das Alarm Script sendet "ALARM!" aus allen möglichen Kanälen
SMS, (in Zukunft auch eMail, WhatsApp ...)

## SMS mit Twilio (Internet)
Twilio ist ein Webservice braucht also eine Internetverbindung wie auch immer die hergestellt wird.

Mit pip wird **twilio** installiert.

```
sudo pip install twilio
```

Account SID und auth_thoken in stall_alarm_config.py eintragen und es sollte laufen.


## SMS mit Wertkarte und smstools

Ein altes GPRS-Modem (USB) kann auch verwendet werden um Alarme zu senden. Kosten 5€~20€

Huawei e160 ... Siemens mc35i ... mc55 ...

```
sudo apt-get install smstools
```

smstools zu konfigurieren ist ziemlich simpel. **/etc/smsd.conf**

ganz unten das Beispiel wie hier anpassen
```
[GSM1]
init = AT^CURC=0
device = /dev/ttyUSB0
incoming = yes
baudrate = 115200

```

und schon sendet der Huawei Stick SMS. Ich empfehle den PIN auf der SIM zu
entfernen das macht bei manchen Sticks probleme.

Wichtig ist noch den user (hier pi) der Gruppe smsd hinzu zu fügen

```
pi@stall ~> sudo usermod -a -G smsd pi
```

Mit systemctl checken ob smstools korrekt läuft und startet.
```
pi@stall ~> sudo systemctl start smstools.service
```

Debian verwendet mitttlerweile auch systemd(wurde auch zeit)
https://wiki.archlinux.org/index.php/Systemd#Using_units

Die Logs sind unter **/var/log/smstools/smsd.log**.


### Probleme mit zu langsamen Modem und zu schnellem Rechner
Mein RaspberrPi 3 startet smstools zu schnell. Das Modem liefert SIM Busy und smstools startet nicht. Als abhilfe habe ich das **/etc/ini.d/smstools** geändert und ein **sleep 20** hinzugefügt.

```
	# Start the daemon
	ARGS="-p$PIDFILE -i$INFOFILE -u$USER -g$GROUP"
	sleep 20
	if start-stop-daemon -q --start --background -p $PIDFILE --exec $DAEMON -- $ARGS ; then
		echo "$NAME."
	else
		echo "$NAME already running."
	fi

	sleep 1
```

# Verbinden des Relais mit dem RaspberryPi
Unsere Schaltschrank hat ein Relais verbaut das sich öffnet wenn.
1. Der Strom ausfällt
2. Ein Problem bei der Lüftung besteht (Motorschutz oder LS auslöst)

Dieses Relais wird an GPIO in der Beispiel Config an Pin17 und Masse gehängt.

# Alarm Script

**stall_alarm.py** ist ein Skript dass einen GPIO pin am PI als Alarmkontakt nutzt. Das Skript kann einfach mit crontab gestartet werden.

## Installation
Script und config sind in getrennten Modulen.

1. **stall_alarm.py** und **stall_alarm_config.py** auf den Raspberry Pi kopieren. (**scp**, **git clone**, **whatever**)
2. [crontab anpassen]('https://wiki.archlinux.org/index.php/Cron') um Probealarme und Alarme zu senden. Das Projekt enthält eine Beispiel **stall_alarm_crontab**.
3. stall_alarm_config anpassen (Telefonnummer eintragen ... )
4. Reboot und prüfen ob alles läuft. (Relais schalten z.B.)

## Manuell Test-Nachrichten senden

Ich empfehle **bpython** als interaktiven interpreter **python3** einfach zu starten geht natürlich auch.

```
pi@mobilstall ~> bpython
bpython version 0.16 on top of Python 3.5.3 /usr/bin/python3
>>> import stall_alarm
>>> stall_alarm.send_sms_alarm()
2017-12-31 13:01:20.753797 sending 'ALARM @Stall' via smstools to 4369911111111
2017-12-31 13:01:20.778968 sending 'ALARM @Stall' via smstools to 436502222222
2017-12-31 13:01:20.805347 sending 'ALARM @Stall' via smstools to 4369933333333
>>> exit()
```
