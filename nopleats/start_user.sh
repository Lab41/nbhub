#!/bin/bash
echo "---- Socat ----"
# get a copy of the docker information through the docker port
sudo socat -d -d TCP-LISTEN:41000,fork UNIX:/var/run/docker.sock >/dev/null 2>&1  &

echo "---- Get self ----"
# take a short nap so the socket is available for use.
# make the docker datastructure into environment variables.
sleep 1
curl http://localhost:41000/containers/json > /tmp/self
for i in `(/usr/bin/python /opt/nopleats/readData.py /tmp/self)`; do export $i; done

echo "---- Env ----"
# echo check the sorted environent
/usr/bin/env | /usr/bin/sort

echo "---- Adding user ----"
# add the external user
/usr/bin/mo /opt/nopleats/add_user_stub > /opt/nopleats/add_user.sh; chmod +x /opt/nopleats/add_user.sh
/opt/nopleats/add_user.sh


echo "---- Starting filebeat ----"
/usr/bin/mo /opt/nopleats/filebeat_basic.yaml  > /etc/filebeat/filebeat.yml
mkdir /var/log/self
chmod 755 /var/log/self
service filebeat start
cp /tmp/self /var/log/self


echo "---- Syslog ----"
#start the syslog if it is defined
if [ "${!L41_RSYSLOG_HOST-x}" = "x" -a "${L41_RSYSLOG_HOST-y}" = "y" ]; then
    echo "Rsyslog not used"
else
    echo "---- Writing out rsyslog conf ----"
    /usr/bin/mo /opt/nopleats/rsyslogsetup > /etc/rsyslog.d/10-lab41.conf

    echo "---- Start syslog ----"
    service rsyslog start
    logger `/bin/cat /tmp/self`
fi

echo "---- Making app output dir ----"
# make the output directory if it is defined
if [ "${!L41_MAKE_DIR-x}" = "x" -a "${L41_MAKE_DIR-y}" = "y" ]; then
    echo "no directory to make"
else
    echo Creating ${L41_MAKE_DIR}
    mkdir -p ${L41_MAKE_DIR}
    chmod 777 ${L41_MAKE_DIR}
fi

cd /opt/super
set +e
for i in `(ls | sort -n )`; do . ./$i ; done


cd /opt/user
for i in `(ls | sort -n )`; do sudo -E -u ${L41_USERNAME} bash -c "cd /home/${L41_USERNAME}; /opt/user/$i" ; done
echo "---- done ----"
