# import

# import psychopy
# from psychopy import locale_setup, gui, visual, core, data, event, logging, monitors

# import os  # system and path functions
# import pandas as pd  # data structures
# import serial
# import platform
# import sys
# import PIL

# from numpy import pi, sin, random, zeros


import numpy as np

from numpy import pi, sin
from numpy.random import random, randint, shuffle


import psychopy
from psychopy import locale_setup, visual, core, data, event, logging, monitors, gui

EEG = 0

introText = 'Siia tuleb intro tekst...'
clickMouseText = "[Jätkamiseks vajuta hiireklahvi]"

monSettings = {'size': (1024, 768), 'fullscr': False}

win = visual.Window(
    size=monSettings['size'], fullscr=monSettings['fullscr'], screen=0, color='black',
    blendMode='avg', useFBO=False, monitor='ERSSVEP',
    units='deg', waitBlanking=True)

clock = core.Clock()
calibrate = True

mouse = event.Mouse(win=win)
mouse.setVisible(False)

text_h = 0.7
text = visual.TextStim(win=win,
                       text='insert txt here',
                       font='Arial',
                       pos=(0, 0), height=text_h, wrapWidth=20, ori=0,
                       color='white', colorSpace='rgb', opacity=1,
                       languageStyle='LTR',
                       depth=0.0, alignHoriz='center')

continueText = visual.TextStim(win=win,
                               text='insert txt here',
                               font='Arial',
                               pos=(12.5, -12.5), height=text_h, wrapWidth=20, ori=0,
                               color='white', colorSpace='rgb', opacity=1,
                               languageStyle='LTR',
                               depth=0.0)


def draw_text(txt, pause_dur, mouse_resp, secondTxt):
    pause_time = clock.getTime()

    while (clock.getTime() - pause_time) < pause_dur:
        buttons = mouse.getPressed()
        theseKeys = event.getKeys(keyList=['q', 'space'])
        if len(theseKeys) == 0 and sum(buttons) == 0:
            text.setText(txt), text.draw()
            if len(secondTxt) > 0:
                continueText.setText(secondTxt), continueText.draw()
            win.flip()
        elif len(theseKeys) > 0 and theseKeys[0] == 'space' and mouse_resp == 0:
            break
        elif len(theseKeys) > 0 and theseKeys[0] == 'q':
            if expInfo['EEG'] == '1':
                port.setData(0)
                # print('port quit')
            core.quit()
        elif sum(buttons) > 0 and mouse_resp == 1:
            break


def sendTrigger(trigStart, trigN, EEG):
    trigTime = clock.getTime() - trigStart
    if EEG == 1:
        if trigTime < 0.05 and trigTime > 0:  # send trigger for 50 ms and do not send the trigger before next flip time
            port.setData(trigN)
            # print(trigN)
        else:
            port.setData(0)


def draw_calibDot(win, dotDur, position, trigN):
    startTime = clock.getTime()
    # trigDic[str(counter)]
    while (clock.getTime()-startTime) <= dotDur:
        t = startTime-clock.getTime()
        outerCircle.size = sin(2*pi*t*0.25)
        outerCircle.pos, innerCircle.pos = position, position
        outerCircle.draw(), innerCircle.draw()
        win.flip()
        sendTrigger(startTime, trigN, EEG)

        theseKeys = event.getKeys(keyList=['q', 'space'])

        if len(theseKeys) > 0 and theseKeys[0] == 'q':
            if EEG == 1:
                port.setData(0)
                calibrate = False
            core.quit()


innerCircle = visual.Polygon(
    win=win, name='innerCircle', edges=99,
    size=(0.25, 0.25),
    ori=0, pos=(0, 0),
    lineWidth=0, lineColor=[0, 0, 0], lineColorSpace='rgb',
    fillColor=[1, -1, -1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

outerCircle = visual.Polygon(
    win=win, name='outerCircle', edges=99,
    size=(0.5, 0.5),
    ori=0, pos=(0, 0),
    lineWidth=0, lineColor=[0, 0, 0], lineColorSpace='rgb',
    fillColor=[0, 0, 0], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

trigBase = '10000000'
posDic = {}
trigDic = {}
horiz = (34*0.62)-6
vert = (28*0.62)-6

h = np.linspace(-horiz, horiz, 4)
v = np.linspace(-vert, vert, 4)

counter = 0
for posy in np.flip(v):
    for posx in h:
        counter += 1
        posDic[str(counter)] = (posx, posy)
        # if counter % 2 == 0:
        #     trigDic[str(counter)] = '1'
        # else:
        #     trigDic[str(counter)] = '0'

randPosList = list(range(1, len(posDic)))
shuffle(randPosList)

draw_text(introText, float('inf'), 1, clickMouseText)

while calibrate:
    for position in randPosList:
        draw_calibDot(win, 2, posDic[str(position)], position)
        core.wait(1)
        if position == randPosList[-1]:
            calibrate = False
            # close and quit
            if EEG == 1:
                port.setData(0), port.close()
                win.close(), core.quit()

    # t = time-clock.getTime()
    # outerCircle.size = sin(2*pi*t*0.25)
    # outerCircle.draw(), innerCircle.draw()
    # win.flip()
