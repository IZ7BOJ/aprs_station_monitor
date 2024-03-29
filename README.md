# aprs_station_monitor
python script which send notification on telegram about the vitality of a list of APRS stations, on the basis of the last packet registered on aprs.fi database coming from the stations to be monitored.

This script periodically makes a query to aprs.fi database using APIs, and send a notification by telegram of the stations, or digipeater or igates that goes down/up.
The script can be used by sysops to monitor the vitality of a group o digipeaters, and to know the vitality situation in realtime.
The vitality is assumed on the basis of the last packet registered on aprs.fi database coming from the stations to be monitored.
If the "last heard" interval time is more than the timeout specified in the config section, the station is declared "dead"
The telegram notifications are sent every time a station changes state (Alive to Dead and Dead to Alive)
This script should be executed in background (sudo python aprs_stations_monitor.py &) and is configured to log errors and transition "alive->dead" and "dead->alive"

# INSTALLING AND USING
Before using this script, intall and configure the library "telegram-send ( https://pypi.org/project/telegram-send/ ) and configure the destination of the notifications (single user, group or channel).

sudo pip3 install telegram-send

telegram-send --configure if you want to send to your account
telegram-send --configure-group to send to a group 
telegram-send --configure-channel to send to a channel.

Then, every parameter of the config section of the script must be declared, including aprs.fi API personal Key (an account on aprs.fi is required)

You can start the script automatically using systemd. Follow these instrunctions:

Create a systemd service file using:
$ sudo nano /lib/systemd/system/aprs_station_monitor.service with the contents as shown below

[Unit]
Description=telegram alert for aprs stations
After=meadiacenter.service

[Service]
User=root
Group=root
Type=simple
ExecStart=/usr/bin/python /home/pi/Applications/aprs_station_monitor.py #change the path with yours!!
Restart=Always

[Install]
WantedBy=multi-user.target


Type "ctrl-o", ENTER, "ctrl-x" to save and exit the nano editor

After any changes to /lib/systemd/system/aprs_station_monitor.service:
sudo systemctl daemon-reload
sudo systemctl enable aprs_station_monitor.service
sudo reboot

Ensure the aprs_station_monitor.service in systemd is enabled and running:
systemctl list-unit-files | grep enabled
systemctl | grep running | grep aprs
systemctl status aprs_station_monitor.service -l

If there are any issues with starting the script using systemd, then examine the journal using:
sudo journalctl -u aprs_station_monitor.service

# SOFTWARE STABILITY
This script may have bugs, problems and it could be written without a lot of good programming rules. But it works for me.

# Author
Alfredo IZ7BOJ iz7boj[--at--]gmail.com

# LICENSE
You can modify this program, but please give a credit to original author. Program is free for non-commercial use only.
(C) Alfredo IZ7BOJ 2018

# Version 
0.1 beta

