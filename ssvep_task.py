#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP task 15/01/2020
"""
# IMPORT MODULES
# region
# future should make it possible to run the same code under Python 2
# from __future__ import absolute_import, division

import os  # system and path functions
import pandas as pd  # data structures

import serial

from numpy import pi, sin, random
from numpy.random import randint
from psychopy import locale_setup, gui, visual, core, data, event

# endregion

# Information about the experimental session
# psychopyVersion = '3.0.7'
# filename of the script
expName = os.path.basename(__file__)[1:-3] + '_' + data.getDateStr()

# expInfo = {'participant': '', 'session': '001'}
# dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
# if dlg.OK == False:
#     core.quit()  # user pressed cancel
# expInfo['date'] = data.getDateStr()  # add a simple timestamp
# expInfo['expName'] = expName
# expInfo['psychopyVersion'] = psychopyVersion

# FIND ALL FILES
# region
# Find stimuli and create a list of all_files


# get the current directory
dirpath = os.getcwd()
# print("current directory is : " + dirpath)

# define the path to the pictures folder and find the list of files
pic_dir = dirpath + '\\ssvep_iaps'
all_files = list(filter(lambda x: x.endswith('.jpg'), os.listdir(pic_dir)))
picFolder = ['ssvep_iaps']
# endregion

# Setup the Window
win = visual.Window(
    size=(1920, 1200), fullscr=True, screen=0, color='black',
    blendMode='avg', useFBO=True, monitor='mon2',
    units='deg')


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

appraisal_text = visual.TextStim(
    win=win, name='appraisal_text',
    text='juku',
    font='Arial',
    pos=(0, 0), height=1, wrapWidth=30, ori=0,
    color='white', colorSpace='rgb', opacity=1,
    languageStyle='LTR',
    depth=0.0)

VAS = visual.RatingScale(
    win=win, marker='triangle', size=1.0,
    pos=[0.0, -0.4], low=0, high=100, precision=100,
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
apprSeries = table['Neg. Tõlgenduslause eesti keeles']
picSeries = table['imageID']

# Set durartions
fixDuration = 1.5  # fixation duration
apprDuration = 3  # text duration
stimDuration = 3  # stim duration

# DEFINE FUNCTIONS
# region

# pic = picFolder[0]+'/'+all_files[0]
#pic = 'ssvep_iaps/' + str(table.imageID[0]) + '.jpg'

# and not event.getKeys('q')

# flickering picture


def draw_ssvep(win, pic, duration):
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
    while (clock.getTime() - apprStartTime) < duration:
        if not event.getKeys('q'):
            # appraisal_text.text = trialText
            appraisal_text.draw()
            win.flip()
        else:
            core.quit()

# ratings

# mingil põhjusel läheb kinni, kui kohe nupule vajutada
def draw_VAS(win, VAS, VAS_text):
    # Initialize components for Routine "VAS"
    VAS.reset()
    VASstartTime = clock.getTime()  # core.Clock()
    # VAS.setAutoDraw(True)
    while VAS.noResponse:
        if not event.getKeys('q'):
            VAS_text.draw()
            VAS.draw()
            win.flip()
        else:
            core.quit()
    # VAS.setAutoDraw(False)
    # VAS.getRating()
    # VAS.getRT()
# endregion

# for sending the triggers
# port = serial.Serial('COM3', baudrate=115200) #
# if stimulus1.status = STARTED and not stimulus1_msg_sent:
#     port.write(bytes(str(binary))) # send the message now
#     stimulus1_msg_sent = True
# or
# if stimulus1.status = STARTED and not stimulus1_msg_sent:
#     win.callOnFlip(port.write, something) # send the message when the window is updated
#     stimulus1_msg_sent = True

# port.close()


# This is the trial loop
runExperiment = True
nrTrials = 5
trials = randint(1, 100, len(picSeries))

ti = 0
while runExperiment:

    if ti == nrTrials:
        core.quit()
    # pic = picFolder[0]+'/' + str(table.imageID[ti]) + '.jpg'
    pic = picFolder[0]+'/' + str(picSeries[trials[ti]]) + '.jpg'

    # Draw fixation
    draw_fix(win, fixation, fixDuration)

    # Draw appraisal text
    appraisal_text.text = apprSeries[trials[ti]]
    draw_appraisal(win, appraisal_text, apprDuration)

    # Draw flickering picture
    draw_ssvep(win, pic, stimDuration)

    # Draw question
    VAS_text.text = 'Insert your question here...'
    draw_VAS(win, VAS, VAS_text)

    ti += 1


# close and quit
win.close()
core.quit()
