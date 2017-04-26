# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 10:32:40 2016
CScan functions
@author: Mike
"""

import os
import sys
import numpy as np

#### user made libs ####
import GRBL_lib as Grbl
import Console_lib as Console

###############################################################################
##################### PyCScan V1.0 BETA Function Library ######################
###############################################################################

# This contains all functions unique to this program/application

################################# Test Modes ##################################     
def movTestMode(s):
    # Do something
    # Note absolute coordinate system
    #Grbl.testFeedrateMove(s, 10, 15)  
    Grbl.feedrateMove(s, 20, 30)
    Grbl.pause(s, 5)    
    Grbl.fastMove(s, 0, 0)
    
def daqTestMode(Instrument, filename):
    try:
        #Instrument.write(':MMEMory:STORe:SNP:DATA "%s"' % (filename))
        #Instrument.write(':MMEM:STOR "%s"' % (filename)) 
        #^^^this works with D:\ added to filename during submission
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
        
    print('Check device to see if file: \'' + filename + '\' was successfully'+
        ' written.')
         
################################# Other Modes #################################    

    
def genPoints():
    
    #TODO: This nested shit seems inefficient but I guess it works. maybe make
    # modular function for any 2/3 selection stuff
    while 1:
        print('Input 1 to first specify DISTANCE.\n' +
            'Input 2 to first specify RESOLUTION/Step Size.\n' +
            'Input 3 to first specify NUMBER OF POINTS.\n')
        init_choice = input('Your choice:\n')
        
        if init_choice == '1':
            distance = input('Input distance to cover:\n')
            
            while 1:
                print('\nInput 1 to specify a RESOLUTION/Step Size.\n' + 
                        'Input 2 to specify the NUMBER OF POINTS.\n')
                second_choice = input('Your choice:\n')
                
                if second_choice == '1':
                    resolution = input('Input step/resolution in mm:\n')
                    num_points = 'calc'
                    break
                elif second_choice == '2':
                    num_points = input('Input number of points:\n')
                    resolution = 'calc'
                    break
                else:
                    print('Invalid option, redo.')
                    
            break
            
        elif init_choice == '2':
            resolution = input('Input step/resolution in mm:\n')
            
            while 1:
                print('\nInput 1 to specify a DISTANCE.\n' + 
                        'Input 2 to specify the NUMBER OF POINTS.\n')
                second_choice = input('Your choice:\n')
                
                if second_choice == '1':
                    distance = input('Input distance to cover in mm:\n')
                    num_points = 'calc'
                    break
                elif second_choice == '2':
                    num_points = input('Input number of points:\n')
                    distance = 'calc'
                    break
                else:
                    print('Invalid option, redo.')
                    
            break
                
        elif init_choice == '3':
            resolution = input('Input step/resolution in mm:\n')
            
            while 1:
                print('\nInput 1 to specify a RESOLUTION/Step Size.\n' + 
                        'Input 2 to specify the NUMBER OF POINTS.\n')
                second_choice = input('Your choice:\n')
                
                if second_choice == '1':
                    resolution = input('Input step/resolution in mm:\n')
                    num_points = 'calc'
                    break
                elif second_choice == '2':
                    num_points = input('Input number of points:\n')
                    resolution = 'calc'
                    break
                else:
                    print('Invalid option, redo.')
                    
            break
        else:
            print('Invalid option, redo.')
            
    # Check to see which option is to be calculated, and generate points
    # accordingly.
    
            
    # what was done before was use number of points and step size. start there
    if distance == 'calc':
        try:
            resolution = float(resolution)
            num_points = int(num_points)            
        except Exception as e:
            print('[-] SHTF.')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('[-] Exception Caught.\nType: ' + str(exc_type) + '\nText: ' 
                + str(e) + '\nLine: ' + str(exc_tb.tb_lineno) + '\nIn file: ' 
                + str(fname))
            print('Something wrong with types in genPoints function',1)
            sys.exit(1)
        
        points = np.arange(0, num_points*resolution, resolution)
        distance = num_points*resolution
        
    elif resolution == 'calc':
        # have distance and num_points
        try:
            distance = float(distance)
            num_points = int(num_points)
        except Exception as e:
            print('[-] SHTF.')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('[-] Exception Caught.\nType: ' + str(exc_type) + '\nText: ' 
                + str(e) + '\nLine: ' + str(exc_tb.tb_lineno) + '\nIn file: ' 
                + str(fname))
            print('Something wrong with types in genPoints function',1)
            sys.exit(1)
            
        points = np.linspace(0, distance, num_points)
        resolution = (distance+1)/num_points

    elif num_points == 'calc':
        # have distance and resolution
        try:
            distance = float(distance)
            resolution = float(resolution)
        except Exception as e:
            print('[-] SHTF.')
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('[-] Exception Caught.\nType: ' + str(exc_type) + '\nText: ' 
                + str(e) + '\nLine: ' + str(exc_tb.tb_lineno) + '\nIn file: ' 
                + str(fname))
            print('Something wrong with types in genPoints function',1)
            sys.exit(1)
            
        points = np.arange(0, distance+resolution, resolution)
        num_points = len(points)
        
    else:
        Console.timeStamp('Something is wrong with the genPoints function.',1)
        sys.exit(1)
    
    return points, distance, resolution, num_points
    


def fileNameGen():
    #TODO: Remove this or do something with it
    return 1