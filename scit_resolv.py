#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time


def testVmDNS(float_ip, dname="www.scit.com"):
    try:
        server_ip = float_ip
        ret = int(os.popen("dig @" + server_ip + " " + dname + " +time=3 +tries=2;echo $?").readlines()[-1].strip("\n"))
        if ret != 0:
            return False
        else:
            return True
    except:
        return False
