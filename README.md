# icinga2_xmpp-notifications
Small python script to send xmpp notifications from your icinga2 monitoring system.
Based on [this script](https://gitlab.com/meschenbacher/icinga2-xmpp-notification),
but without using enviroment variables (Director compatible) and different formatting.

# Dependencies

python3-sleekxmpp

In debian:
```
apt-get install python3-sleekxmpp
```

elsewhere probably:
```
pip install sleekxmpp
```

# Installation

Copy 'xmpp-notification.py' to a location of your choosing (possibly
'/etc/icinga2/scripts' besides the default the default mail scripts, but
any location might suffice.
Remember to set the permissions correctly, so the icinga2 daemon is able
to execute the script.

Append the content of 'icinga2_conf/commands.conf' somewhere in your config
to define the command for icinga2. Set the path according to the location
of the script.

Append the content of 'icinga2_conf/templates.conf' somewhere in your config
to define the notification templates for icinga2.
Set JID and the password for the XMPP-Account you want to send notifications here.

Add the customvar 'userjid' with the JID you want to notify to the user you want
to notify. A hint is in 'icinga2_conf/users.conf'.

# Caveats
Since the JID and the password for the sending account are handed over via
arguments, they are visible for all users on the system who are able to get
their hands on a list of running processes (most likely meaning all users).
This is not ideal, but this way the script can be integrated via Director.

# Notes
Improvements are welcome! Send me a PR or open an issue if you think there
is a problem.
Also I do owe [this guy](https://gitlab.com/meschenbacher) a beer!
