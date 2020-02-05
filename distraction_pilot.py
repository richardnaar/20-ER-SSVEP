#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP task 04/02/2020
# monitor setting (e.g. mon2 to testMonitor)
# set up a iaps folder (ssvep_iaps)
# remove indexes after file names (eg 6570.1.jpg to 6570.jpg)
# nb - check randomization (find shuffle)
# counterbalance high and low between conditions (currently: high == distraction)
# viewing angle: 34x28 (Hajcak jt 2013)
"""

# region IMPORT MODULES

# future should make it possible to run the same code under Python 2
# from __future__ import absolute_import, division
from psychopy import sound


import psychtoolbox as ptb
import os  # system and path functions
import pandas as pd  # data structures
import numpy as np

import serial

from numpy import pi, sin, random, zeros
from numpy.random import randint
from psychopy import locale_setup, gui, visual, core, data, event, logging, sound
from numpy.random import random, randint, shuffle

# endregion

# region SET UP THE DATA
# get the current directory
dirpath = os.getcwd()
print(dirpath)
# Information about the experimental session
psychopyVersion = '3.2.4'
# filename of the script
expName = os.path.basename(__file__) # + data.getDateStr()

expInfo = {'participant': 'rn', 'session': '001', 'EEG': '0', 'Chemicum': '0', 'stimFrequency': '15','square': '0', 'testMonkey': '1', 'pauseAfterEvery': '20'}
# dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
# if dlg.OK == False:
#     core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = dirpath + '\\data\\' + expInfo['participant'] + '_' + expName + '_' + expInfo['date']

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(
    name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=dirpath + '\\' + os.path.basename(__file__),
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# this outputs to the screen, not a file
# logging.console.setLevel(logging.WARNING)

# endregion

# region SIMULUS TIMING AND SET UP THE EEG PORT

# Set durartions
if expInfo['testMonkey'] == '1':
    fixDuration = 4  # fixation duration (will change on every iteration)
    stimDuration = 12.5  # stim duration
    iti_dur = 2
    soundStart = stimDuration/2
    expInfo['participant'] = 'Monkey'
else:
    fixDuration = 4 # just the first iti, later will change on trial (random()+0.5)
    stimDuration = 12.5  # stim duration
    iti_dur = 2
    soundStart = 6.5

expInfo['stimDuration'] = stimDuration # save data
expInfo['itiDuration'] = iti_dur # save data

if expInfo['EEG'] == '1':
    from psychopy import parallel
    if expInfo['Chemicum'] == '1':
        port = parallel.ParallelPort(address=0x378)
    else:
        port = parallel.ParallelPort(address=0xe010)
        port.setData(0)
    trigNum = 0
# endregion

# region FIND FILES
# Find stimuli and create a list of all_files

# print("current directory is : " + dirpath)

# define the path to the pictures folder and find the list of files
pic_dir = dirpath + '\\ssvep_iaps'
all_files = list(filter(lambda x: x.endswith('.jpg'), os.listdir(pic_dir)))
picFolder = ['ssvep_iaps']

# Import the condion file

xls_file = pd.ExcelFile('ERSSVEP_images.xlsx')
table = xls_file.parse('ERSSVEP_images')
apprSeriesNeg = table['NEG Tõlgenduslause eesti keeles']
apprSeriesNtr = table['NTR tõlgenduslause eesti keeles ']

picConditon = table['emo']
picSeries = table['imageID']

# endregion

# region SETUP WINDOW
win = visual.Window(
    size=(1920, 1080), fullscr=True, screen=0, color='black', #size=(1920, 1200), 1920, 1080, 1536, 864, (1024, 768)
    blendMode='avg', useFBO=True, monitor='testMonitor',
    units='deg')

# Hide mouse
# win.setMouseVisible(False)
m = event.Mouse(win=win)
m.setVisible(False)
mouse = event.Mouse(win=win)

expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate']) # save data
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess


# Initiate clock to keep track of time
clock = core.Clock()
# endregion

# region INITIALIZE TASK COMPONENTS

pause_text = 'See on paus. Jätkamiseks vajuta palun hiireklahvi . . .'

start_text = 'Palun oota kuni eksperimentaator käivitab mõõtmise . . . \n\n Programmi sulgemiseks vajuta: "q"'

goodbye_text = 'Katse on lõppenud. Programmi sulgemiseks vajuta palun hiireklahvi . . . '


text = visual.TextStim(win=win,
    text='insert txt here',
    font='Arial',
    pos=(0, 0), height=1, wrapWidth=None, ori=0, 
    color='white', colorSpace='rgb', opacity=1, 
    languageStyle='LTR',
    depth=0.0);

fixation = visual.ShapeStim(
    win=win, name='fixation', vertices='cross',
    size=(1, 1),
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1, 1, 1], lineColorSpace='rgb',
    fillColor=[1, 1, 1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

background = visual.Rect(
    win=win,units='deg', 
    width=(25, 25)[0], height=(20, 20)[1],
    ori=0, pos=(0, 0),
    lineWidth=0, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

square = visual.Rect(
    win=win,units='deg', 
    width=(20, 20)[0], height=(15, 15)[1],
    ori=0, pos=(0, 0),
    lineWidth=0, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[-1,-1,-1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

# set up the sound (the pitch/octave will be changed inside the loop)
mySound = sound.Sound(
    value='A', secs=0.2, octave=3, stereo=1, volume=
    1.0, loops=0, sampleRate=48000, blockSize=128, 
    preBuffer=-1, hamming=True, autoLog=True)

# endregion

# region DEFINE FUNCTIONS

# flickering picture

def sendTrigger(trigStart,trigN, EEG):
    trigTime = clock.getTime() - trigStart 
    if EEG == '1':
        if trigTime < 0.025:
            port.setData(trigN)
        else:
            port.setData(0)

# define parameters used to draw the flickering stimuli
theta = pi/2 # phase offset
A = 0.20 # 0.3 # can't be larger than 0.5 (min = 0.5-0.5 and max = 0.5+0.5)

f = float(expInfo['stimFrequency']) # in Hz # save data
pauseAfterEvery = int(expInfo['pauseAfterEvery'])  # save data
# save these parameters to the file
expInfo['flickeringAmplitude'] = A # save data
expInfo['phaseOffset'] = theta # save data

# window, picture (cd/folder/name.jpg), duration, picture name (for data), pitch (octave), amplitude, frequecy, phase offset
def draw_ssvep(win, duration, pitch, A, f, theta, ti, trigNum):
    # print(ti-picCount)
    # print('pic_'+ str(trigNum))
    picStartTime = clock.getTime()
    soundPlayed = False
    timeC = 0
    time = clock.getTime() - picStartTime
    while (time) < duration:

        if not event.getKeys('q'):
            if expInfo['square'] == '0':
                time = win.getFutureFlipTime(clock='ptb') - picStartTime
                images[ti-picCount].opacity = (1-A) + ( A*sin(2*pi*f* time +  theta) )
            else:
                time = win.getFutureFlipTime(clock='ptb') - picStartTime
                col = 0.25*sin(2*pi*f*time)
                background.fillColor = [col,col,col]
                background.draw()
                square.draw()

            # Draw an image

            images[ti-picCount].draw()
            
            # not sure if this is really necessary
            if timeC == 0:
                duration = duration + (clock.getTime() - picStartTime) #
                # print(duration)
                timeC += 1

            # send the trigger and flip
            if not soundPlayed:
                sendTrigger(picStartTime, trigNum, expInfo['EEG'])
            win.flip()

            # play sound half way through
            if (clock.getTime() - picStartTime) > soundStart and not soundPlayed:
                mySound.setSound('A', octave = pitch)
                trigNum += 10
                # print('sound_'+ str(trigNum))
                soundTime = clock.getTime()
                # send the trigger and play
                sendTrigger(soundTime, trigNum, expInfo['EEG'])
                mySound.play()
                soundPlayed = True
            elif soundPlayed:
                sendTrigger(soundTime, trigNum, expInfo['EEG'])
        else:
            if expInfo['EEG'] == '1':
                port.setData(0)
            core.quit()
        # update time                
        time = clock.getTime() - picStartTime


# fixation
def draw_fix(win, fixation, duration, trigNum):
    # print('fix_'+ str(trigNum))
    fixStartTime = clock.getTime() # win.getFutureFlipTime(clock='ptb')  # core.Clock()
    time = clock.getTime() - fixStartTime
    while (time) < duration:
        if not event.getKeys('q'):
            if expInfo['square'] == '1':
                time = win.getFutureFlipTime(clock='ptb') - fixStartTime
                col = A*sin(2*pi*f*time)
                background.fillColor = [col,col,col]
                background.draw()
                square.draw()
            fixation.draw()
            # send the trigger and flip
            sendTrigger(fixStartTime, trigNum, expInfo['EEG'])
            win.flip()
        else:
            if expInfo['EEG'] == '1':
                port.setData(0)
            core.quit()
        time = clock.getTime() - fixStartTime

# inter-trial-interval
def draw_iti(win, iti_dur, trigNum):
    # print('iti_'+str(trigNum))
    iti_time = clock.getTime()
    time = clock.getTime() - iti_time
    while (time) < iti_dur:
        if expInfo['square'] == '1':
            time = win.getFutureFlipTime(clock='ptb') - iti_time
            col = A*sin(2*pi*f*time)
            background.fillColor = [col,col,col]
            background.draw()
            square.draw()
        # send the trigger and flip
        sendTrigger(iti_time, trigNum, expInfo['EEG'])
        win.flip()
        time = clock.getTime() - iti_time

def draw_text(txt, pause_dur):
    pause_time = clock.getTime()
    while (clock.getTime() - pause_time) < pause_dur:
        buttons = mouse.getPressed()
        theseKeys = event.getKeys(keyList=['q', 'space'])
        if len(theseKeys) == 0 and sum(buttons) == 0:
            text.setText(txt)
            text.draw()
            win.flip()
        elif sum(buttons) > 0:
            break
        elif theseKeys[0] == 'q':
            if expInfo['EEG'] == '1':
                port.setData(0)
            core.quit()
# endregion

# region IDEAS FOR TRIGGERING
# for sending the biosemi triggers
# port = serial.Serial('COM3', baudrate=115200) #
# if stimulus1.status = STARTED and not stimulus1_msg_sent:
#     port.write(bytes(str(binary))) # send the message now
#     stimulus1_msg_sent = True
# or
# if stimulus1.status = STARTED and not stimulus1_msg_sent:
#     win.callOnFlip(port.write, something) # send the message when the window is updated
#     stimulus1_msg_sent = True

# port.close()
# endregion

# region SHUFFLE TRIALS AND LOAD IMAGES
runExperiment = True
trials = list(range(0, len(picSeries)))
nTrials = len(trials)

distrCondNeg = list(zeros(25)) + list(zeros(25)+1)
appraisalCondNtr = list(zeros(25)) + list(zeros(25)+1)

shuffle(trials)
shuffle(distrCondNeg)
shuffle(appraisalCondNtr)
# pitchList = [3,5]

images = []
for file in trials[0:pauseAfterEvery]:
    images.append(visual.ImageStim(win=win, image=  pic_dir + '\\' + str(picSeries[file]) + '.jpg', units = 'deg', size = (25,20), name=str(picSeries[file])))
    if expInfo['square'] == '1':
        images[-1].size = (20,15)
#endregion

# region THIS IS THE TRIAL LOOP
draw_text(start_text, float('inf'))

picCount = 0
ti = 0
apCounterNeg = 0
apCounterNtr = 0
while runExperiment:
    expInfo['globalTime'] = clock.getTime() # save data
    m.setVisible(False) # hide the cursor
    if ti == nTrials:
        # close and quit
        draw_text(goodbye_text, float('inf'))
        if expInfo['EEG'] == '1':
            port.setData(0)
            port.close()
        win.close()
        core.quit()

    # RANDOMIZATION

    if picConditon[trials[ti]] == 'neg':
        trigNum = 1 # trigger num
        if distrCondNeg[apCounterNeg] == 0:
            distrCond = 'distr'
        else:
            distrCond = 'no-distr'
            tone = 2
        apCounterNeg += 1
    else:
        trigNum = 2
        if distrCondNeg[apCounterNtr] == 0:
            distrCond = 'distr'
        else:
            distrCond= 'no-distr'
        apCounterNtr += 1

    # define the pitch according to the distractor condition
    if distrCond == 'distr':
        pitch = 5
        trigNum += 3
    else:
        pitch = 3
        trigNum += 6

    # Draw FIXATION
    if expInfo['testMonkey'] == '0':
        fixDuration = random() + 0.5
    else:
        fixDuration = fixDuration

    trigNum += 10
    draw_fix(win, fixation, fixDuration, trigNum)


    # Draw flickering PICTURE
  
    trigNum += 10
    draw_ssvep(win, stimDuration, pitch, A, f, theta, ti, trigNum)

    # Define picture name for saving
    picName = images[ti-picCount].name

    # SAVE SOME DATA
    thisExp.addData('distraction', distrCond)
    thisExp.addData('valence', picConditon[trials[ti]])
    thisExp.addData('pictureID', picName)
    expInfo['fixDuration'] = fixDuration

    # ITI
    trigNum += 20
    draw_iti(win, iti_dur, trigNum)

    # PAUSE (preloading next set of N (pauseAfterEvery) images to achive better timing)
    pauseStart = clock.getTime() # win.getFutureFlipTime(clock='ptb')
    if (ti+1)%pauseAfterEvery == 0:
        trigNum += 10
        # print('pause_'+str(trigNum)) 

        if expInfo['testMonkey'] == '0':
            draw_text(pause_text, float('inf'))
        else:
            draw_text(pause_text, 0.2)

        sendTrigger(pauseStart, trigNum, expInfo['EEG'])

        picCount += pauseAfterEvery
        images = [] 
        start = ti
        end = ti+pauseAfterEvery

        if end > nTrials:
            end = nTrials
        # PRELOAD PICTURES FOR EACH BLOCK    
        for file in trials[start:end]:
            images.append(visual.ImageStim(win=win, image=  pic_dir + '\\' + str(picSeries[file]) + '.jpg', units = 'deg', size = (25,20), name=str(picSeries[file])))
            if expInfo['square'] == '1':
                images[-1].size = (20,15)

    thisExp.nextEntry()
    ti += 1
#endregion    

# region CLOSE AND QUIT
# these shouldn't be strictly necessary (should auto-save)
# thisExp.saveAsWideText(filename+'.csv')
# thisExp.saveAsPickle(filename)

# close and quit

