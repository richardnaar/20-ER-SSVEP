# EOG calibration

# import

import numpy as np

from numpy import pi, sin
from numpy.random import random, randint, shuffle

import os  # system and path functions
import psychopy
from psychopy import locale_setup, visual, core, data, event, logging, monitors, gui, sound


expInfo = {'participant': 'Participant', 'EEG': '0', 'Chemicum': '0'}

if expInfo['EEG'] == '1':
    # print('set port')
    from psychopy import parallel
    if expInfo['Chemicum'] == '1':
        port = parallel.ParallelPort(address=0x378)
    else:
        port = parallel.ParallelPort(address=0xe010)
        port.setData(0)

dirpath = os.getcwd()
dataDir = dirpath + '\\data\\'
date = data.getDateStr()
filename = expInfo['participant'] + '-EOG-calib' + date + '.txt'

with open(dataDir+filename, 'a') as file_object:
    file_object.write('Participant' + ',' +
                      'Position' + ',' + 'x' + ',' + 'y' + '\n')

dlg = gui.DlgFromDict(dictionary=expInfo, title='EOG-calibration')
if dlg.OK == False:
    core.quit()  # user pressed cancel

introText = 'Enne katsega alustamist seadistame Sinu näole asetatud elektroode.\n\nKui katse läbiviija on programmi käivitanud, ilmuvad ekraanile väikesed ringid. Sinu ülesandeks\
on neid ringe hoolikalt vaadata.\n\n\n\nPalun oota kuni eksperimentaator käivitab katse...'
clickMouseText = "[Jätkamiseks vajuta hiireklahvi]"
byeTxt = 'Aitäh, kalibreerimine on lõppenud. Kutsu palun katse läbiviija.'

monSettings = {'size': (800, 600), 'fullscr': True}

win = visual.Window(
    size=monSettings['size'], fullscr=monSettings['fullscr'], screen=0, color='black',
    blendMode='avg', useFBO=False, monitor='ERSSVEP',
    units='deg', waitBlanking=True)

clock = core.Clock()
calibrate = True
tic = clock.getTime()

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


def sendTrigger(trigStart, trigN):
    trigTime = clock.getTime() - trigStart
    if expInfo['EEG'] == '1':
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
        outerCircle.size = sin(2*pi*t*(0.5/dotDur))
        outerCircle.pos, innerCircle.pos = position, position
        outerCircle.draw(), innerCircle.draw()
        win.flip()
        sendTrigger(startTime, trigN)

        theseKeys = event.getKeys(keyList=['q', 'space'])

        if len(theseKeys) > 0 and theseKeys[0] == 'q':
            if expInfo['EEG'] == '1':
                port.setData(0)
                calibrate = False
            core.quit()


def playSounds():
    short, long = 0.5, 1
    note_c = sound.Sound(value="C", secs=short, octave=4, hamming=True)
    note_e = sound.Sound(value="E", secs=short, octave=4, hamming=True)
    note_d = sound.Sound(value="D", secs=short, octave=4, hamming=True)
    note_ee = sound.Sound(value="E", secs=long, octave=4, hamming=True)

    note_e.play(), core.wait(short), note_c.play(), core.wait(
        short), note_d.play(), core.wait(short), note_ee.play()


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
horiz = round(34*0.62)-10
vert = round(28*0.62)-10

h = np.linspace(-horiz, horiz, 4)
v = np.linspace(-vert, vert, 4)

counter = 0
for posy in np.flip(v):
    for posx in h:
        counter += 1
        posDic[str(counter)] = (posx, posy)

randPosList = list(range(1, len(posDic)+1))
np.random.shuffle(randPosList)

draw_text(introText, float('inf'), 0, [])

# with open(dataDir+filename, 'a') as file_object:
#     file_object.write("\nI love making games.")

while calibrate:
    for position in randPosList:
        draw_calibDot(win, 2.5, posDic[str(position)], position)
        core.wait(0.5)
        win.flip()
        with open(dataDir+filename, 'a') as file_object:
            file_object.write(
                expInfo['participant'] + ',' + str(position) + ',' + str(posDic[str(position)][0]) + ',' + str(posDic[str(position)][1]) + '\n')
        core.wait(0.5)
        if position == randPosList[-1]:
            playSounds()
            draw_text(byeTxt,  float('inf'), 1, clickMouseText)
            doc = clock.getTime()
            print('aeg: ' + str(doc-tic))
            calibrate = False
            # close and quit
            if expInfo['EEG'] == '1':
                core.wait(0.25)
                port.setData(0)
                win.close(), core.quit()
