# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 14:07:27 2016
Device Lib

separate file for all functions regarding connection and use of devices
using VISA by using pyVisa.

@author: Mike
"""

import visa
import os
import sys

#### user made libs ####
import Console_lib as Console

############################## Device Connection ##############################

def connectVISA(address):
    ''' Connect to the DaQ instrument using VISA. '''

    try:
        rm = visa.ResourceManager()
        #E5071C_A_11_22 = ...
        Instrument = rm.open_resource(address) # Because Agilent said so
    except Exception as e:
            print('[-] SHTF.')
            #raise # What does this do? test when code copied into next program!
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #print(exc_type, fname, exc_tb.tb_lineno) # why this not conv to str?
            print('[-] Exception Caught.\nType: ' + str(exc_type) + '\nText: ' 
                + str(e) + '\nLine: ' + str(exc_tb.tb_lineno) + '\nIn file: ' 
                + str(fname))
            sys.exit(1)    
            
    Console.timeStamp('Successfully connected to VISA instrument')
    
    return Instrument, rm



    
def captureSNP(Instrument, filename):
    ''' Capture the data to the VNA, instrument, etc. '''

    try:
        ### RIGHT HERE IS THE COMMAND FOR TELLING THE VNA TO SAVE
        ### IT MIGHT BE DIFFERENT FOR A DIFFERENT INSTRUMENT
        # This is for the E5071C
        #Instrument.write(':MMEMory:STORe:SNP:DATA "%s"' % (filename))
        # This is for the E8362B
        Instrument.write(':MMEM:STOR "D:\\' + filename + '"' )

    except Exception as e:
        print('[-] SHTF.')
        #raise # What does this do? test when code copied into next program!
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #print(exc_type, fname, exc_tb.tb_lineno) # why this not conv to str?
        print('[-] Exception Caught.\nType: ' + str(exc_type) + '\nText: ' 
            + str(e) + '\nLine: ' + str(exc_tb.tb_lineno) + '\nIn file: ' 
            + str(fname))
        sys.exit(1)
        
        Console.timeStamp('Command sent. Check device to see if file: \'' + filename + 
            '\' was successfully' + ' written.')
