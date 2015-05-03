#!/bin/bash
SERVER=ub14-32

ssh $SERVER <<'CLEAN'
cd devel/tmp
rm -rf webkit
CLEAN

scp -r webkit ub14-32:./devel/tmp/
ssh $SERVER <<'INSTALL' 
cd devel/tmp/webkit/Notificador-instalador
echo 'gustavo' | sudo -S bash instalar.sh
INSTALL
