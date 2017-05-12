# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 14:20:22 2016
Prototype cscan for chinese laser engraver
@author: Mike
"""
'''
Dependencies: Assuming bot use Arduino Nano ATMega328 clone uC and CH340
Chinese USB serial chip

Install serial drivers for Arduino Nano CH340
Install GRBL if not already installed (comes with Arduino IDE I think)
Install pyserial, 'pip install pyserial'
'''
''' Some good GCODE to know for GRBL:
M05 = Turn laser OFF
M03 = Turn laser on
G0 Xsomexpointfloat Ysomeypointfloat Zsomezpointflot # move AFAP
G1 Xfloat Yfloat Zfloat # move at feedrate, Fvalue
G4 Ptimeinsecstopause (not hold)



M30 = end
% = comment

reprap stuff to translate to GRBL still
G91 = set to incremental Gcode
G90 = set back to absolute coords

**** NOTE: Depending on how much extra time is available, this program may NOT 
have the most robust inputs. Be nice to it and think about what types it wants
or it may crash! At the very least it should forward why it crashed. ****

Sources:
https://onehossshay.wordpress.com/2011/08/26/grbl-a-simple-python-interface/
https://onehossshay.wordpress.com/2011/08/21/grbl-how-it-works-and-other-thoughts/
http://pyserial.readthedocs.io/en/latest/pyserial_api.html
http://pyserial.readthedocs.io/en/latest/shortintro.html
https://github.com/grbl/grbl/wiki/Configuring-Grbl-v0.9
https://www.youtube.com/watch?v=XkGqyjF6XqM
'''

#### clear;
from IPython import get_ipython
get_ipython().magic('reset -sf')
#####


#import time # for sleep on init
#import datetime # for timestamp
import os # for exception catching
import sys # for program exiting in exception catching
#import serial

#import agilent.command_expert as ce

#import visa
#import time

# All needed dependent libs listed here regardless of need for reference
import CScan_lib as CSl
import GRBL_lib as Grbl
import VISA_lib as Visa
import Console_lib as Console
import Linescan as LS
import Cscan as CS
import serial # for serial comms

###############################################################################
######################## Begin User Defined Parameters ########################
###############################################################################
#port = 'COM3'
port = 'COM5'
baud_rate = 9600

#E5071C_addr = 'USB0::0x0957::0x0D09::MY46212637::0::INSTR'
E5071C_addr = 'GPIB0::16::INSTR'

# Dwell times, as in wait x num of secs after completing operation to go onto
# next one

# While movement must be complete to move onto the next one, this allows extra
# time for any vibrations in the fixture to settle down
CNC_dwell = 1 #4   # Time in s, currently also being used to let avg average things

DaQ_dwell = 1   # Time in s after sending capture command before doing
                # something else. i.e. how long VNA takes to capture data
'''Modes:
Mode 0 = Print settings
Mode 1 = Change setting
Mode 2 = Movement test (for testing just movement without the VNA connected)
Mode 3 = DAQ test (for testing just DaQ without the CNC/movement connected)
Mode 4 = Line scan
Mode 5 = CScan (2D scan)
'''
###############################################################################
###############################################################################
###############################################################################

# Print timestamp
Console.timeStamp('CSCAN V1.0 BETA Init!')

# Present program flow and query user for desired mode
print('The following modes of operation are available:\nMode 0 = Show setting'+
        's\nMode 1 = Change setting\nMode 2 = Movement test (for testing CNC '+
        'movement/connectivity alone)\nMode 3 = DaQ Test (for testing the VIS'+
        'A compatible instrument alone)\nMode 4 = Line scan\nMode 5 = CScan(2'+
        'D scan)\n')
mode = input('Input what mode to enter:\n')
#mode = 4

# Check to make sure user is not stupid and entered a char of type INT
try:
    mode = int(mode)
except Exception as e:
        print('[-] SHTF.')
        #raise # What does this do? test when code copied into next program!
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #print(exc_type, fname, exc_tb.tb_lineno) # why this not conv to str?
        print('[-] Exception Caught.\nType: ' + str(exc_type) + '\nText: ' 
            + str(e) + '\nLine: ' + str(exc_tb.tb_lineno) + '\nIn file: ' 
            + str(fname))
        sys.exit(10)
                   
############################# Begin Program Flow ##############################           
if mode == 0:    
    Console.timeStamp('Settings query mode.')
    
    # Connect to the engraver/CNC machine and output a CNC object
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    
    # Get the settings
    Grbl.getSettings(objectCNC)

    # Close the object when finished    
    objectCNC.close()

elif mode == 1:
    Console.timeStamp('Settings modification mode.')
    
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    Grbl.writeSettings(objectCNC)
    objectCNC.close()

elif mode == 2:
    Console.timeStamp('Movement test mode.')
    
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    CSl.movTestMode(objectCNC)    

    
elif mode == 3:
    Console.timeStamp('Data Acquisition test mode.')
    
    # Connect to the VNA
    E5071C, rm = Visa.connectVISA(E5071C_addr)
    
    # Run test to save a file with some filename on the given instrument
    filename = input('Input a filename to test file saving on the VISA device'+
                        ':\n')
    CSl.daqTestMode(E5071C, filename)
    
    # Close the instrument and resource manager objects
    E5071C.close()
    rm.close()
    
elif mode == 4:
    Console.timeStamp('Line scan mode!!!!!!111') 
    
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    E5071C, rm = Visa.connectVISA(E5071C_addr)
    LS.lineScan(objectCNC, E5071C, CNC_dwell, DaQ_dwell)
    objectCNC.close()
    E5071C.close()
    rm.close()
    
    #TODO:
    '''
    [-] SHTF.
[-] Exception Caught.
Type: <class 'serial.serialutil.SerialException'>
Text: could not open port 'COM4': PermissionError(13, 'Access is denied.', None, 5)
Line: 39
In file: CScan_lib.py
To exit: use 'exit', 'quit', or Ctrl-D.
An exception has occurred, use %tb to see the full traceback.

'''
    
elif mode == 5:
    Console.timeStamp('CScan 2D scan mode. EXCELCIOR!')
    
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    E5071C, rm = Visa.connectVISA(E5071C_addr)
    CS.cScan(objectCNC, E5071C, CNC_dwell, DaQ_dwell)


elif mode == 6:
    Console.timeStamp('Debug Mode.')
    CS.debugMode(CNC_dwell, DaQ_dwell)
else:
    Console.timeStamp('Invalid mode entered! Mode is INT in the valid range of' +
        ' modes.', 1)
        
