# Kitsu-Robot
Kitsu automation backend

## Setup

### Dependencies

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