#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP task 17/01/2020
"""
# IMPORT MODULES
# region
# future should make it possible to run the same code under Python 2
# from __future__ import absolute_import, division

import os  # system and path functions
import pandas as pd  # data structures

import serial

from numpy import pi, sin, random, zeros
from numpy.random import randint
from psychopy import locale_setup, gui, visual, core, data, event, logging
from numpy.random import random, randint, shuffle

# endregion

# Set durartions
fixDuration = 1.5  # fixation duration
apprDuration = 4  # text duration
stimDuration = 6.5  # stim duration

# get the current directory
dirpath = os.getcwd()
print(dirpath)
# Information about the experimental session
# psychopyVersion = '3.0.7'
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
filename = dirpath + '\\data\\' + \
    expInfo['participant'] + expName + '_' + expInfo['date']

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

linew = 3
line = visual.ShapeStim(
    win=win, name='line',
    ori=0, pos=(0, -3),
    lineWidth=6, lineColor=[1, 1, 1], lineColorSpace='rgb',
    vertices=((-linew, 0), (linew, 0)),
    fillColor=[1, 1, 1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

line_moving = visual.ShapeStim(
    win=win, name='line',
    ori=0, pos=(0, -3),
    lineWidth=6, lineColor=[1, 0, 0], lineColorSpace='rgb',
    vertices=((-linew, 0), (linew, 0)),
    fillColor=[1, 1, 1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

appraisal_text = visual.TextStim(
    win=win, name='appraisal_text',
    text='juku',
    font='Arial',
    pos=(0, 0), height=1, wrapWidth=30, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0)

VAS = visual.RatingScale(
    # labels=(' ', ' '),
    win=win, name='VAS', marker='triangle', size=1.0, stretch=1.0,
    pos=[0.0, -0.4], low=0, high=100, precision=100, skipKeys=None,
    showValue=False, scale=None, acceptPreText='Kliki skaalal',
    acceptText='Salvestan', markerStart='50')

VAS_text = visual.TextStim(
    win=win, name='appraisal_text',
    text='VAS text',
    font='Arial',
    pos=(0, 5), height=1, wrapWidth=None, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0)
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


def draw_ssvep(win, pic, duration, picName):
    picStartTime = clock.getTime()
    image = visual.ImageStim(win, image=pic, size=30)
    while (clock.getTime() - picStartTime) < duration:
        if not event.getKeys('q'):
            image.opacity = .7 - (0.15*sin(2*pi*15*clock.getTime()))+0.15
            # Draw an image
            image.draw()
            win.flip()
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


def draw_appraisal(win, appraisal_text, duration):
    apprStartTime = clock.getTime()  # core.Clock()
    x = 0
    while (clock.getTime() - apprStartTime) < duration:
        time_passed = clock.getTime() - apprStartTime
        if not event.getKeys('q'):
            appraisal_text.draw()
            line.draw()
            x = (time_passed/duration)*(linew*2)
            line_moving.vertices = ((-linew, 0), (-linew+x, 0))
            line_moving.draw()
            win.flip()
        else:
            core.quit()
    thisExp.addData('appraisalTxt', appraisal_text.text)
# ratings

# mingil põhjusel läheb kinni, kui esimesele nupule vajutada


def draw_VAS(win, VAS, VAS_text, colName):
    # Initialize components for Routine "VAS"
    VAS.reset()
    VASstartTime = clock.getTime()
    m.setVisible(True)
    while VAS.noResponse:
        if not event.getKeys('q'):
            VAS_text.draw()
            VAS.draw()
            win.flip()
        else:
            core.quit()
    m.setVisible(False)
    # write average srate to the file
    thisExp.addData(colName, VAS.getRating())
    thisExp.addData(colName+'_RT', VAS.getRT())
    core.wait(0.25)
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


# This is the TRIAL LOOP
runExperiment = True
trials = list(range(0, len(picSeries)))
nTrials = len(trials)

appraisalCondNeg = list(zeros(25)) + list(zeros(25)+1)
appraisalCondNtr = list(zeros(25)) + list(zeros(25)+1)

shuffle(trials)
shuffle(appraisalCondNeg)
shuffle(appraisalCondNtr)

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
    draw_fix(win, fixation, fixDuration)

    # Draw flickering PICTURE (1st time)
    draw_ssvep(win, pic, stimDuration, picName)

    # Draw QUESTION (1st time)
    VAS_text.text = 'Insert your question #1 here...'
    draw_VAS(win, VAS, VAS_text, 'Qestion_1')

    # # Draw FIXATION (2nd time)
    # draw_fix(win, fixation, fixDuration)

    # Preliminary randomization scheme

    if picConditon[trials[ti]] == 'neg':
        if appraisalCondNeg[apCounterNeg] == 0:
            aCondition = 'neg'
        else:
            aCondition = 'ntr'
        apCounterNeg += 1
    else:
        if appraisalCondNtr[apCounterNtr] == 0:
            aCondition = 'neg'
        else:
            aCondition = 'ntr'
        apCounterNtr += 1

    if aCondition == 'neg':
        appraisal_text.text = apprSeriesNeg[trials[ti]]
    else:
        appraisal_text.text = apprSeriesNtr[trials[ti]]

    thisExp.addData('aValence', aCondition)
    thisExp.addData('picValence', picConditon[trials[ti]])

    # Draw APPRAISAL text
    draw_appraisal(win, appraisal_text, apprDuration)

    # Draw flickering PICTURE (2nd time)
    draw_ssvep(win, pic, stimDuration, picName)

    # Draw QUESTION (2nd time)
    VAS_text.text = 'Insert your question #2 here...'
    VAS.labels = ('left2', 'right2')
    draw_VAS(win, VAS, VAS_text, 'Qestion_2')

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
