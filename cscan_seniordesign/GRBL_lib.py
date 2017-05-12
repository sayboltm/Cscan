# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 13:58:28 2016
Gcode lib
separate lib for gcode commands

This library contains all functions relating to connecting/using/querying GRBL

@author: Mike
"""
# Built-in/community libs
import serial
import time
import sys
import os

#### user made libs ####
import Console_lib as Console

###############################################################################


def connectGRBL(port, baud_rate):
    ''' Connect to the CNC machine (laser engraver) running GRBL, return this as a 
    serial object  '''
    
    # Be persistent by putting in a for loop
    for attempt in range(10):
        # Open GRBL serial port
        try:
            s = serial.Serial(port, baud_rate)
            break
        except serial.serialutil.SerialException:
            # The connection was not closed before
            print('[-] PermissionError Exception. Connection left open!')#
            print('Type: \'objectCNC.close()\' into the console.')
            print('Close the port before proceeding. Try to automate this')
            print('Alternatively, you may not have the correct COM port. Chec'+
                    'k the Device Manager, and look under COM ports.')
            sys.exit(1)
            
#            serial.Serial.flushInput()
#            serial.Serial.flushOutput()
#            serial.Serial.close(port)
        except Exception as e:
            print('[-] SHTF.')
            # If it catastrophically fails, print all the details
            #raise # What does this do? test when code copied into next program!
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #print(exc_type, fname, exc_tb.tb_lineno) # why this not conv to str?
            print('[-] Exception Caught.\nType: ' + str(exc_type) + '\nText: ' 
                + str(e) + '\nLine: ' + str(exc_tb.tb_lineno) + '\nIn file: ' 
                + str(fname))
            sys.exit(1)
            
    # Wake up GRBL by sending these chars (found on GRBL guide)
    s.write(str.encode('\r\n\r\n'))
    time.sleep(2) # Wait for GRBL to init
    s.flushInput() # Flush startup text in serial input    
    
    Console.timeStamp('Successfully connected to CNC machine.')
    
    return s

def getSettings(s):
    ''' Function to query GRBL when given a serial object who is mapped to
    the device running GRBL '''
    
    Console.timeStamp('Querying the board for its settings.\n')
    
    # Query the machine for its settings
    # This can be sent from the console too, '$$' tells GRBL to return the 
    # settings. So to encode, send over seial and flush means the following:
    s.write(b'$$\n')
    
    # While GRBL is returning settings, keep reading/processing
    settings_avail = 1
    while settings_avail:
        shit = s.readline()
        
        # The last line is the b'ok\r\n' string, checks first two chars == ok
        # o == 111, k == 107
        if ((shit[0] == 111) and (shit[1] == 107)):
            settings_avail = 0
            continue
        else:
            # Print the decoded string for readability
            print(shit.decode('utf-8').rstrip('\r\n'))
    
    print('\n')      
    Console.timeStamp('All settings have been acquired and printed.')
    
def writeSettings(s):
    ''' Function to write settings to GRBL/controller for persistent storage'''
    
    new_setting = input('Type the setting and new valueas printed by the ' +
        'settings mode(but without the description) and hit enter. ' +
        'i.e, \'$007=7.65\'.\n')

    new_setting += '\n'
    encoded_new_setting = new_setting.encode('utf-8') # encode string before Tx
    Console.timeStamp('Sending: ' + new_setting)
    s.write(encoded_new_setting)
    printAckErrorCheck(s)
    print('\n')
    getSettings(s)
    print('Check console/log to make sure desired effect is achieved.')
    #s.flush()
    
  
    
  
def checkAndSetSetting(s, setting_num, value):
    ''' Also writes settings, but checks what the value is first and returns
    the old value. Kind of convoluted, but having a separte function for this
    works and it is easier to just leave it. Sorry. Appears to only be used
    once. (Csan.py) '''
    
    Console.timeStamp('Checking setting number: ' + str(setting_num))
    '''
    soooo..... sometimes its data is just a bunch of b'ok\r\n' for a bit until
    it wants to send the actual settings, followed by b'ok\r\n' at the end 
    which is what this loop uses to terminate. so it terminates off the bat in
    these instances, seeing the ok, leaving the list empty and failing when
    trying to grab and split a specific string from it (note: writing out
    instead of one long line may have caught this earlier). ugh
    Note to programmers: do not use W1R0 style (write once, read zero)
    '''
    
    # Query for settings
    s.write(b'$$\r\n')
    
#    settings_avail = 1
    settings_coming = 0
    settings_reg = []
#    while settings_avail:
#        shit = s.readline()
#        # The last line is the b'ok\r\n' string, checks first two chars == ok
#        if ((shit[0] == 111) and (shit[1] == 107)):
#            settings_avail = 0
#            continue
#        else:
#            # Print the decoded string for readability
#            #settings_reg.append(shit.decode('utf-8'))
#            settings_reg.append(shit.decode('utf-8').rstrip('\r\n'))
    attempt = 0            
    while 1:
#        shit = s.readline().decode('utf-8').strip('\r\n')
#        # The last line is the b'ok\r\n' string, checks first two chars == ok
#        #if ((shit[0] == 111) and (shit[1] == 107)):
#        if shit[0:2] == 'ok':
#            #settings_avail = 0
#            #continue
#            pass
#        else:
#            # Print the decoded string for readability
#            #settings_reg.append(shit.decode('utf-8'))
#            while settings_avail:
#                
#                if shit[0:2] == 'ok':
#                    settings_avail = 0
#                    break
#                else:
#                    settings_reg.append(shit)
#                    shit = s.readline().decode('utf-8').strip('\r\n')
#            break
        # sometimes other shit comes through, need to eval with whitelist not 
        # blacklist
        shit = s.readline().decode('utf-8').strip('\r\n')
        # The last line is the b'ok\r\n' string, checks first two chars == ok
        #if ((shit[0] == 111) and (shit[1] == 107)):
        # So the query command has been sent, now looks for returning string to
        # start with a '$'
        if shit[0] == '$':
            settings_reg.append(shit)
            settings_coming = 1
            #continue
        elif shit[0:2] == 'ok' and settings_coming == 1:
            break           
        else:
            # Eventually, the query will be resent if GRBL is being difficult
            attempt += 1
            if attempt == 100:
                print('Setting command ignored by machine. Resending query.')
                s.write(b'$$\r\n')
            elif attempt > 1000:
                sys.exit('Problem sending settings query!')
            
                            
            
            
    
    # Get current value
    # Replaces the equals with a space, splits at spaces and takes value alone
    current_val = settings_reg[setting_num].replace('=', ' ').split()[1]    
    
    if float(current_val) == float(value):
        Console.timeStamp('Setting #' + str(setting_num) + ' is set to: ' + current_val + '\nWhich is equal to the desired value of: ' + str(value) +'! Proceeding without change.')
    else:
        Console.timeStamp('Setting #' + str(setting_num) + ' is set to: ' + current_val + '\nWhich is NOT equal to the desired value of: ' + str(value) +'! Changing setting.... Standby.')
        
        setting = '$' + str(setting_num) + '=' + str(value) + '\r\n'
        s.write(setting.encode('utf-8'))
        printAckErrorCheck(s)
        
    return float(current_val)
      
def SetSetting(s, setting):
    # This mainly differs from 'writeSettings()' by being used internally and
    # has less vebosity.
    
    encoded_setting = setting.encode('utf-8')
    s.write(encoded_setting)
    printAckErrorCheck(s)    

def restartCNC(s, port, baud_rate):
    s.close()
    s = connectGRBL(port, baud_rate)


############################# CNC GCode Commands ##############################
''' The following functions pertain to sending Gcode to GRBL for movement or
other action by the machine. '''
  
def feedrateMove(s, x, y):
    ''' Moves the machine on s object to coords x and y at a specified (or
    default) feedrate. Feedrate = how fast to move in mm/s. '''
    
    Console.timeStamp('Sending G1 (feedrate move)....')
    
    # Send the movement command
    s.write(str.encode('G1 X' + str(x) + ' Y' + str(y) + '\r\n'))
    print('Tx Status: ' +  s.readline().decode('utf-8'))
    
    # Send realtime '?' for status update        
    s.write(b'?\r\n')
    
    # Monitor until machine is idle and/or at position (pos not needed?)    
    while 1:
        s_response = s.readline().decode('utf-8')
        status = s_response.replace('<', ' ').replace(',', ' ').split()
        if status[0] == 'ok':  
            continue
            # For debugging, uncomment to see what it's like to have a
            # conversation with a GRBL!
#            print(s_response)
#            print(status)
#            print('STATUS: ok')
        elif status[0] == 'Run':
            # only until we get back the response from the ? query should we 
            # query again, to avoid spamming GRBL. Or learn how the buffers
            # work and clear them when you need to do other things
            s.write(b'?\r\n')
#            print(s_response)
#            print(status)
#            print('Status: RUN')
        elif status[0] == 'Idle':
            #print(status[0])
#            print(s_response)
#            print(status)
            print('\t\tStatus: Movement complete.\n')
            break
        
        else:
            print(s_response)
            print(status)
            print('[-] Unexpected STATUS: ELSE!!!!')
        
 
def fastMove(s, x, y):
    ''' The G0 command tells the machine/GRBL to move as fast as possible. '''
    
    Console.timeStamp('Sending G0 (unconstrained move)....')
    s.write(str.encode('G0 X' + str(x) + ' Y' + str(y) + '\n'))
    print('Tx Status: ' +  s.readline().decode('utf-8'))
    
    # Send realtime '?' for status update        
    s.write(b'?\r\n')
    # Monitor until machine is idle and/or at position (pos not needed?)    
    while 1:
        s_response = s.readline().decode('utf-8')
        status = s_response.replace('<', ' ').replace(',', ' ').split()
        if status[0] == 'ok':  
            continue
            # For debugging
#            print(s_response)
#            print(status)
#            print('STATUS: ok')
        elif status[0] == 'Run':
            # only until we get back the response from the ? query should we 
            # query again, to avoid spamming GRBL. Or learn how the buffers
            # work and clear them when you need to do other things
            s.write(b'?\r\n')
#            print(s_response)
#            print(status)
#            print('Status: RUN')
        elif status[0] == 'Idle':
            #print(status[0])
#            print(s_response)
#            print(status)
            print('\t\tStatus: Movement complete.\n')
            break
        
        else:
            print(s_response)
            print(status)
            print('[-] Unexpected STATUS: ELSE!!!!')
            
def testFeedrateMove(s, x, y): 
    ''' Test function, probably a heap of crap. '''
    
    Console.timeStamp('Sending G1 (feedrate move)....')
    
    # Send the movement command
    s.write(str.encode('G1 X' + str(x) + ' Y' + str(y) + '\r\n'))
    
    # Monitor until machine is idle and/or at position (pos not needed?)
    while 1:
        #status = s.readline().decode('utf-8').rstrip('\r\n')
        # Send realtime '?' for status update        
        s.write(b'?\r\n')
        s_response = s.readline().decode('utf-8')
        status = s_response.replace('<', ' ').replace(',', ' ').split()
        if status[0] == 'Idle':
            print(status)
            break
        else:
            print(s_response)
            print(status)
#        if status == 'ok':
    # read the response, decode it from bytes to UTF-8 and strip trailing chars
    print('\t\tStatus: ' + s.readline().decode('utf-8').rstrip('\r\n'))
#    return
    
def pause(s, seconds):
    ''' Command to pause the machine. Note this does not apply holding torque 
    unless it has been specified in the GRBL/machine settings. i.e., if you
    pause with an arm in the air, it may succumb to the force of gravity. '''
    
    Console.timeStamp('Sending G4 (pause)....')
    s.write(str.encode('G4 P' + str(seconds) + '\n'))
    print('\t\tStatus: ' + s.readline().decode('utf-8').rstrip('\r\n'))

def printAckErrorCheck(s):
    # pretty much useless with new closed loop feedrate/fast Move
    shit = s.readline().decode('utf-8').rstrip('\r\n')
    print('\t\tStatus: ' + shit)
    if shit[0:2] != 'ok':
        Console.timeStamp('WARNING: Transmission was NOT ok!', 1)
        print('Details: ' + shit)
        
        
#settings_reg = checkAndSetSetting(objectCNC, 1, 2)
