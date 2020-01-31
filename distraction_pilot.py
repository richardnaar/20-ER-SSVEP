#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP task 30/01/2020
# quit: press "q"
# monitor setting (e.g. mon2 to testMonitor)
# set up a iaps folder (ssvep_iaps)
# remove indexes after file names (eg 6570.1.jpg to 6570.jpg)
"""
# IMPORT MODULES
# regionde
# future should make it possible to run the same code under Python 2
# from __future__ import absolute_import, division
from psychopy import sound
# from psychopy import prefs
# prefs.hardware['audioLib'] = ['SoundPTB'] # do not change it for some reason
# print(prefs.hardware)
# sound.init(48000,buffer=128)
# print('Using %s(with audio driver: %s) for sounds' %(sound.audioLib, sound.audioDriver))

import psychtoolbox as ptb
import os  # system and path functions
import pandas as pd  # data structures
import numpy as np

import serial

from numpy import pi, sin, random, zeros
from numpy.random import randint
from psychopy import locale_setup, gui, visual, core, data, event, logging, sound
from numpy.random import random, randint, shuffle

# paralleel-pordi seadistamine
# port = parallel.ParallelPort(address=0xE010)

# endregion

# sr 48000 instead of 44100 ... sound.backend_ptb.SoundPTB
mySound = sound.Sound(
    value='A', secs=0.2, octave=3, stereo=1, volume=
    1.0, loops=0, sampleRate=48000, blockSize=128, 
    preBuffer=-1, hamming=True, autoLog=True)

# get the current directory
dirpath = os.getcwd()
print(dirpath)
# Information about the experimental session
psychopyVersion = '3.2.4'
# filename of the script
expName = os.path.basename(__file__) # + data.getDateStr()

expInfo = {'participant': 'rn', 'session': '001', 'EEG': '0', 'square': '0', 'testMonkey': '1', 'pauseAfterEvery': '20'}
# dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
# if dlg.OK == False:
#     core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
# filename = _thisDir + os.sep + u'data/%s_%s_%s' %(expInfo['participant'], expName, expInfo['date'])
# filename = dirpath + '\\' + expInfo['participant'] + expName + expInfo['date']
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


# Set durartions
if expInfo['testMonkey'] == '1':
    fixDuration = 0.2  # fixation duration (will change on every iteration)
    stimDuration = 0.6  # stim duration
    iti_dur = 0.1
    expInfo['participant'] = 'Monkey'
else:
    fixDuration = random()+0.5  # fixation duration (will change on every iteration)
    stimDuration = 13  # stim duration
    iti_dur = 2

expInfo['stimDuration'] = stimDuration
expInfo['itiDuration'] = iti_dur

if expInfo['EEG'] == '1':
    from psychopy import parallel
    port = parallel.ParallelPort(address=0xe010)
    trigNum = 0

# FIND ALL FILES
# region
# Find stimuli and create a list of all_files

# print("current directory is : " + dirpath)

# define the path to the pictures folder and find the list of files
pic_dir = dirpath + '\\ssvep_iaps'
all_files = list(filter(lambda x: x.endswith('.jpg'), os.listdir(pic_dir)))
picFolder = ['ssvep_iaps']
# endregion

# Setup the Window
win = visual.Window(
    size=(1920, 1200), fullscr=True, screen=0, color='black', #size=(1920, 1200),
    blendMode='avg', useFBO=True, monitor='mon2',
    units='deg')

# Hide mouse
# win.setMouseVisible(False)
m = event.Mouse(win=win)
m.setVisible(False)
mouse = event.Mouse(win=win)

expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess


# Initiate clock to keep track of time
clock = core.Clock()

# INITIALIZE TASK COMPONENTS
# region

pause_text = 'See on paus. Jätkamiseks vajuta palun hiireklahvi . . .'

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

# gabor = visual.GratingStim(
#     win=win, name='grating',
#     tex='sin', mask=None, contrast = 1,
#     ori=90, pos=(0, 0), size=(30, 30), sf=2,
#     phase=0.0, color=[1,1,1], colorSpace='rgb', opacity=0.25,blendmode='avg',
#     texRes=128, interpolate=True, depth=0.0)

background = visual.Rect(
    win=win,units='deg', 
    width=(30, 30)[0], height=(30, 30)[1],
    ori=0, pos=(0, 0),
    lineWidth=0, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[1,1,1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

square = visual.Rect(
    win=win,units='deg', 
    width=(25, 25)[0], height=(25, 25)[1],
    ori=0, pos=(0, 0),
    lineWidth=0, lineColor=[1,1,1], lineColorSpace='rgb',
    fillColor=[-1,-1,-1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

# endregion

# Import the condion file

xls_file = pd.ExcelFile('ERSSVEP_images.xlsx')
table = xls_file.parse('ERSSVEP_images')
apprSeriesNeg = table['NEG Tõlgenduslause eesti keeles']
apprSeriesNtr = table['NTR tõlgenduslause eesti keeles ']

picConditon = table['emo']
picSeries = table['imageID']

# load images

# images = [] 

# for file in picSeries:
    # images.append(visual.ImageStim(win=win, image=  pic_dir + '\\' + str(file) + '.jpg'))

# negntr = list( table["emo"].str.find('ntr') )

# DEFINE FUNCTIONS
# region

# pic = picFolder[0]+'/'+all_files[0]
#pic = 'ssvep_iaps/' + str(table.imageID[0]) + '.jpg'

# and not event.getKeys('q')

# flickering picture

A = 0.20 # 0.3 # can't be larger than 0.5 (min = 0.5-0.5 and max = 0.5+0.5)
f = 15 # in Hz
theta = pi/2 # phase offset
pauseAfterEvery = int(expInfo['pauseAfterEvery']) 
# save these parameters to the file
expInfo['flickeringAmplitude'] = A
expInfo['frequency'] = f
expInfo['phaseOffset'] = theta

def sendTrigger(time, trigN, EEG):
    stopSending = 0
    if EEG == '1':
        if time < 0.1:
            port.setData(trigN)
        elif stopSending == 0:
            port.setData(0)
            stopSending = 1

# window, picture (cd/folder/name.jpg), duration, picture name (for data), pitch (octave), amplitude, frequecy, phase offset
def draw_ssvep(win, pic, duration, picName, pitch, A, f, theta, ti, trigNum):
    # print(ti-picCount)
    # print('pic_'+ str(trigNum))
#    image = visual.ImageStim(win, image=pic, size=25)
    picStartTime = clock.getTime()
    # picStartTime = win.getFutureFlipTime(clock='ptb')
    soundPlayed = False
    timeC = 0
    time = clock.getTime() - picStartTime
    while (time) < duration:

        if not event.getKeys('q'):
            if expInfo['square'] == '0':
                # image.opacity = (1-A) + ( A*sin(2*pi*f* time +  theta) )
                images[ti-picCount].opacity = (1-A) + ( A*sin(2*pi*f* time +  theta) )
            else:
                col = A*sin(2*pi*15*clock.getTime())
                background.fillColor = [col,col,col]
                background.draw()
                square.draw()

            # Draw an image
            sendTrigger(time, 1, expInfo['EEG'])
            # images.pop().draw()
            images[ti-picCount].draw()
            # image.draw()
            # gabor.draw()
            
            # selle asemele saaks kasutada win.getFutureFlipTime()
            if timeC == 0:
                duration = duration + (clock.getTime() - picStartTime) #
                # print(duration)
                timeC += 1
            
            win.flip()

            # play sound half way through
            if (clock.getTime() - picStartTime) > duration/2 and not soundPlayed:
                mySound.setSound('A', octave = pitch)
                trigNum += 100
                # print('sound_'+ str(trigNum))

                mySound.play()
                soundPlayed = True

            # update time    
            time = clock.getTime() - picStartTime
        else:
            core.quit()


# fixation


def draw_fix(win, fixation, duration):
    # print('fix_'+ str(trigNum))
    fixStartTime = clock.getTime()  # core.Clock()
    while (clock.getTime() - fixStartTime) < duration:
        if not event.getKeys('q'):
            if expInfo['square'] == '1':
                col = 0.25*sin(2*pi*15*clock.getTime())
                background.fillColor = [col,col,col]
                background.draw()
                square.draw()
            fixation.draw()
            win.flip()
        else:
            core.quit()

# appraisal text

def draw_iti(win, iti_dur):
    # print('iti_'+str(trigNum))
    iti_time = clock.getTime()
    while (clock.getTime() - iti_time) < iti_dur:
        if expInfo['square'] == '1':
            col = 0.25*sin(2*pi*15*clock.getTime())
            background.fillColor = [col,col,col]
            background.draw()
            square.draw()
        win.flip()


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
            core.quit()


# endregion

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

# Andero saadetud
# if frameN == 30:
#     port.setData(int(trialID))
# if frameN == 33:
#     port.setData(0)

# This is the TRIAL LOOP
runExperiment = True
trials = list(range(0, len(picSeries)))
nTrials = len(trials)

distrCondNeg = list(zeros(25)) + list(zeros(25)+1)
appraisalCondNtr = list(zeros(25)) + list(zeros(25)+1)

# shuffle(trials)
# shuffle(distrCondNeg)
# shuffle(appraisalCondNtr)
# pitchList = [3,5]

images = []

for file in trials[0:pauseAfterEvery]:
    images.append(visual.ImageStim(win=win, image=  pic_dir + '\\' + str(picSeries[file]) + '.jpg'))

picCount = 0
ti = 0
apCounterNeg = 0
apCounterNtr = 0
while runExperiment:
    trialDec =  0

    if ti == nTrials:
        win.close()
        core.quit()

    expInfo['globalTime'] = clock.getTime()

    # hide the cursor
    m.setVisible(False)
    
    # Picture
    picName = str(picSeries[trials[ti]])
    pic = picFolder[0]+'/' + picName + '.jpg'
    # image = visual.ImageStim(win, image=pic, size=25)

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
        trigNum += 10
    else:
        pitch = 3
        trigNum += 20

    # Draw FIXATION
    if expInfo['testMonkey'] == '0':
        fixDuration = random() + 0.5
    else:
        fixDuration = fixDuration

    trigNum += 1000
    draw_fix(win, fixation, fixDuration)

    # save that information on each trial
    thisExp.addData('distraction', distrCond)
    thisExp.addData('valence', picConditon[trials[ti]])
    thisExp.addData('pictureID', picName)
    expInfo['fixDuration'] = fixDuration

    # Draw flickering PICTURE
    trigNum += 1000
    draw_ssvep(win, pic, stimDuration, picName, pitch,A,f,theta, ti, trigNum)
    # trigNum += 100 # sound 

    # ITI
    trigNum += 1000
    draw_iti(win, iti_dur)

    # PAUSE (preloading next set of N (pauseAfterEvery) images to achive better timing)
    if (ti+1)%pauseAfterEvery == 0:
        trigNum += 1000
        print('pause_'+str(trigNum)) 

        if expInfo['testMonkey'] == '0':
            draw_text(pause_text, float('inf'))
        else:
            draw_text(pause_text, 0.2)

        picCount += pauseAfterEvery
        images = [] 
        start = trials[ti]
        end = trials[ti]+pauseAfterEvery
        if end > nTrials:
            end = nTrials

        for file in trials[start:end]:
            images.append(visual.ImageStim(win=win, image=  pic_dir + '\\' + str(picSeries[file]) + '.jpg'))

    thisExp.nextEntry()
    ti += 1
    
    # pause
    

# # these shouldn't be strictly necessary (should auto-save)
# thisExp.saveAsWideText(filename+'.csv')
# thisExp.saveAsPickle(filename)
# # make sure everything is closed down
# thisExp.abort()  # or data files will save again on exit

# close and quit
win.close()
core.quit()