#!/bin/sh

echo "*****************************************************************************"
echo "********************* INSTALADOR DEL NOTIFICADOR ****************************"
echo "*****************************************************************************"

die(){
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "              E R R O R                "
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
}


if [[ $UID -ne 0 ]]; then
    echo "* - El script debe ser ejecutado como root." >&2
    die
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
    cp -r notifier /usr/lib/python2.7/site-packages/ceibal || die
    chmod -R 755 /usr/lib/python2.7/site-packages/ceibal/notifier || die
else
                ######    U B U N T U  ######
    if [[ -d /usr/lib/python2.7 ]]; then
        cp -r notifier /usr/lib/python2.7/dist-packages/ceibal || die
        chmod -R 755 /usr/lib/python2.7/dist-packages/ceibal/notifier || die
    elif [[ -d /usr/lib/python2.6 ]]; then
        cp -r notifier /usr/lib/python2.6/dist-packages/ceibal || die
        chmod -R 755 /usr/lib/python2.6/dist-packages/ceibal/notifier || die
    else
        echo
        echo "* - No se pudieron instalar los archivos del notifier"
        die
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
    dpkg -l | grep -q sweets-sugar && SUGAR_VERSION=94
    dpkg -l | grep -q python-sugar-0.98 && SUGAR_VERSION=98
fi

if [ "$SUGAR_VERSION" = "DESCONOCIDA" ];then
    echo "* Sugar no esta instalada en el sistema"
else 
    echo "* La version de sugar instalada es: $SUGAR_VERSION"

    if [ "$SUGAR_VERSION" = "94"  ]; then
        cp sugar/sugar-session-94-f14 /usr/bin/sugar-session || die
    elif [ "$SUGAR_VERSION" = "94" -a "$SO" = "Ubuntu" ]; then
        cp sugar/sugar-session-94-ub /opt/sweets/sugar/bin/sugar-session || die
    elif [ "$SUGAR_VERSION" = "98" -a "$SO" = "Fedora" ]; then
        cp sugar/sugar-session-98-f18 /usr/bin/sugar-session || die
        cp sugar/shell-98-f18.py /usr/lib/python2.7/site-packages/jarabe/model/shell.py || die
    elif [ "$SUGAR_VERSION" = "98" -a "$SO" = "Ubuntu" ]; then
        cp sugar/sugar-session-98-ub /usr/bin/sugar-session || die
    elif [ "$SUGAR_VERSION" = "104" ]; then
        cp sugar/main-104-f20.py /usr/lib/python2.7/site-packages/jarabe/main.py || die
    else
        echo "* No hay actualizacion disponible para esta version de Sugar"
    fi
fi

echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO LOS ARCHIVOS DE EJECUCION ..."
cp sbin/* /usr/sbin/ || die
chmod 755 /usr/sbin/notificador-mostrar-html || die
chmod 755 /usr/sbin/notificador-obtener || die
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
    mkdir /home/$usuario/.config/autostart || die
fi
cp notificador-mostrar.desktop /home/$usuario/.config/autostart || die
chown $usuario:$usuario /home/$usuario/.config/autostart/notificador-mostrar.desktop || die
echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO EL LOGO"
echo "*"
if [[ ! -d /home/$usuario/.notifier ]]; then
    mkdir /home/$usuario/.notifier || die
    mkdir /home/$usuario/.notifier/data || die
fi
cp -r images  /home/$usuario/.notifier/  || die
cp no_more_notifications.html /home/$usuario/.notifier/data/ || die
echo "*"
echo "*"
echo "* VERIFICANDO E INSTALANDO CRON"
echo "*"
cat << EOF > /home/$usuario/.notifier/cron-notifier
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DISPLAY=:0

*/10 * * * * /usr/bin/python /usr/sbin/notificador-obtener
EOF
crontab -u $usuario /home/$usuario/.notifier/cron-notifier
chown -R $usuario:$usuario /home/$usuario/.notifier || die
echo "*"
echo "*"
echo "*"
echo "*"
echo "*****************************************************************************"
echo "*************************  TERMINO LA INSTALACION  **************************"
echo "*****************************************************************************"