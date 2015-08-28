#!/bin/bash
SERVER=xo15
SERVER=xo175
SERVER=test12
SERVER=ceibal@192.168.0.106

ssh $SERVER <<'CLEAN'
cd devel/tmp
rm -rf webkit
CLEAN

scp -r instalador $SERVER:./devel/tmp/
ssh $SERVER <<'INSTALL' 
cd devel/tmp/instalador
echo 'gustavo' | sudo -S bash instalar.sh
INSTALL
