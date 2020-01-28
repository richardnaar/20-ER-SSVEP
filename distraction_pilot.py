#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP task 17/01/2020
"""
# IMPORT MODULES
# region
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
from psychopy import locale_setup, gui, visual, core, data, event, logging, sound # parallel
from numpy.random import random, randint, shuffle

# paralleel-pordi seadistamine
# port = parallel.ParallelPort(address=0xE010)

# endregion

# sound
# mySound = sound.Sound('A', octave = 3, secs=0.6, sampleRate=44100, autoLog=True, loops=0, stereo=True)

# sr 48000 instead of 44100 ... sound.backend_ptb.SoundPTB
mySound = sound.Sound(
    value='A', secs=0.2, octave=3, stereo=1, volume=
    1.0, loops=0, sampleRate=48000, blockSize=128, 
    preBuffer=-1, hamming=True, autoLog=True)

# Set durartions
fixDuration = random()+0.5  # fixation duration (will change on every iteration)
stimDuration = 9  # stim duration
iti_dur = 2

# get the current directory
dirpath = os.getcwd()
print(dirpath)
# Information about the experimental session
# psychopyVersion = '3.2.4'
# filename of the script
expName = os.path.basename(__file__)[1:-3]  # + data.getDateStr()

expInfo = {'participant': 'rn', 'session': '001'}
# dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
# if dlg.OK == False:
#     core.quit()  # user pressed cancel
expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
# filename = _thisDir + os.sep + u'data/%s_%s_%s' %(expInfo['participant'], expName, expInfo['date'])
# filename = dirpath + '\\' + expInfo['participant'] + expName + expInfo['date']
filename = dirpath + '\\data\\' + expInfo['participant'] + expName + '_' + expInfo['date']

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(
    name=expName, version='',
    extraInfo=expInfo, runtimeInfo=None,
    originPath=dirpath + '\\' + os.path.basename(__file__),
    savePickle=True, saveWideText=True,
    dataFileName=filename)
# this outputs to the screen, not a file
# logging.console.setLevel(logging.WARNING)

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
    size=(1920, 1200), fullscr=True, screen=0, color='grey',
    blendMode='avg', useFBO=True, monitor='mon2',
    units='deg')

# Hide mouse
# win.setMouseVisible(False)
m = event.Mouse(win=win)
m.setVisible(False)

expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess


# Initiate clock to keep track of time
clock = core.Clock()

# INITIALIZE TASK COMPONENTS
# region

fixation = visual.ShapeStim(
    win=win, name='fixation', vertices='cross',
    size=(1, 1),
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1, 1, 1], lineColorSpace='rgb',
    fillColor=[1, 1, 1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)
# endregion

# Import the condion file

xls_file = pd.ExcelFile('ERSSVEP_images.xlsx')
table = xls_file.parse('ERSSVEP_images')
apprSeriesNeg = table['NEG Tõlgenduslause eesti keeles']
apprSeriesNtr = table['NTR tõlgenduslause eesti keeles ']

picConditon = table['emo']
picSeries = table['imageID']

# negntr = list( table["emo"].str.find('ntr') )

# DEFINE FUNCTIONS
# region

# pic = picFolder[0]+'/'+all_files[0]
#pic = 'ssvep_iaps/' + str(table.imageID[0]) + '.jpg'

# and not event.getKeys('q')

# flickering picture

def draw_ssvep(win, pic, duration, picName, pitch):
    picStartTime = clock.getTime()
    image = visual.ImageStim(win, image=pic, size=30)
    soundPlayed = False
    newVol = 1
    while (clock.getTime() - picStartTime) < duration:
        if not event.getKeys('q'):
            image.opacity = .7 - (0.15*sin(2*pi*15*clock.getTime()))+0.15
            # Draw an image
            image.draw()
            win.flip()
            if (clock.getTime() - picStartTime) > duration/2 and not soundPlayed:
                # nextFlip = win.getFutureFlipTime(clock='ptb')
                mySound.setSound('A', octave = pitch)
                mySound.play()  # when=nextFlipsync with screen refresh
                soundPlayed = True
        else:
            core.quit()
    thisExp.addData('pictureID', picName)

# fixation


def draw_fix(win, fixation, duration):
    fixStartTime = clock.getTime()  # core.Clock()
    while (clock.getTime() - fixStartTime) < duration:
        if not event.getKeys('q'):
            fixation.draw()
            win.flip()
        else:
            core.quit()

# appraisal text

def draw_iti(win, iti_dur):
    iti_time = clock.getTime()
    while (clock.getTime() - iti_time) < iti_dur:
        win.flip()

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
trials = list(range(1, len(picSeries)))
nTrials = len(trials)

distrCondNeg = list(zeros(25)) + list(zeros(25)+1)
appraisalCondNtr = list(zeros(25)) + list(zeros(25)+1)

shuffle(trials)
shuffle(distrCondNeg)
shuffle(appraisalCondNtr)
# pitchList = [3,5]

ti = 0
apCounterNeg = 0
apCounterNtr = 0
while runExperiment:

    # hide the cursor
    m.setVisible(False)
    
    if ti == nTrials:
        core.quit()

    picName = str(picSeries[trials[ti]])
    pic = picFolder[0]+'/' + picName + '.jpg'
    

    # Draw FIXATION (1st time)
    fixDuration = random() + 0.5
    draw_fix(win, fixation, fixDuration)

    # Preliminary randomization scheme

    if picConditon[trials[ti]] == 'neg':
        if distrCondNeg[apCounterNeg] == 0:
            distrCond = 'distr'
        else:
            distrCond = 'no-distr'
            tone = 2
        apCounterNeg += 1
    else:
        if distrCondNeg[apCounterNtr] == 0:
            distrCond = 'distr'
        else:
            distrCond= 'no-distr'
        apCounterNtr += 1

    if distrCond == 'distr':
        pitch = 5
    else:
        pitch = 3
    
    # Draw flickering PICTURE
    draw_ssvep(win, pic, stimDuration, picName, pitch)

    # ITI
    draw_iti(win, iti_dur)

    ti += 1
    thisExp.nextEntry()
    

# # these shouldn't be strictly necessary (should auto-save)
# thisExp.saveAsWideText(filename+'.csv')
# thisExp.saveAsPickle(filename)
# # make sure everything is closed down
# thisExp.abort()  # or data files will save again on exit

# close and quit
win.close()
core.quit()
