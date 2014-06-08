#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
from scit_resolv import *


def test_case():
    while True:
        ret = testVmDNS("192.168.1.124")
        if ret:
            os.popen("echo 0 >> test_data/test.log")
        else:
            os.popen("echo 1 >> test_data/test.log")


test_case()
