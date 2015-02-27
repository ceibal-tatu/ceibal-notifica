#!/bin/sh

echo "*****************************************************************************"
echo "********************* INSTALADOR DEL NOTIFICADOR ****************************"
echo "*****************************************************************************"

if [[ $UID -ne 0 ]]; then
echo "* - El script debe ser ejecutado como root." >&2
exit 1;
fi
echo "*"
echo "*"
echo "* VERIFICANDO SISTEMA OPERATIVO ..."
VERSION="/etc/fedora-release"
SO=""
if [[ -f $VERSION ]]; then
	SO="Fedora"
	echo "* - Su sistema operativo es: Fedora"
else
	SO="Ubuntu"
	echo "* - Su sistema operativo es: Ubuntu"
fi
echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO SISTEMA DE NOTIFICACIONES ..."
if [ "$SO" = "Fedora" ];then
    if [[ ! -d /usr/lib/python2.7/site-packages/ceibal ]]; then
        cp -r ceibal /usr/lib/python2.7/site-packages
    fi
    cp -r notifier /usr/lib/python2.7/site-packages/ceibal
    chmod -R 755 /usr/lib/python2.7/site-packages/ceibal/notifier
else
	if [[ -d /usr/lib/python2.7 ]]; then
	    if [[ ! -d /usr/lib/python2.7/dist-packages/ceibal ]]; then
    	    cp -r ceibal /usr/lib/python2.7/dist-packages
        fi
        cp -r notifier /usr/lib/python2.7/dist-packages/ceibal
        chmod -R 755 /usr/lib/python2.7/dist-packages/ceibal/notifier
	elif [[ -d /usr/lib/python2.6 ]]; then
    	if [[ ! -d /usr/lib/python2.6/dist-packages/ceibal ]]; then
    		cp -r ceibal /usr/lib/python2.6/dist-packages
        fi
        cp -r notifier /usr/lib/python2.6/dist-packages/ceibal
        chmod -R 755 /usr/lib/python2.6/dist-packages/ceibal/notifier
    else
        echo
        echo "* - No se pudieron instalar los archivos del notifier"
	fi
fi
echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO ARCHIVO CRON ..."
if [[ -d /etc/cron.d/ ]]; then
	cp cron/notifier /etc/cron.d/
fi
echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO LOS ARCHIVOS DE EJECUCION ..."
cp sbin/* /usr/sbin/
chmod 755 /usr/sbin/notificador-mostrar-html
chmod 755 /usr/sbin/notificador-obtener
echo "*"
echo "*"
echo "* DETECTO EL NOMBRE DE USUARIO ..."
echo "*"
if id -u "ceibal" >/dev/null 2>&1; then
        usuario=ceibal
elif id -u "estudiante" >/dev/null 2>&1;then
        usuario=estudiante
elif id -u "olpc" >/dev/null 2>&1;then
        usuario=olpc
else 
    usuario=$SUDO_USER
fi
echo "*"
echo "*"
echo "* AGREGO el notificador-mostrar-html AL ARRANQUE ..."
echo "*"
if [[ ! -d /home/$usuario/.config/autostart ]]; then
    mkdir /home/$usuario/.config/autostart
fi
cp notificador-mostrar.desktop /home/$usuario/.config/autostart
chown $usuario:$usuario /home/$usuario/.config/autostart/notificador-mostrar.desktop
echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO EL LOGO"
if [[ ! -d /home/$usuario/.notifier ]]; then
    mkdir /home/$usuario/.notifier
    mkdir /home/$usuario/.notifier/data
    mkdir /home/$usuario/.notifier/images
fi
cp images/planceibal.png /home/$usuario/.notifier/images/
cp boton_notificaciones.png /home/$usuario/.notifier/images/boton_notificaciones.png
chown -R $usuario:$usuario /home/$usuario/.notifier    
echo "*"
echo "*"
echo "*****************************************************************************"
echo "*************************  TERMINO LA INSTALACION  **************************"
echo "*****************************************************************************"

