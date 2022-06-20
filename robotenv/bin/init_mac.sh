#!/bin/zsh
/usr/bin/osascript -e 'tell application "Terminal" to activate'
/usr/bin/osascript -e 'tell application "Terminal" to do script "/usr/bin/python /opt/kitsu-robot/setenv.py; screen -L -c /opt/kitsu-robot/screen.conf -S Kitsu-Robot -d -m /opt/kitsu-robot/robotenv/bin/python3 /opt/kitsu-robot/robot.py" in window 1'
sleep 2
/usr/bin/osascript -e 'quit application "Terminal"'
