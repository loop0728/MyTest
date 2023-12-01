#!/bin/sh

readconf=$(readlink -f linkFile 2> /dev/null)
echo $readconf

readconf2=$(readlink -f linkXXX 2> /dev/null)
echo $readconf2

readconf3=$(readlink -f xxx 2> /dev/null)
echo $readconf3

