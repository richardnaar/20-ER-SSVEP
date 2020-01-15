#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP demo with visual.ImageStim
"""
# Import the modules that we need in this script
# region
# future should make it possible to run the same code under Python 2
from __future__ import absolute_import, division

import os  # system and path functions
import pandas as pd  # data structures

from numpy import pi, sin, random
from psychopy import core, event, visual
# endregion

# Information about the experimental session
# psychopyVersion = '3.0.7'
expName = os.path.basename(__file__)[1:-3]  # filename of the script

# expInfo = {'participant': '', 'session': '001'}
# dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
# if dlg.OK == False:
#     core.quit()  # user pressed cancel
# expInfo['date'] = data.getDateStr()  # add a simple timestamp
# expInfo['expName'] = expName
# expInfo['psychopyVersion'] = psychopyVersion

# Find stimuli and create a list of all_files
# region

# get the current directory
dirpath = os.getcwd()
# print("current directory is : " + dirpath)

# define the path to the pictures folder and find the list of files
pic_dir = dirpath + '\\ssvep_iaps'
all_files = list(filter(lambda x: x.endswith('.jpg'), os.listdir(pic_dir)))
conditions = ['ssvep_iaps']
# endregion

# Create a window to draw in
win = visual.Window(size=(1920, 1200), color='black', monitor='mon2')

# Initiate clock to keep track of time
clock = core.Clock()

# Import the condion file

xls_file = pd.ExcelFile('ERSSVEP_images.xlsx')
table = xls_file.parse('ERSSVEP_images')

# function to draw the pictures
duration = 3  # stim duration

# pic = conditions[0]+'/'+all_files[0]
#pic = 'ssvep_iaps/' + str(table.imageID[0]) + '.jpg'

# and not event.getKeys('q')


def draw_ssvep(win, pic, duration):
    startTime = clock.getTime()
    image = visual.ImageStim(win, image=pic, size=500)
    while (clock.getTime() - startTime) < duration:
        if not event.getKeys('q'):
            image.opacity = .7 - (0.15*sin(2*pi*15*clock.getTime()))+0.15
            # Draw an image
            image.draw()
            win.flip()
        else:
            core.quit()


# This is she trial loop
runExperiment = True
nrTrials = 2
ti = 0
while runExperiment:
    if ti == nrTrials:
        core.quit()
    pic = conditions[0]+'/' + str(table.imageID[ti]) + '.jpg'
    draw_ssvep(win, pic, duration)
    ti += 1


# close and quit
win.close()
core.quit()
