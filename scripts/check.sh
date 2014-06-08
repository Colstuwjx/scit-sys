#!/bin/bash -
#for vm
#self-check and shutdown dns service when found error
while true;
do
    dig @127.0.0.1 www.scit.com +time=3 +tries=2;
    if [ $? -ne 0 ];
    then
        service named stop;
    fi

    NAMED_CONF=$(md5sum /etc/named.conf |cut -d' ' -f1)
    SCIT_DATA=$(md5sum /var/named/scit.com.zone |cut -d' ' -f1)
    if [ ${NAMED_CONF} != "b1446a1be362dac71e5e1d9a6e7028fe" || ${SCIT_DATA} != "8880ba0a002b0166a9dbc21bf96a51e0" ];
    then
        service named stop;
    fi
done
