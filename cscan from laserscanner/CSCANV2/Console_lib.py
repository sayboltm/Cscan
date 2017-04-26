# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 14:01:08 2016

CONSOLE LIB: A library of useful shit for the console

Last Updated: 8/16/2016

@author: Mike
"""
import datetime

def timeStamp(text, bad=0):
#    print('[+] [{:%b-%d-%Y %H:%M:%S}] CSCAN V1.0 BETA\
#    Init!'.format(datetime.datetime.now()))
# 
    if bad == 0:
        print('[+] [{:%b-%d-%Y %H:%M:%S}] '.format(datetime.datetime.now()) +
        text)
    else:
        print('[-] [{:%b-%d-%Y %H:%M:%S}] '.format(datetime.datetime.now()) +
        text)