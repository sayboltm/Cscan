# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 14:20:22 2016
Prototype cscan for chinese laser engraver
@author: Mike
"""
'''
###############################################################################
This is the main scanning program. Run this file.
###############################################################################

Dependencies: Assuming bot use Arduino Nano ATMega328 clone uC and CH340
Chinese USB serial chip. This microcontroler is presumed to be loaded with GRBL
 software. GRBL emulates a serial interface and can be interfaced with using
 a USB serial connection and the serial library in Python. Before you can
 connect to the arduino running GRBL (effectively your CNC controller), you 
 must install the drivers for the appropriate arduino. In this specific
 instance, the laser engraver/gantry came with an Arduino Nano CH340 clone,
 but this process should work with any other arduino.

Basic steps:
Install serial drivers for Arduino Nano CH340 or other arduino
Install GRBL if not already installed (comes with Arduino IDE I think)
Install pyserial, 'pip install pyserial'

###############################################################################
Gcode is a basic instruction set for communication with CNC machines with 
syntax like: <Command> <parameters>, i.e.:
    Gsomenumber Xsomexcoord Ysomeycoord Zsomezcoord
Some Gcode commands also start with M

Some good GCODE to know for GRBL:
M05 = Turn laser OFF
M03 = Turn laser on
G0 Xsomexpointfloat Ysomeypointfloat Zsomezpointflot # move as fast as possible
G1 Xfloat Yfloat Zfloat # move at feedrate, Fvalue
G4 Ptimeinsecstopause (note: pausing may not apply holding torque)
M30 = end
% = comment

/// Development notes //// reprap stuff to translate to GRBL still
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

# This clears variables like matlab. If running on linux, you may need
# to comment out if ipython is not installed
#### clear;
#from IPython import get_ipython
#get_ipython().magic('reset -sf')
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
import Console_lib as Console # Console/timestamp functions
#import GRBL_lib as Grbl # All functions for interacting with Grbl
import GRBL_lib3 as Grbl # updated for 3rd axis support
import VISA_lib as Visa # All functions for communication over GPIB using VISA
import Cscan as CS # Cscan (as in a 2D scan) function
#import CScan_lib as CSl # Supporting functions for Cscan, also some test functions
import CScan_lib3 as CSl # 3d version of Cscan_lib
import Linescan as LS # Line scan (1D) movement functions (not used much)
import serial # for serial comms over USB

###############################################################################
######################## Begin User Defined Parameters ########################
###############################################################################
# This program merely gets user input and calls other functions which handle
# movement and use of the passed parameters

# This is the COM port that the Arduino running GRBL is connected to
#port = 'COM3'
port = 'COM1'
#baud_rate = 9600 # Baud rate should stay at 9600 as far as I know
baud_rate = 115200 # Use this baud rate for Arduino Uno Senior design
# I am not sure why 9600 served me well for my laser engraver scanner but
# does not work for this setup


# This is the address of the VNA or other GPIB data acquisition hardware
# TODO: Rename to generic name not E5071C, a specific instrument
#E5071C_addr = 'USB0::0x0957::0x0D09::MY46212637::0::INSTR'
E5071C_addr = 'GPIB0::16::INSTR'

# Dwell times, as in wait x num of secs after completing operation to go onto
# next one

# While movement must be complete to move onto the next one, this allows extra
# time for any vibrations in the fixture to settle down
CNC_dwell = 4   # Time in s, currently also being used to let avg average things

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
    ''' This mode asks Grbl for its settings, then listens to what it says
    until it hits newline (\n) characters, indicating the end of the settings
    list '''
    
    # Connect to the engraver/CNC machine and output a CNC object
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    
    # Get the settings
    Grbl.getSettings(objectCNC)

    # Close the object when finished. Else, permission will be denied when
    # trying to connect/reopen next time 
    objectCNC.close()

elif mode == 1:
    ''' This mode is for writing a setting to Grbl. Use the previous mode
    to ask Grbl for the settings so you know what they are before writing
    values to it '''
    
    Console.timeStamp('Settings modification mode.')
    
    # Get CNC object/connect, write the settings, then close the CNC object
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    Grbl.writeSettings(objectCNC)
    objectCNC.close()

elif mode == 2:
    ''' This mode is for testing the movement of the CNC machine alone. Start
    here when modifying this program for a different CNC machine. '''
    
    Console.timeStamp('Movement test mode.')
    
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    #CSl.movTestMode(objectCNC) 
    Grbl.defineFeedrate(objectCNC, 50)
    print("Finishing Definition")
    Grbl.feedrateMove(objectCNC, 500, 0, 0)
    print("end moving");
    objectCNC.close()
    
elif mode == 3:
    ''' This mode is for testing the data acquisition on the VNA or sending
    other commands over GPIB using the VISA standard. '''
    
    Console.timeStamp('Data Acquisition test mode.')
    
    # Connect to the VNA, return instrument and resource manager objects
    # Not sure what resource manager does but Agilent says to do it this way
    # Hasn't failed yet and only a few extra lines
    E5071C, rm = Visa.connectVISA(E5071C_addr)
    
    # Run test to save a file with some filename on the given instrument
    filename = input('Input a filename to test file saving on the VISA device'+
                        ':\n')
    
    CSl.daqTestMode(E5071C, filename)
    
    # Close the instrument and resource manager objects
    E5071C.close()
    rm.close()
    
elif mode == 4:
    ''' Use successful movement and VNA interaction commands to move the
    scanner/laser engraver/gantry_of_your_choice in a straight line, pausing
    to tell the VNA to save a file at various points using simple Python. 
    One small step for the CNC machine (or stepper motors, ha! get it?), 
    one giant leap for bots of all kind! '''
    
    Console.timeStamp('Line scan mode!!!!!!111') 
    
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    E5071C, rm = Visa.connectVISA(E5071C_addr)
    LS.lineScan(objectCNC, E5071C, CNC_dwell, DaQ_dwell)
    objectCNC.close()
    E5071C.close()
    rm.close()
    
    #TODO: dunno, probably an unhandled exception somewhere. If in doubt, 
    # power cycle everything and try again.
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
    ''' This is the 2D scan (known as 'cscan') mode. '''
    
    Console.timeStamp('CScan 2D scan mode. EXCELCIOR!')
    
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    E5071C, rm = Visa.connectVISA(E5071C_addr)
    
    Grbl.defineFeedrate(objectCNC, 10)
    #CS.cScan(objectCNC, E5071C, CNC_dwell, DaQ_dwell) # I removed this because requires the VNA
    CS.debugModeMovement(CNC, port, baud_rate, CNC_dwell, DaQ_dwell) # TRY THIS SHIT
    objectCNC.close()
    E5071C.close()
    rm.close()

elif mode == 6:
    ''' I think this is just an extra mode to try random stuff. It is hidden
    from the user by not printing it with the rest of the modes. Feel free to 
    add more to experiment or whatever. '''
    
    Console.timeStamp('Debug Mode.')
    CS.debugMode(CNC_dwell, DaQ_dwell)
    
elif mode == 7:
    ''' Secret mode to automatically write step size to GRBL! '''
    objectCNC = Grbl.connectGRBL(port, baud_rate)
    Grbl.writeStepsPerMM(objectCNC, 250)
    objectCNC.close()
    
else:
    Console.timeStamp('Invalid mode entered! Mode is INT in the valid range of' +
        ' modes.', 1)
        
