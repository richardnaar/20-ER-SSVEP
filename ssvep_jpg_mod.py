#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP demo with visual.ImageStim
"""
# Import the modules that we need in this script
from __future__ import division

import os

from numpy import pi, sin
from psychopy import core, event, visual

# get the current directory
dirpath = os.getcwd()
# print("current directory is : " + dirpath)

# define the path to the pictures folder
the_dir = dirpath + '\\ssvep_iaps'
all_files = list(filter(lambda x: x.endswith('.jpg'), os.listdir(the_dir)))
conditions = ['ssvep_iaps']

# Create a window to draw in
win = visual.Window(size=(1920, 1200), color='black', monitor='mon2')

pic = conditions[0]+'/'+all_files[0]
# An image using ImageStim.
#image = visual.ImageStim(win, image='pictures/face.jpg', size = 512)
image = visual.ImageStim(win, image=pic, size=500)

# Initiate clock to keep track of time
clock = core.Clock()

while clock.getTime() < 0.1:
    win.flip()

piCount = 0
while not event.getKeys('q'):

    image.opacity = .7 - (0.15*sin(2*pi*15*clock.getTime()))+0.15
#    image.opacity = (0.5*sin(2*pi*15*clock.getTime()) )+0.5
    # Show the result of all the above
    image.draw()
    win.flip()
    if event.getKeys('space'):  # &
        if len(all_files)-1 > piCount:
            piCount += 1
            pic = conditions[0]+'/'+all_files[piCount]
            image = visual.ImageStim(win, image=pic, size=500)


win.close()
core.quit()
