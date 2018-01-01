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


## USB 3G Modem Setup (Notwendig für SMS versand mit Wertkarte)
Eine Internetverbindung muss natürlich nicht bestehen. Allerdings muss der
Stick als Modem erkannt werden.

Im Arch Wiki gibts einige Artikel dazu wie man diverse Sticks als Modem nutzt
 - https://wiki.archlinux.org/index.php/USB_3G_Modem
 - https://wiki.archlinux.org/index.php/udev#Setting_static_device_names
 - https://wiki.archlinux.org/index.php/Huawei_E1550_3G_modem
 - https://wiki.archlinux.org/index.php/Huawei_E220

Ich besitze ein Huawei Mobile Connect, Model E160 von bob. Ein Modeswitch ist
bei meinem Model scheinbar nicht notwendig. Es wird nie als USB Speicher erkannt
ist sofort als Modem verfügbar. Das ist aber von Provider und Model abhängig.


### Statische Hardwarenamen
Es kann passieren dass das Modem die Verbindung verliert und neue Namen bekommt.
Spannungsschwankungen, Versehentliches rausziehen des Modems ... . Um das zu
verhindern kann man dem USB Device einen defnierten Namen geben (Symlinks mit
udev)

```
pi@mobilstall /e/u/rules.d> lsusb
Bus 001 Device 007: ID 12d1:1001 Huawei Technologies Co., Ltd. E169/E620/E800 HSDPA Modem
Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. SMC9514 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

Folgende UDEV Regeln lösen das Problem
```

pi@mobilstall /e/u/rules.d> cat 98-huwei-gsm.rules
SUBSYSTEMS=="usb", ATTRS{modalias}=="usb:v12D1p1001*", KERNEL=="ttyUSB*", ATTRS{bInterfaceNumber}=="00", ATTRS{bInterfaceProtocol}=="ff", SYMLINK+="ttyUSB_utps_modem"
SUBSYSTEMS=="usb", ATTRS{modalias}=="usb:v12D1p1001*", KERNEL=="ttyUSB*", ATTRS{bInterfaceNumber}=="01", ATTRS{bInterfaceProtocol}=="ff", SYMLINK+="ttyUSB_utps_diag"
SUBSYSTEMS=="usb", ATTRS{modalias}=="usb:v12D1p1001*", KERNEL=="ttyUSB*", ATTRS{bInterfaceNumber}=="02", ATTRS{bInterfaceProtocol}=="ff", SYMLINK+="ttyUSB_utps_pcui"
```


# Message Providers
Das Alarm Script sendet "ALARM!" aus allen möglichen Kanälen
SMS, (in Zukunft auch eMail, WhatsApp ...)


## SMS mit Twilio (Internet)
Twilio ist ein Webservice braucht also eine Internetverbindung wie auch immer
die hergestellt wird.

Mit pip wird **twilio** installiert.

```
sudo pip install twilio
```

Account SID und auth_thoken in stall_alarm_config.py eintragen und es sollte
laufen.


## SMS mit Wertkarte und smstools
Ein altes GPRS-Modem (USB) kann auch verwendet werden um Alarme zu senden.
Kosten 5€~20€

Huawei e160 ... Siemens mc35i ... mc55 ...

```
sudo apt-get install smstools
```

smstools zu konfigurieren ist ziemlich simpel. **/etc/smsd.conf**

ganz unten das Beispiel wie hier anpassen
```
[GSM1]
init = AT^CURC=0
device = /dev/ttyUSB_utps_modem
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
Mein RaspberrPi 3 startet smstools zu schnell. Das Modem liefert SIM Busy und
smstools startet nicht. Als abhilfe habe ich das **/etc/ini.d/smstools**
geändert und ein **sleep 20** hinzugefügt um den Stick etwas mehr Zeit (20sec)
zu geben um zu starten.

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

**stall_alarm.py** ist ein Skript dass einen GPIO pin am PI als Alarmkontakt
nutzt. Das Skript kann einfach mit crontab gestartet werden.

## Installation
Script und config sind in getrennten Modulen.

1. **stall_alarm.py** und **stall_alarm_config.py** auf den Raspberry Pi
    kopieren. (**scp**, **git clone**, **whatever**)
2. [crontab anpassen]('https://wiki.archlinux.org/index.php/Cron') um
    Probealarme und Alarme zu senden. Das Projekt enthält eine Beispiel
    **stall_alarm_crontab**.
3. stall_alarm_config anpassen (Telefonnummer eintragen ... )
4. Reboot und prüfen ob alles läuft. (Relais schalten z.B.)

## Testen
Bevor man so etwas Produktiv laufen lässt ein paar Tage testen. Also eine
Nachricht täglich senden. Wenn alles stabil läuft trotzdem einmal wöchentlich
einen Probealarm (wie auch bei der Feuerwehr)

## Manuell Test-Nachrichten senden

Ich empfehle **bpython** als interaktiven interpreter **python3** einfach zu
starten geht natürlich auch.

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
