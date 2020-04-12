# CoreNLP
FILE="stanford-corenlp-full-2018-10-05.zip"
DIR="stanford-corenlp-full-2018-10-05"
LINK="stanford-corenlp"

if [ -d "./libs" ] 
then
    echo "Directory ./libs exists." 
else
    mkdir libs
    echo "Create ./libs" 
fi

cd libs

if [ -f "$FILE" ]
then
    echo "File $FILE exists." 
else
    echo "Download $FILE" 
    # wget http://nlp.stanford.edu/software/$FILE
fi

if [ -d "$DIR" ] 
then
    echo "Directory $DIR exists." 
else
    echo "unzip $FILE"
    unzip $FILE
fi

if [ -L "$LINK" ]
then
    rm $LINK
fi

echo "Create symlink"
ln -s $DIR $LINK

echo "Remove $FILE"
rm $FILE

FILE2="bert-base-srl-2019.06.17.tar.gz"
LINK2="allennlp-SRL.tar.gz"
if [ -f "$FILE2" ]
then
    echo "File $FILE2 exists." 
else
    echo "Download $FILE2" 
    wget https://s3-us-west-2.amazonaws.com/allennlp/models/$FILE2
fi

if [ -L "$LINK2" ]
then
    rm $LINK2
fi

echo "Create symlink"
ln -s $FILE2 $LINK2

echo "SUCCESS....!!!"
