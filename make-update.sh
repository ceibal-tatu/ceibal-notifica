PATH_UPDATE=$HOME'/fuentes/actualizaciones/notificadorv2'
PATH_NOTIFICADOR='instalador-webkit-devel.tar.gz'
PATH_MIPC=$HOME'/fuentes/mi-laptop/dist/ceibalmipc-1.tar.gz'
PATH_ACTUALIZADOR=$HOME'/fuentes/generar-actualizaciones'

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


cd ceibalmipc-1
sh instalar.sh

cd ../webkit/Notificador-instalador
sh instalar.sh


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
DATE='20150422'

listVar="dxo-uy-1.75 1_0a 1_5a 1_75b 4_0b 1_25a uy-mg-1 CM_Ubuntu_a CM_Ubuntu_b BGH_Ubuntu_b BGH2_Ubuntu_b MG6_Ubuntu_b"
for i in $listVar; do
    sh publicar_actualizacion_biblioteca.sh $i $DATE $PATH_UPDATE
done
