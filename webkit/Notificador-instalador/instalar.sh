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
                ######    F E D O R A  ######
    if [[ ! -d /usr/lib/python2.7/site-packages/ceibal ]]; then
        cp -r ceibal /usr/lib/python2.7/site-packages
    else
        cp ceibal/* /usr/lib/python2.7/site-packages/ceibal/
    fi

    cp -r notifier /usr/lib/python2.7/site-packages/ceibal
    chmod -R 755 /usr/lib/python2.7/site-packages/ceibal/notifier

else
                ######    U B U N T U  ######
	if [[ -d /usr/lib/python2.7 ]]; then
	    if [[ ! -d /usr/lib/python2.7/dist-packages/ceibal ]]; then
    	    cp -r ceibal /usr/lib/python2.7/dist-packages
        else
            cp ceibal/* /usr/lib/python2.7/dist-packages/ceibal/
        fi

        cp -r notifier /usr/lib/python2.7/dist-packages/ceibal
        chmod -R 755 /usr/lib/python2.7/dist-packages/ceibal/notifier

	elif [[ -d /usr/lib/python2.6 ]]; then
    	if [[ ! -d /usr/lib/python2.6/dist-packages/ceibal ]]; then
    		cp -r ceibal /usr/lib/python2.6/dist-packages
        else
            cp ceibal/* /usr/lib/python2.6/dist-packages/ceibal/
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
echo "* ACTUALIZANDO SUGAR-SESSION ..."
echo "*"
SUGAR_VERSION="DESCONOCIDA"

if [ "$SO" = "Fedora" ]; then
    SUGAR_VERSION=`rpm -iqa | grep "^sugar-[0-9]" | cut -d"." -f 2`
else
    if [ ! "$(dpkg -l | grep -q "python-sugar-0.98")" ]; then
        SUGAR_VERSION="98"
    fi
    if [ ! "$(dpkg -l | grep -q "sweets-sugar")" ]; then
        SUGAR_VERSION="94"
    fi
fi

if [ "$SUGAR_VERSION" = "DESCONOCIDA" ];then
    echo "* Sugar no esta instalada en el sistema"
else 
    echo "* La version de sugar instalada es: $SUGAR_VERSION"

    if [ "$SUGAR_VERSION" = "94"  ]; then
        cp sugar/sugar-session-94-f14 /usr/bin/sugar-session
    elif [ "$SUGAR_VERSION" = "94" -a "$SO" = "Ubuntu" ]; then
        cp sugar/sugar-session-94-ub /opt/sweets/sugar/bin/sugar-session
    elif [ "$SUGAR_VERSION" = "98" -a "$SO" = "Fedora" ]; then
        cp sugar/sugar-session-98-f18 /usr/bin/sugar-session
        cp sugar/shell-98-f18.py /usr/lib/python2.7/site-packages/jarabe/model/shell.py
    elif [ "$SUGAR_VERSION" = "98" -a "$SO" = "Ubuntu" ]; then
        cp sugar/sugar-session-98-ub /usr/bin/sugar-session
    elif [ "$SUGAR_VERSION" = "104" ]; then
        cp sugar/main-104-f20.py /usr/lib/python2.7/site-packages/jarabe/main.py
    else
        echo "* No hay actualizacion disponible para esta version de Sugar"
    fi
fi

echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO LOS ARCHIVOS DE EJECUCION ..."
cp sbin/* /usr/sbin/
chmod 755 /usr/sbin/notificador-mostrar-html
chmod 755 /usr/sbin/notificador-obtener
chmod 755 /usr/sbin/notificador-chequeo-cron.py
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
echo "* VERIFICANDO E INSTALANDO ARCHIVO CRON ..."
if [[ -d /etc/cron.d/ ]]; then
    cat << EOF > /etc/cron.d/notifier
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DISPLAY=:0

*/10 * * * * $usuario /usr/bin/python /usr/sbin/notificador-obtener
@reboot root /usr/bin/python /usr/sbin/notificador-chequeo-cron.py
EOF
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
cp images/* /home/$usuario/.notifier/images/
cp no_more_notifications.html /home/$usuario/.notifier/data/
chown -R $usuario:$usuario /home/$usuario/.notifier    
echo "*"
echo "* ELIMINO BASE DE DATOS INSTALADA messages.db"
rm /home/$usuario/.notifier/data/messages.db
echo "*"
echo "*"
echo "*****************************************************************************"
echo "*************************  TERMINO LA INSTALACION  **************************"
echo "*****************************************************************************"

