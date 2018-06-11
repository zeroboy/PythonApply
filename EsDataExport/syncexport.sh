#!/bin/bash
echo $1
if [ "$1" =  "" ]
then
  echo 'arg not empyt!'
fi

#touch `date +%Y%m%d%H%M%S`.txt

#echo $1 > `date +%Y%m%d%H%M%S`.txt

/usr/bin/python start.py $1 >/tmp/EsDataExport.log


