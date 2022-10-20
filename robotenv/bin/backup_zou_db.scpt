tell application "Terminal"
    activate
    do script "cd /Volumes/storage/opt/zou/backups/; DB_PASSWORD=mysecretpassword /opt/zou/zouenv/bin/zou dump-database; exit 0" in window 1
end tell

set isBusy to true
repeat until isBusy is false
   tell application "Terminal"
       tell window 1
           set isBusy to busy as boolean --> Test if busy
       end tell
   end tell
   delay 1 --> Check every second
end repeat

quit application "Terminal"