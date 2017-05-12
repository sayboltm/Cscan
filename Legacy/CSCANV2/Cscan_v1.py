# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 14:22:37 2016
Cscan

separte file for cscan (2D scan)

@author: Mike
"""

import time

#### user made libs ####
import CScan_lib as CSl
import Console_lib as Console
import GRBL_lib as Grbl
import VISA_lib as Visa


###############################################################################
################################### 2D Scan ###################################
###############################################################################
def cScan(CNC, DaQ_instrument, CNC_dwell, DaQ_dwell):
    Console.timeStamp('Demo Mode!')
    print('Need 2/3 parameters to make successful movement:\n - Distance\n' +
            ' - Resolution\n - Number of datapoints\nThe last can be' +
            ' calculated from the other two')
            # Currently, does resolution and number of datapoints, which comes
            # out to a distance. Sometimes easier to just type a distance
            # need another function to generate the movement
    
    print('#################################################################' +
            '##############\n############ The following dialogue is regardin' +
            'g X AXIS settings! #############\n#############################' +
            '##################################################') 
            
    x_points, x_distance, x_resolution, x_num_points = CSl.genPoints()
    
    print('\n###############################################################' +
            '################\n############ The following dialogue is regard' +
            'ing Y AXIS settings! #############\n###########################' +
            '####################################################') 
            
    y_points, y_distance, y_resolution, y_num_points = CSl.genPoints()
    
    print('\n###############################################################' +
            '################\n')
            
    prefix = input('Input any file name prefix:\n')
    extension_order = input('Input order of SNP, i.e. \'2\' for *.S2P files:\n')
    
    filenames = []
    positions = []

    # Not sure why had such issues here. Is same thing as below, but with index
    oddloop = 0
    for j in range(len(y_points)):
        y_points[j]  = '{:1.1f}'.format(y_points[j])

        if oddloop == 0:
            posgen_range = range(len(x_points))
            oddloop = 1
        elif oddloop == 1:
            posgen_range = range(len(x_points)-1, -1, -1)
            oddloop = 0
        for i in posgen_range:
            x_points[i] = '{:1.1f}'.format(x_points[i])
            filename = prefix + '[' + str(x_points[i]) + ',' + str(y_points[j]) + ']' + '.S' + extension_order + 'P'
            filenames.append(filename)
            positions.append([x_points[i],y_points[j]])
            #print(filename)


    # confirm with user
    Console.timeStamp('Will do a linescan with following parameters:\n')
    print('Move from (x,y) [' + str(positions[0][0]) + ',' + str(positions[0][1]) + \
            '] to [' + str(positions[-1][0])  + ',' + str(positions[-1][1]) + \
            '] (mm) saving data every [' + str(x_resolution) + ',' + str(y_resolution) + '] (mm), which equates to [' + str(x_num_points) + ',' + str(y_num_points) + '] datapoints in each dir or ' + str(x_num_points*y_num_points) + ' total points.\n') 
    print('And save as these files:\n' + str(filenames[:]))
    kosher = input('Is this ok? (y/n)\n')
    if kosher == 'y' or kosher == 'Y': 
        Console.timeStamp('Operation queued.')        
        #continue
    else:
        Console.timeStamp('Operation aborted.',1)        
        return
        ## Sim version
    
    old_setting = Grbl.checkAndSetSetting(CNC, 7, 255)
    #TODO: Fixthis dialogue
    if old_setting == float(255):
        print('Previous setting of Steppers enabled detected. This was desig' +
                'ned to save power and wear on the motors so changing the va' +
                'lue to 50 instead of 255(steppers always enabled)')
        old_setting = 50
    
    firstmoverun = 1
    for pos in range(len(positions)):  
        if firstmoverun == 1:
            # First point, no move, just sample
            Console.timeStamp('Sampling and saving at [' + str(positions[0][0]) + ',' + str(positions[0][1]) + ']')
            Visa.captureSNP(DaQ_instrument, str(filenames[pos]))   
            time.sleep(DaQ_dwell)
            #print('SIMULATION: Data saved as: ' + str(filenames[pos]))
            firstmoverun = 0
        else:
            # Move to next position
            #TODO: change to movement
            Console.timeStamp('Moving, waiting for avg, then sampling and saving at ' + str(positions[pos]))
            #print('Sending movement: G01 X' + str(positions[pos][0]) + ' Y' + str(positions[pos][1]))
            Grbl.feedrateMove(CNC, positions[pos][0], positions[pos][1])
            time.sleep(CNC_dwell)   
            Visa.captureSNP(DaQ_instrument, str(filenames[pos]))
            print('Data saved as: ' + str(filenames[pos]))
            #print('SIM: Capturing data as ' + str(filenames[pos]))   
            time.sleep(DaQ_dwell)
    
    print('Moving home....')
    Grbl.feedrateMove(CNC, 0, 0)
    #time.sleep(10)   
    Grbl.checkAndSetSetting(CNC, 7, 50) 
    print('Check to make sure setting applied with settings mode. It probably didnt')
    #print('CNC steppers left enabled')
    

    Console.timeStamp('Cscan complete! Check to make sure files successfully' +
            ' saved. Should have the following:\n')
    print(str(filenames[:]))
      
''' old crap attempts at stuff
Note: this went right after CNC check and set settings, but it thinks there
is an unexpected indent in this commented block and will not run if placed
there

    # None of this crap works. Remember to poweroff or check settings mode to 
    # actually apply the setting
#    CNC.write(b'\x18')
#    print(CNC.readline())
#    print(CNC.readline())    
#    Grbl.restartCNC(CNC, port, baud_rate)      
#    #Grbl.feedrateMove(CNC, 0, 0)
'''









      
############## DEBUG MODE
def debugMode(CNC_dwell, DaQ_dwell):
    # Need to nail down movement like on program for Chaofeng and A3200
    Console.timeStamp('Demo Mode!')
    print('Need 2/3 parameters to make successful movement:\n - Distance\n' +
            ' - Resolution\n - Number of datapoints\nThe last can be' +
            ' calculated from the other two')
            # Currently, does resolution and number of datapoints, which comes
            # out to a distance. Sometimes easier to just type a distance
            # need another function to generate the movement
    
    print('#################################################################' +
            '##############\n############ The following dialogue is regardin' +
            'g X AXIS settings! #############\n#############################' +
            '##################################################') 
            
    x_points, x_distance, x_resolution, x_num_points = CSl.genPoints()
    
    print('#################################################################' +
            '##############\n############ The following dialogue is regardin' +
            'g Y AXIS settings! #############\n#############################' +
            '##################################################') 
            
    y_points, y_distance, y_resolution, y_num_points = CSl.genPoints()
    
    print('\n###############################################################' +
            '################\n')
            
    prefix = input('Input any file name prefix:\n')
    extension_order = input('Input order of SNP, i.e. \'2\' for *.S2P files:\n')
    
    filenames = []
    positions = []

    # Not sure why had such issues here. Is same thing as below, but with index
    oddloop = 0
    for j in range(len(y_points)):
        y_points[j]  = '{:1.1f}'.format(y_points[j])

        if oddloop == 0:
            posgen_range = range(len(x_points))
            oddloop = 1
        elif oddloop == 1:
            posgen_range = range(len(x_points)-1, -1, -1)
            oddloop = 0
        for i in posgen_range:
            x_points[i] = '{:1.1f}'.format(x_points[i])
            filename = prefix + '[' + str(x_points[i]) + ',' + str(y_points[j]) + ']' + '.S' + extension_order + 'P'
            filenames.append(filename)
            positions.append([x_points[i],y_points[j]])
            #print(filename)


    # confirm with user
    Console.timeStamp('Will do a linescan with following parameters:\n')
    print('Move from (x,y) [' + str(positions[0][0]) + ',' + str(positions[0][1]) + \
            '] to [' + str(positions[-1][0])  + ',' + str(positions[-1][1]) + \
            '] (mm) saving data every [' + str(x_resolution) + ',' + str(y_resolution) + '] (mm), which equates to [' + str(x_num_points) + ',' + str(y_num_points) + '] datapoints in each dir or ' + str(x_num_points*y_num_points) + ' total points.\n') 
    print('And save as these files:\n' + str(filenames[:]))
    kosher = input('Is this ok? (y/n)\n')
    if kosher == 'y' or kosher == 'Y': 
        Console.timeStamp('Operation queued.')        
        #continue
    else:
        Console.timeStamp('Operation aborted.',1)        
        return
        ## Sim version
    
    firstmoverun = 1
    for pos in range(len(positions)):  
        if firstmoverun == 1:
            # First point, no move, just sample
            Console.timeStamp('SIMULATION: Sampling and saving at [' + str(positions[0][0]) + ',' + str(positions[0][1]) + ']')
            print('SIMULATION: Data saved as: ' + str(filenames[pos]))
            firstmoverun = 0
        else:
            # Move to next position
            #TODO: change to movement
            Console.timeStamp('SIMULATION: Sampling and saving at ' + str(positions[pos]))
            print('SIM: Sending movement: G01 X' + str(positions[pos][0]) + ' Y' + str(positions[pos][1]))
            time.sleep(CNC_dwell)
            print('SIM: Capturing data as ' + str(filenames[pos]))   
            time.sleep(DaQ_dwell)
            
            
def debugModeMovement(CNC, port, baud_rate, CNC_dwell, DaQ_dwell):
    Console.timeStamp('Demo Mode!')
    print('Need 2/3 parameters to make successful movement:\n - Distance\n' +
            ' - Resolution\n - Number of datapoints\nThe last can be' +
            ' calculated from the other two')
            # Currently, does resolution and number of datapoints, which comes
            # out to a distance. Sometimes easier to just type a distance
            # need another function to generate the movement
    
    print('#################################################################' +
            '##############\n############ The following dialogue is regardin' +
            'g X AXIS settings! #############\n#############################' +
            '##################################################') 
            
    x_points, x_distance, x_resolution, x_num_points = CSl.genPoints()
    
    print('\n###############################################################' +
            '################\n############ The following dialogue is regard' +
            'ing Y AXIS settings! #############\n###########################' +
            '####################################################') 
            
    y_points, y_distance, y_resolution, y_num_points = CSl.genPoints()
    
    print('\n###############################################################' +
            '################\n')
            
    prefix = input('Input any file name prefix:\n')
    extension_order = input('Input order of SNP, i.e. \'2\' for *.S2P files:\n')
    
    filenames = []
    positions = []

    # Not sure why had such issues here. Is same thing as below, but with index
    oddloop = 0
    for j in range(len(y_points)):
        y_points[j]  = '{:1.1f}'.format(y_points[j])

        if oddloop == 0:
            posgen_range = range(len(x_points))
            oddloop = 1
        elif oddloop == 1:
            posgen_range = range(len(x_points)-1, -1, -1)
            oddloop = 0
        for i in posgen_range:
            x_points[i] = '{:1.1f}'.format(x_points[i])
            filename = prefix + '[' + str(x_points[i]) + ',' + str(y_points[j]) + ']' + '.S' + extension_order + 'P'
            filenames.append(filename)
            positions.append([x_points[i],y_points[j]])
            #print(filename)


    # confirm with user
    Console.timeStamp('Will do a linescan with following parameters:\n')
    print('Move from (x,y) [' + str(positions[0][0]) + ',' + str(positions[0][1]) + \
            '] to [' + str(positions[-1][0])  + ',' + str(positions[-1][1]) + \
            '] (mm) saving data every [' + str(x_resolution) + ',' + str(y_resolution) + '] (mm), which equates to [' + str(x_num_points) + ',' + str(y_num_points) + '] datapoints in each dir or ' + str(x_num_points*y_num_points) + ' total points.\n') 
    print('And save as these files:\n' + str(filenames[:]))
    kosher = input('Is this ok? (y/n)\n')
    if kosher == 'y' or kosher == 'Y': 
        Console.timeStamp('Operation queued.')        
        #continue
    else:
        Console.timeStamp('Operation aborted.',1)        
        return
        ## Sim version
    
    old_setting = Grbl.checkAndSetSetting(CNC, 7, 255)
    
    if old_setting == float(255):
        print('Previous setting of Steppers enabled detected. This was desig' +
                'ned to save power and wear on the motors so changing the va' +
                'lue to 50 instead of 255(steppers always enabled)')
        old_setting = 50
    
    firstmoverun = 1
    for pos in range(len(positions)):  
        if firstmoverun == 1:
            # First point, no move, just sample
            Console.timeStamp('SIMULATION: Sampling and saving at [' + str(positions[0][0]) + ',' + str(positions[0][1]) + ']')
            print('SIMULATION: Data saved as: ' + str(filenames[pos]))
            firstmoverun = 0
        else:
            # Move to next position
            #TODO: change to movement
            Console.timeStamp('Moving, then sampling and saving at ' + str(positions[pos]))
            #print('Sending movement: G01 X' + str(positions[pos][0]) + ' Y' + str(positions[pos][1]))
            Grbl.feedrateMove(CNC, positions[pos][0], positions[pos][1])
            time.sleep(CNC_dwell)   
            print('SIM: Capturing data as ' + str(filenames[pos]))   
            time.sleep(DaQ_dwell)
    
    print('Moving home....')
    Grbl.feedrateMove(CNC, 0, 0)
    #time.sleep(10)   
    Grbl.checkAndSetSetting(CNC, 7, 50) 
    print('Check to make sure setting applied with settings mode. It probably didnt')
    # None of this crap works. Remember to poweroff or check settings mode to 
    # actually apply the setting
#    CNC.write(b'\x18')
#    print(CNC.readline())
#    print(CNC.readline())    
#    Grbl.restartCNC(CNC, port, baud_rate)      
#    #Grbl.feedrateMove(CNC, 0, 0)       
            