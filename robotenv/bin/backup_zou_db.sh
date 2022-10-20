#!/bin/zsh
/usr/bin/osascript -e 'tell application "Terminal" to activate'
/usr/bin/osascript -e 'tell application "Terminal" to do script "/bin/bash -rcfile /opt/kitsu-robot/robotenv/bin/backup_zou_db.rc" in window 1'
# sleep 2
# /usr/bin/osascript -e 'quit application "Terminal"'
