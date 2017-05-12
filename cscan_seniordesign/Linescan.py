# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 14:21:49 2016
Linescan

File for functions for doing a line scan (1D scan)
Hasn't been updated in god knows how long... proceed at your own risk.

@author: Mike
"""

import os
import sys
import numpy as np
import time

#### user made libs ####
import CScan_lib as CSl
import GRBL_lib as Grbl
import VISA_lib as Visa
import Console_lib as Console


###############################################################################
################################## Line Scan ##################################
###############################################################################
def lineScan(CNC, DaQ_instrument, CNC_dwell, DaQ_dwell):    
    # need to:
    Console.timeStamp('Line Scan Interface, standby 1 mike....')
    
    # TODO: integrate holding torque 'fix' into a temporary setting applied 
        # here and removed at end
    
    # TODO: Put in while loop
    step_size = input('Input step size in mm (resolution, e.g. \'1.0\') :\n')
    number_points = input('Input number of datapoints:\n')
    prefix = input('Input any file name prefix:\n')
    extension_order = input('Input order of SNP, i.e. \'2\' for *.S2P files:\n')
#    step_size = 2
#    number_points = 10
#    prefix = 'shitfix'
#    extension_order = '1'
    # TODO: Check for errors
    '''
    so lets say have 1 mm res
    and num points = 10
    
    0 1 2 3 4 5 6 7 8 9 are the positions to stop and measure
    
    so filename 0 = prefix0.0.SNP
    
    points = np.arange(0, numpoints, resolution), formatted to most sig resolution
    '{:.1f}'.format(^^that shit)
    
    # Fuck it just cutting resolution to 0.1 mm
    '''
    try:
        number_points = int(number_points)
        step_size = float(step_size)
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
    
    #Come up with position vectors
    #come up with filenames
    # print results
    points = np.arange(0, number_points*step_size, step_size)
    
    filenames = []
    positions = []
    # Not sure why had such issues here. Is same thing as below, but with index
    for i in range(len(points)):
        points[i] = '{:1.1f}'.format(points[i])
        filename = prefix + str(points[i]) + '.S' + extension_order + 'P'
        filenames.append(filename)
        positions.append(points[i])
        print(filename)

    # confirm with user
    Console.timeStamp('Will do a linescan with following parameters:\n')
    print('Move from ' + str(positions[0]) + ' to ' + str(positions[-1]) + ' (mm) savi'+\
            'ng data every ' + str(step_size) + ' (mm)')
    print('And save as these files:\n' + str(filenames[:]))
    kosher = input('Is this ok? (y/n)\n')
    if kosher == 'y' or kosher == 'Y': 
        Console.timeStamp('Operation queued.')        
        #continue
    else:
        Console.timeStamp('Operation aborted.',1)        
        return
    
    #### Begin Movement/DaQ ####
    ## Sim version
#    for points in range(number_points):
#        if points == float(positions[0]):
#            # First point, no move, just sample
#            Console.timeStamp('SIMULATION: Sampling and saving at ' + str(positions[0]))
#            print('SIMULATION: Data saved as: ' + str(filenames[points]))
#        else:
#            # Move to next position
#            #TODO: change to movement
#            Console.timeStamp('SIMULATION: Sampling and saving at ' + str(positions[points]))
#            print('SIM: Sending movement: G01 X' + str(positions[points]))
#            print('SIM: Capturing data as ' + str(filenames[points]))
            
    for points in range(number_points):
        if points == float(positions[0]):
            # First point, no move, just sample
            Console.timeStamp('Sampling and saving at ' + str(positions[0]))
            Visa.captureSNP(DaQ_instrument, str(filenames[points]))
            time.sleep(DaQ_dwell)
            print('Data saved as: ' + str(filenames[points]))
        else:
            # Move to next position
            #TODO: change to movement
            Console.timeStamp('Moving, then sampling and saving at ' + str(positions[points]))
            #print('SIM: Sending movement: G01 X' + positions[points])
            Grbl.feedrateMove(CNC, positions[points], 0)
            time.sleep(CNC_dwell)
            Visa.captureSNP(DaQ_instrument, str(filenames[points]))
            time.sleep(DaQ_dwell)
            print('Data saved as: ' + str(filenames[points]))
            
    Console.timeStamp('Line scan complete! Check to make sure files successfully sav' +
                'ed. Should have the following:\n')
    print(str(filenames[:]))
    
    
    
#DEBUGGGGGGG
def debugMode(CNC_dwell, DaQ_dwell):
    # Need to nail down movement like on program for Chaofeng and A3200
    Console.timeStamp('Demo Mode!')
    print('Need 2/3 parameters to make successful movement:\n - Distance\n' +
            ' - Resolution\n - Number of datapoints\nThe last can be' +
            ' calculated from the other two')
            # Currently, does resolution and number of datapoints, which comes
            # out to a distance. Sometimes easier to just type a distance
            # need another function to generate the movement
            
    points, distance, resolution, num_points = CSl.genPoints()
    
    prefix = input('Input any file name prefix:\n')
    extension_order = input('Input order of SNP, i.e. \'2\' for *.S2P files:\n')
    
    filenames = []
    positions = []
    # Not sure why had such issues here. Is same thing as below, but with index
    for i in range(len(points)):
        points[i] = '{:1.1f}'.format(points[i])
        filename = prefix + str(points[i]) + '.S' + extension_order + 'P'
        filenames.append(filename)
        positions.append(points[i])
        print(filename)

    # confirm with user
    Console.timeStamp('Will do a linescan with following parameters:\n')
    print('Move from ' + str(positions[0]) + ' to ' + str(positions[-1]) + ' (mm) savi'+\
            'ng data every ' + str(resolution) + ' (mm)')
    print('And save as these files:\n' + str(filenames[:]))
    kosher = input('Is this ok? (y/n)\n')
    if kosher == 'y' or kosher == 'Y': 
        Console.timeStamp('Operation queued.')        
        #continue
    else:
        Console.timeStamp('Operation aborted.',1)        
        return
        ## Sim version
        
    for points in range(len(points)):
        if points == float(positions[0]):
            # First point, no move, just sample
            Console.timeStamp('SIMULATION: Sampling and saving at ' + str(positions[0]))
            print('SIMULATION: Data saved as: ' + str(filenames[points]))
        else:
            # Move to next position
            #TODO: change to movement
            Console.timeStamp('SIMULATION: Sampling and saving at ' + str(positions[points]))
            print('SIM: Sending movement: G01 X' + str(positions[points]))
            print('SIM: Capturing data as ' + str(filenames[points]))    
    
    