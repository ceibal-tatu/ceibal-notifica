PATH_UPDATE=$(awk -F "=" '/PATH_UPDATE/ {print $2}' update.conf)
PATH_NOTIFICADOR=$(awk -F "=" '/PATH_NOTIFICADOR/ {print $2}' update.conf)
PATH_MIPC=$(awk -F "=" '/PATH_MIPC/ {print $2}' update.conf)
PATH_ACTUALIZADOR=$(awk -F "=" '/PATH_ACTUALIZADOR/ {print $2}' update.conf)
LIST_UPDATES=$(awk -F "=" '/LIST_UPDATES/ {print $2}' update.conf)

git pull
sh generate-tar.sh

#limpia dir
rm -fr $PATH_UPDATE
mkdir -p $PATH_UPDATE

#copia instaladores
cp $PATH_NOTIFICADOR $PATH_UPDATE
cp $PATH_MIPC $PATH_UPDATE

#Crea instalar de la actualizacion
cat <<EOF > $PATH_UPDATE/instalar
#!/bin/bash
isFedora() {
    [ -f /etc/fedora-release ]
}

salir(){
    echo "salir"; 
    exit 0	
}

#Instala actualizacion solo para fedora 14,18,20 y ubuntu 10,12
#y borra instalacion vieja
if isFedora; then
    ! grep -q -e "Fedora 14" -e "Fedora 18" -e "Fedora 20" /etc/fedora-release && salir
    rpm -e ceibal-notifier
else	
    ! lsb_release -sr | grep -q -e "10.04" -e "12.04" && salir
    rm -fr /etc/cron.d/notificador
fi

#Elimina ceibal notifica
rm -fr /home/*/Activities/CeibalNotifica.activity
rm -fr /usr/share/applications/CeibalNotifica.desktop

cd ceibalmipc-1
bash instalar.sh

cd ../webkit/Notificador-instalador
bash instalar.sh


EOF

chmod a+x $PATH_UPDATE/instalar

#Descomprime tar.gz
cd $PATH_UPDATE
tar -xzvf ceibalmipc-1.tar.gz 
tar -xzvf instalador-webkit-devel.tar.gz
rm -fr ceibalmipc-1.tar.gz instalador-webkit-devel.tar.gz

#nautilus $PATH_UPDATE
#Generar Actualizacion
cd $PATH_ACTUALIZADOR
#DATE=$(date +"%Y%m%d")
DATE='20150501'

for i in $LIST_UPDATES; do
    sh publicar_actualizacion_biblioteca.sh $i $DATE $PATH_UPDATE
done
