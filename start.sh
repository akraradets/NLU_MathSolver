# Check if the process is already started
PID=`lsof -i :9000 | awk '{ print $2 }' | sed -n 2p`
# If PID is empty
if [ -z "$PID" ]
then
    echo "Starting the server...."
    cd ./libs/stanford-corenlp
    java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -preload tokenize,ssplit,pos,lemma,ner,parse,depparse -status_port 9000 -port 9000 -timeout 15000 & 
else
    echo "[processID=$PID] The server is running or someone is using port 9000"
fi
