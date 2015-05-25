#!/bin/bash
SERVER=ceibal@192.168.1.122
SERVER=xo15
SERVER=dxu
SERVER=ub14-32
SERVER=xo4
SERVER=xo175

ssh $SERVER <<'CLEAN'
cd devel/tmp
rm -rf webkit
CLEAN

scp -r webkit $SERVER:./devel/tmp/
ssh $SERVER <<'INSTALL' 
cd devel/tmp/webkit/Notificador-instalador
echo 'erne2011' | sudo -S bash instalar.sh
INSTALL
