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
