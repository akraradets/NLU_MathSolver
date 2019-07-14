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
    wget http://nlp.stanford.edu/software/$FILE
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

echo "SUCCESS....!!!"
