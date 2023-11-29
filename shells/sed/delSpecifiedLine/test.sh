#!/bin/sh

echo "mdev.conf content:"
cat mdev.conf

echo
echo "app_mdev.conf content:"
cat app_mdev.conf

echo
echo "remove DEVNAME line in mdev.conf, then merge app_mdev.conf to mdev.conf"

sed -e '/DEVNAME/d' mdev.conf > mdev.tmp
cat mdev.tmp > mdev.conf
cat app_mdev.conf >> mdev.conf
rm mdev.tmp

echo "show mdev.conf content after del & merge options:"
cat mdev.conf

