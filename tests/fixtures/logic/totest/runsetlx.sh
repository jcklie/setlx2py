for FILENAME in `find . -iname "*.stlx"` 
do `pwd`/"setlX $FILENAME" > $FILENAME.reference
done
