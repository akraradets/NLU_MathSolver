PID=`lsof -i :9000 | awk '{ print $2 }' | sed -n 2p`

if [ -z "$PID" ]
then
    echo "The server is not started"
else
    echo "Kill process $PID"
    kill -9 $PID
fi