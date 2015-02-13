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
    if [[ -d /usr/lib/python2.7/site-packages/ceibal/notifier ]]; then
    	cp notifier/* /usr/lib/python2.7/site-packages/ceibal/notifier
    	chmod -R 755 /usr/lib/python2.7/site-packages/ceibal/notifier
    else
    	echo
    	echo "* - No se pudieron instalar los archivos del notifier"
	fi
else
	if [[ -d /usr/lib/python2.7/dist-packages/ceibal/notifier ]]; then
    	    cp notifier/* /usr/lib/python2.7/dist-packages/ceibal/notifier
    	    chmod -R 755 /usr/lib/python2.7/dist-packages/ceibal/notifier
    else
    	if [[ -d /usr/lib/python2.6/dist-packages/ceibal/notifier ]]; then
    		cp notifier/* /usr/lib/python2.6/dist-packages/ceibal/notifier
    	    chmod -R 755 /usr/lib/python2.6/dist-packages/ceibal/notifier
    	else
    		echo
    		echo "* - No se pudieron instalar los archivos del notifier"
        fi
	fi
fi
echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO EJECUCION AL ARRANQUE ..."
if [ "$SO" = "Fedora" ];then
	if [[ -d /home/olpc/.config/autostart ]]; then
		cp auto-start/python.desktop /home/olpc/.config/autostart
		chmod -R 755 /home/olpc/.config/autostart/python.desktop
		chown olpc:olpc /home/olpc/.config/autostart/python.desktop
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
echo "* VERIFICANDO E INSTALANDO EL LOGO Y DB..."
if [[ -d /etc/notifier/ ]]; then
	cp messages.db /etc/notifier/data/
	chmod 777 /etc/notifier/data/messages.db
	cp images/planceibal.png /etc/notifier/images/
	chmod 777 /etc/notifier/images/planceibal.png
fi
echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO LOS ARCHIVOS DE EJECUCION ..."
cp sbin/* /usr/sbin/
chmod 755 /usr/sbin/notificador-mostrar
chmod 755 /usr/sbin/notificador-mostrar-html
chmod 755 /usr/sbin/notificador-obtener
echo "*"
echo "*"
echo "* INSTALANDO PROGRAMA CEIBAL NOTIFICA ..."
if [[ ! -d /usr/local/share/CeibalNotifica ]]; then
	mkdir /usr/local/share/CeibalNotifica
fi
cp -r ceibal_notifica/* /usr/local/share/CeibalNotifica/
chmod -R 755 /usr/local/share/CeibalNotifica/
cp CeibalNotifica.desktop /usr/share/applications/
cp CeibalNotifica /usr/local/bin/
chmod 755 /usr/local/bin/CeibalNotifica
echo "*"
echo "*"
echo "* INSTALANDO ACTIVIDAD CEIBAL NOTIFICA ..."
if [[ -d /home/olpc/Activities/CeibalNotifica.activity ]]; then
	cp ceibal_notifica/CeibalNotifica-for-Sugar.py /home/olpc/Activities/CeibalNotifica.activity/CeibalNotifica.py
	chmod 755 /home/olpc/Activities/CeibalNotifica.activity/CeibalNotifica.py
	cp ceibal_notifica/store.py /home/olpc/Activities/CeibalNotifica.activity/
	chmod 755 /home/olpc/Activities/CeibalNotifica.activity/store.py
fi
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
    echo "Nombre de usuario desconocido"
fi
echo "*"
echo "*"
echo "* AGREGO el notificador-mostrar-html AL ARRANQUE ..."
echo "*"
if [[ -d /home/$usuario/.config/autostart ]]; then
    cp notificador-mostrar.desktop /home/$usuario/.config/autostart
    chown $usuario:$usuario /home/$usuario/.config/autostart/notificador-mostrar.desktop
else
    mkdir /home/$usuario/.config/autostart
    cp notificador-mostrar.desktop /home/$usuario/.config/autostart
    chown $usuario:$usuario /home/$usuario/.config/autostart/notificador-mostrar.desktop
fi

echo "*****************************************************************************"
echo "*************************  TERMINO LA INSTALACION  **************************"
echo "*****************************************************************************"

