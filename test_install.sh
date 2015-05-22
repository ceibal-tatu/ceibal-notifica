#!/bin/bash
SERVER=ceibal@192.168.1.122
SERVER=xo15
SERVER=xo175
SERVER=ub14-32

ssh $SERVER <<'CLEAN'
cd devel/tmp
rm -rf webkit
CLEAN

scp -r webkit $SERVER:./devel/tmp/
ssh $SERVER <<'INSTALL' 
cd devel/tmp/webkit/Notificador-instalador
echo 'gustavo' | sudo -S bash instalar.sh
INSTALL
