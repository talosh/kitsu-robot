# Kitsu-Robot
Kitsu automation backend

## Setup

### Dependencies
```
brew install logrotate
```

### Get Kitsu-Robot sources
```
sudo mkdir /opt/kitsu-robot
sudo chown dladmin:staff /opt/kitsu-robot
cd /opt/kitsu-robot
git clone https://github.com/talosh/kitsu-robot.git .
```

Create virtual environment and install python dependencies
```
pip3 install virtualenv
virtualenv robotenv
. robotenv/bin/activate
pip3 install -r requirements.txt
```

### Configure logging

* rotate logs
```
crontab -e
```

add line

```
0 4 * * * /usr/local/opt/logrotate/sbin/logrotate --state /opt/kitsu-robot/log/logrotate.status /opt/kitsu-robot/logrotate.conf
```

* Web logging:

```
copy com.dirtylooks.tailon.plist to ~/Library/LaunchAgents
add proxy string to /usr/local/etc/nginx/servers/zou
    location /log {
    proxy_http_version 1.1;
        proxy_pass http://localhost:5002;
	proxy_redirect off;
	proxy_set_header Host $host;
    }
```

### Crontab
* crontab
```
0 0 * * * sudo /usr/local/bin/rsnapshot -c /usr/local/etc/rsnapshot.conf daily
0 4 * * * /usr/local/opt/logrotate/sbin/logrotate --state /opt/kitsu-robot/log/logrotate.status /opt/kitsu-robot/logrotate.conf
40 * * * * /usr/bin/osascript /opt/kitsu-robot/robotenv/bin/backup_zou_db.scpt
```
