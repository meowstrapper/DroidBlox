#!/system/bin/sh
robloxPID = ""
while [ -z "$robloxPID" ]; do
    robloxPID = "${pidof com.roblox.client}"
    if [ -z "$robloxPID" ]; then
        echo hi
        sleep 1
    fi
done

logcat --pid $robloxPID &
logcatPID=$!

while true; do
    if [ -z "$(pidof com.roblox.client)"]; then
        kill $logcatPID
        exit 1;
    fi
    sleep 1
done