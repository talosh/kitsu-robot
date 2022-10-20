#!/bin/zsh
/usr/bin/osascript -e 'tell application "Terminal" to activate'
/usr/bin/osascript -e 'tell application "Terminal" to do script "/bin/bash -c "cd /Volumes/storage/opt/zou/backups/; DB_PASSWORD=mysecretpassword /opt/zou/zouenv/bin/zou dump-database"" in window 1'
sleep 2
/usr/bin/osascript -e 'quit application "Terminal"'
