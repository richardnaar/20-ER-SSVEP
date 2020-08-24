#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP task 21/08/2020
monitor setting (e.g. testMonitor to ERSSVEP)
set up the folders (ssvep_iaps, training_pics, intro_pics)
viewing angle: 34x28 (Hajcak jt 2013)
NB - programmi katkestamiseks vajuta klaviatuuril "q"
"""

# C:\Program Files\PsychoPy3\Lib\site-packages\psychopy\demos\coder\stimuli

# region IMPORT MODULES

# future should make it possible to run the same code under Python 2
# from __future__ import absolute_import, division
import psychopy
from psychopy import locale_setup, gui, visual, core, data, event, logging, monitors

import os  # system and path functions
import pandas as pd  # data structures
import serial
import platform
import sys
import PIL

from numpy import pi, sin, random, zeros
from numpy.random import random, randint, shuffle

import numpy as np

# endregion (IMPORT MODULES )

# region DEFINE PICTURE FOLDERS (and name of the condition file)
# relative to the os.getcwd()
intro_pictures = 'stimuli\\instructions'  # folder with the intro pictures
training_pics = 'stimuli\\practice'  # folder with the training pictures
ssvep_exp = 'stimuli\\images'  # folder with the experimental pictures
conditionFile = 'ERSSVEP_images'  # name of the condition file

# endregion DEFINE PICTURE FOLDERS

# region SET UP THE INFO DIALOG AND EXPERIMENT HANDLER
# get the current directory
dirpath = os.getcwd()

# Information about the experimental session
psychopyVersion = psychopy.__version__
print('PsychoPy version: ' + psychopy.__version__)

# filename of the script
expName = os.path.basename(__file__)  # + data.getDateStr()

expInfo = {'participant': 'Participant', 'session': '001', 'EEG': '0', 'Chemicum': '0',
           'stimFrequency': '15', 'testMonkey': '0', 'pauseAfterEvery': '32', 'countFrames': '1', 'reExposure': '0', 'triggerTest': '0', 'showIntro': '1'}

dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Set durartions
if expInfo['testMonkey'] == '1':
    fixDuration, stimDuration, iti_dur_default, secondCueTime, expInfo['participant'] = \
        1.5,        12.6,           3.5,   [
            6.6, 7.08, 7.56, 8.04], 'Monkey'  # 0.1,        1,              0.2,        [0.1, 0.2, 0.3, 0.4], 'Monkey'
else:
    # just the first iti, later will change on every trial (random()+0.5)
    fixDuration, stimDuration, iti_dur_default, secondCueTime = \
        1.5,        12.6,           3.5,   [
            6.6, 7.08, 7.56, 8.04]  # [6, 6.32, 6.64,6.96]  [6, 6.48, 6.96, 7.44]

expInfo['stimDuration'] = stimDuration  # save data
expInfo['itiDuration'] = str(iti_dur_default) + '+/- 0.5'  # save data

# Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
filename = dirpath + '\\data\\' + \
    expInfo['participant'] + '_' + expName + '_' + expInfo['date']

print('Data folder and filename... ' + filename[-48:])

runInfo = str(platform.uname()[0:])

# An ExperimentHandler isn't essential but helps with data saving
thisExp = data.ExperimentHandler(
    name=expName, version=psychopyVersion,
    extraInfo=expInfo, runtimeInfo=None,
    originPath=dirpath + '\\' + os.path.basename(__file__),
    savePickle=True, saveWideText=True,
    dataFileName=filename)

# endregion (SET UP THE EPERIMENT INFO DATA)

# region EEG PORT SETUP

if expInfo['EEG'] == '1':
    # print('set port')
    from psychopy import parallel
    if expInfo['Chemicum'] == '1':
        port = parallel.ParallelPort(address=0x378)
    else:
        port = parallel.ParallelPort(address=0xe010)
        port.setData(0)

trigdic = {'training': '0', 'experiment': '1', 'VAATA PILTI': '1', 'LOENDA': '0', 'NEG': '1', 'NEUTRAL': '0',
           'a': '00', 'b': '10', 'c': '01', 'd': '11', 'first': '00', 'second': '10', 'question': '11'}

trigger = str()

# endregion (EEG PORT SETUP)

# region FIND FILES
# Find stimuli and create a list of all_files

print("current directory is : " + dirpath)

# pictures (pptx slides convered to pictures) used in the introduction
try:
    intro_dir = dirpath + '\\' + intro_pictures
    introfiles = list(
        filter(lambda x: x.endswith('.JPG'), os.listdir(intro_dir)))
    for slide in introfiles:
        if len(slide) < 11:  # (e.g. Slide01.JPG vs Slide1.JPG)
            os.rename(intro_dir+'\\'+slide, intro_dir +
                      '\\'+slide[:-5]+'0'+slide[5:])
    introfiles = list(
        filter(lambda x: x.endswith('.JPG'), os.listdir(intro_dir)))
    # pictures used in the training loop
    training_dir = dirpath + '\\' + training_pics
    trainingfiles = list(
        filter(lambda x: x.endswith('.jpg'), os.listdir(training_dir)))
    # pictures used in the experiment
    pic_dir = dirpath + '\\' + ssvep_exp
    all_files = list(filter(lambda x: x.endswith('.jpg'), os.listdir(pic_dir)))
    noData = False
except:
    print('NB! A problem with locating the pictures. Using example pictures instead...')
    example_pictures_dir = 'C:\\Program Files\\PsychoPy3\\Lib\site-packages\psychopy\demos\coder\stimuli'
    intro_dir, training_dir, pic_dir = example_pictures_dir, example_pictures_dir, example_pictures_dir
    introfiles = list(
        filter(lambda x: x.endswith('.jpg'), os.listdir(intro_dir)))
    # introfiles.sort()
    # pictures used in the training loop
    trainingfiles = list(
        filter(lambda x: x.endswith('.jpg'), os.listdir(training_dir)))
    # pictures used in the experiment
    all_files = list(filter(lambda x: x.endswith('.jpg'), os.listdir(pic_dir)))
    noData = True
# Import the condion file
try:
    xls_file = pd.ExcelFile(conditionFile + '.xlsx')
    table = xls_file.parse()  # 'ERSSVEP_images'
except:
    print('Can\'t find condition table... Are you sure that the name of the condition file is: ' + conditionFile + '?')

# endregion (FIND FILES)

# region RANDOMIZATION
if noData == False:
    # sort by emo and picset
    table = table.sort_values(['emo', 'picset']).reset_index(drop=True)
    # define newTable as data frame in pandas
    newTable, picsets = pd.DataFrame(), np.unique(table['picset'])
    # randomize picsets
    shuffle(picsets)
    trueSetSize, counter, tilist = int(len(table)/len(picsets)), 0, list()

    # iterate randomly through all the picsets
    for seti in picsets:
        # pick the subset of the data
        currentset = table[table['picset'] == seti].reset_index(drop=True)
        # tilist randomizes trials within each set
        rndtilist = list(range(counter*trueSetSize, trueSetSize * (counter+1)))
        shuffle(rndtilist)
        tilist = tilist + rndtilist
        # iterate through all the emo categories
        for valencei in np.unique(currentset['emo']):
            # define conditions and 2nd cue times for each emotion category and each set seperately
            emoSetInCurrent = currentset[currentset['emo']
                                         == valencei].reset_index(drop=True)
            # condition data
            condlist = list(range(1, 5))*4
            emoSetInCurrent['cond'] = condlist

            # present question once in each condition (25 % of the time if 8 design cells and 32 pics in the set)
            setSize = len(emoSetInCurrent)
            numberOfAConds = len(np.unique(emoSetInCurrent['cond']))
            rndQM = np.zeros((int(setSize/numberOfAConds), numberOfAConds))
            rndQM[randint(len(rndQM))] = 1
            # rndQM[0:len(rndQM)] = 1  # just for debugging - comment out later
            emoSetInCurrent['presentVAS'] = np.squeeze(
                np.asarray(rndQM)).reshape(-1).astype(int)

            # randomize condition and question presentation
            emoSetInCurrent[['cond', 'presentVAS']] = emoSetInCurrent[[
                'cond', 'presentVAS']].sample(frac=1).reset_index(drop=True)

            # emoSetInCurrent['countingQuestion'] = zeros(setSize)
            # emoSetInCurrent['countingQuestion'][randint(setSize)] = 1

            secondCueRndList = list()
            for sndcue in range(0, int(np.ceil(setSize/len(secondCueTime)))+1):
                shuffle(secondCueTime)
                secondCueRndList = secondCueRndList+secondCueTime
            secondCueRndList = secondCueRndList[0:setSize]
            # # define 2nd cue times similarly for each emotion category in each set separately
            # secondCueRndList = secondCueTime * \
            #     int(np.ceil(setSize/len(secondCueTime)))
            # secondCueRndList = secondCueRndList[0:setSize]
            # shuffle(secondCueRndList)
            emoSetInCurrent = emoSetInCurrent.sort_values(
                ['cond']).reset_index(drop=True)
            emoSetInCurrent['secondCueTime'] = secondCueRndList

            # this randomization is not strictly nessesary since 'tilist' (see below) shuffles the trials within each set already
            emoSetInCurrent = emoSetInCurrent.sample(
                frac=1).reset_index(drop=True)
            newTable = newTable.append(emoSetInCurrent).reset_index(drop=True)
        counter += 1

    # sorting vased on trialID ensures that the trilas are shuffled within each picset
    newTable['trialID'] = tilist
    newTable = newTable.sort_values(['trialID']).reset_index(drop=True)

    newTable['cond'] = newTable['cond'].astype(str)
    picConditon = newTable['emo']
    picSeries = newTable['imageFile']


# define box colors and randomize
boxcols = [[1.000, 0.804, 0.004], [-1.000, 0.686, 0.639]]
shuffle(boxcols)
# colstrdic can be used in the instructions
if boxcols[0][0] > 0:
    colstrdic = {'VAATA PILTI': 'kollane', 'LOENDA': 'sinine'}
else:
    colstrdic = {'VAATA PILTI': 'sinine', 'LOENDA': 'kollane'}
# these two dictionaries are used to set the box colour and to present appraisal cue according to the conditions 1 to 4
coldic = {'1': [boxcols[0], boxcols[0]], '2': [boxcols[0], boxcols[1]],
          '3': [boxcols[1], boxcols[1]], '4': [boxcols[1], boxcols[0]]}
condic = {'1': ['VAATA PILTI', 'VAATA PILTI'], '2': ['VAATA PILTI', 'LOENDA'],
          '3': ['LOENDA', 'LOENDA'], '4': ['LOENDA', 'VAATA PILTI']}
# this will be used to print digits from the upper half on the screen randomly
intOnScreen = np.linspace(150, 950, 9)

# endregion (RANDOMIZATION)


# region SETUP WINDOW

if expInfo['testMonkey'] == '1':
    monSettings = {'size': (1920/2, 1080/2), 'fullscr': False}
    boxdenom = float('inf')
else:
    # (1024, 768) (1920, 1200)
    monSettings = {'size': (1024, 768), 'fullscr': True}
    boxdenom = float('inf')  # 2.8

win = visual.Window(
    size=monSettings['size'], fullscr=monSettings['fullscr'], screen=0, color='black',
    blendMode='avg', useFBO=True, monitor='ERSSVEP',
    units='deg')

# Hide mouse

mouse = event.Mouse(win=win)
mouse.setVisible(False)

expInfo['frameRate'] = win.getActualFrameRate()
print(expInfo['frameRate'])
if expInfo['frameRate'] != None:
    frameDur = round(expInfo['frameRate'])  # save data
    print('the monitor refresh rate is: ' + str(frameDur))
else:
    frameDur = 'NaN'  # could not measure, so NaN
    print('could not measure refresh rate... this should not happen')

# use frameRate to add data and to define moduloNr

pauseAfterEvery = int(expInfo['pauseAfterEvery'])  # save data
if expInfo['countFrames'] == 0:
    # define parameters used to draw the flickering stimuli
    theta = pi/2  # constant phase offset
    f = float(expInfo['stimFrequency'])  # in Hz # save data
    # save these parameters to the file
    expInfo['phaseOffset'] = theta  # save data
    # 0.3 # can't be larger than 0.5 (min = 0.5-0.5 and max = 0.5+0.5)
    A = 0.20
    expInfo['flickeringAmplitude'] = A  # save data
else:
    moduloNr = int(
        np.ceil(round(float(expInfo['frameRate'])) / float(expInfo['stimFrequency']))*0.5)
    A = 0.20
    expInfo['contrastChange'] = A*2  # save data
    expInfo['actualFrequency'] = np.ceil(
        round(float(expInfo['frameRate'])))/(moduloNr*2)

# endregion (SETUP WINDOW)

# region INITIALIZE TASK COMPONENTS

horiz, vert = 34*0.5, 28*0.5,
picSize = (horiz, vert)

pause_text = 'See on paus. Palun oota kuni eksperimentaator taaskäivitab mõõtmise . . .'
practice_text1 = "Katse jooksul näidatakse Sulle ükshaaval erinevaid pilte.\n\nSinu ülesandeks on iga pildi vaatamise ajal teha seda, \
mida pildile eelnev märksõna ütleb.\n\nVAATA PILTI: Keskendu pildil kujutatule ja reageeri loomulikult.\n\nLOENDA: Loenda etteantud \
arvust kahekaupa allapoole, et vähendada negatiivseid tundeid.\n\nAbiks on pilti ümbritsev raam. \n\nKui raam on " + colstrdic["VAATA PILTI"] + \
    ", siis tuleb pilti lihtsalt vaadata ja kui " + \
    colstrdic["LOENDA"] + ", siis pildi vaatamise ajal arve loendada.\n\nKatses on pilte, kus pildi esitamise ajal ülesanne \
muutub - esialgu tuleb märksõna VAATA PILTI ja seejärel LOENDA või vastupidi. Koos ülesande muutumisega muutub ka raami värv."
practice_text2 = "Palun kirjelda oma sõnadega, mida Sa pead katse ajal tegema."
practice_text3 = "Järgmiseks tutvustame sulle katse ajal esitatavat küsimust."
# practice_text4 = "Kui negativselt sa ennast hetkel tunned?\n\n\n\n\n\n\n\n\n\n\n\nÜldse mitte negatiivselt ------------- Väga negatiivselt"
practice_text4 = "Nüüd saad kirjeldatud ülesannet näitepiltidega harjutada."

practiceTextDic = {'1': practice_text1, '2': practice_text2,
                   '3': practice_text3, '4': practice_text4}

start_text1 = "Aitäh, harjutus on läbi ja nüüd algab katse põhiosa! Oota kuni katse läbiviija on ruumist lahkunud."
start_text2_1 = "Meeldetuletuseks: Tee iga pildi vaatamise ajal seda, mida märksõna ütleb. \n\n\
VAATA PILTI: Keskendu pildil kujutatule ja reageeri loomulikult. \n\n\
LOENDA: Loenda arve etteantud arvust kahekaupa allapoole, et vähendada negatiivseid tundeid. \n\n"
start_text2_2 = "Sind aitab pilti ümbritseva raami värv. \n\nKui raam on " + colstrdic["VAATA PILTI"] + \
    ", siis vaata pilti ja kui " + \
    colstrdic["LOENDA"] + ", siis loenda. \n\nAlusta juhendi rakendamist kohe, kui pilt ekraanile ilmub. \n\n\
Katses on pilte, kus pildi esitamise ajal ülesanne muutub.\nProovi uut juhendit rakendada kohe, kui märksõna ja raami värv muutuvad."
start_text3 = 'Palun oota kuni eksperimentaator käivitab mõõtmise . . .'

expTextDic = {'1': start_text1, '2': start_text2_1+start_text2_2,
              '3': start_text3}

clickMouseText = "[Jätkamiseks vajuta hiireklahvi]"


goodbye_text = 'Aitäh! Katse on läbi! Kutsu katse läbiviija. \n\nPärast mõõtevahendite eemaldamist palume Sul vastata teises ruumis lühikesele küsimustikule \
\n\nProgrammi sulgemiseks vajuta palun hiireklahvi . . . '

self_VAS = 'Kui negatiivselt sa ennast hetkel tunned?'
self_VAS_min = 'Väga negatiivselt'
self_VAS_max = 'Üldse mitte negatiivselt'

# Initiate clock to keep track of time
clock = core.Clock()
text_h = 0.65
text = visual.TextStim(win=win,
                       text='insert txt here',
                       font='Arial',
                       pos=(0, 0), height=text_h, wrapWidth=20, ori=0,
                       color='white', colorSpace='rgb', opacity=1,
                       languageStyle='LTR',
                       depth=0.0, alignHoriz ='center')  # 

continueText = visual.TextStim(win=win,
                               text='insert txt here',
                               font='Arial',
                               pos=(15, -15), height=text_h, wrapWidth=20, ori=0,
                               color='white', colorSpace='rgb', opacity=1,
                               languageStyle='LTR',
                               depth=0.0)

fixation = visual.ShapeStim(
    win=win, name='fixation', vertices='cross',
    size=(1, 1),
    ori=0, pos=(0, 0),
    lineWidth=1, lineColor=[1, 1, 1], lineColorSpace='rgb',
    fillColor=[1, 1, 1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)
# the frame
background = visual.Rect(
    win=win, units='deg',
    width=(horiz+2, horiz+2)[0], height=(vert+2, vert+2)[1],
    ori=0, pos=(0, 0),
    lineWidth=0, lineColor=[1, 1, 1], lineColorSpace='rgb',
    fillColor=[1, 1, 1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)
# subtitle box
subbox = visual.Rect(
    win=win, units='deg',
    width=(5, 5)[0], height=(1, 1)[1],
    ori=0, pos=(0, -horiz/boxdenom),
    lineWidth=0, lineColor=[1, 1, 1], lineColorSpace='rgb',
    fillColor=[-1, -1, -1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

# Initialize components for Routine "vas"
scale_width = 5
scale_y_pos = -2

item = visual.TextStim(win=win, name='item',
                       text='default text',
                       font='Arial',
                       pos=(0, 5), height=text_h, wrapWidth=20, ori=0, units='deg',
                       color=[0.702, 0.702, 0.702], colorSpace='rgb', opacity=1,
                       languageStyle='LTR',
                       depth=-1.0)
scale_low = visual.TextStim(win=win, name='scale_low',
                            text='default text',
                            font='Arial',
                            pos=(-scale_width-3, scale_y_pos), height=text_h, wrapWidth=3, ori=0, units='deg',
                            color=[0.702, 0.702, 0.702], colorSpace='rgb', opacity=1,
                            languageStyle='LTR',
                            depth=-2.0)
scale_high = visual.TextStim(win=win, name='scale_high',
                             text='default text',
                             font='Arial',
                             pos=(scale_width+4, scale_y_pos), height=text_h, wrapWidth=3, ori=0, units='deg',
                             color=[0.702, 0.702, 0.702], colorSpace='rgb', opacity=1,
                             languageStyle='LTR',
                             depth=-3.0)

slf_scale = visual.Rect(
    win=win, name='slf_scale',
    width=(scale_width*2, 0)[0], height=(0.25, 0.25)[1], ori=0, pos=(0, scale_y_pos), units='deg',
    lineWidth=text_h, lineColor=[0.702, 0.702, 0.702], lineColorSpace='rgb',
    fillColor=[0.702, 0.702, 0.702], fillColorSpace='rgb',
    opacity=1, depth=-4.0, interpolate=True)
slf_set = visual.Rect(
    win=win, name='slf_set',
    width=(0.2, 0)[0], height=(0.25, 0.25)[1], ori=0, pos=(0, scale_y_pos), units='deg',
    lineWidth=text_h, lineColor=[-1, -1, -1], lineColorSpace='rgb',
    fillColor=[-1, -1, -1], fillColorSpace='rgb',
    opacity=1, depth=-5.0, interpolate=True)

# endregion (TASK COMPONENTS)

# region DEFINE FUNCTIONS


def sendTrigger(trigStart, trigN, EEG):
    trigTime = clock.getTime() - trigStart
    if EEG == '1':
        if trigTime < 0.05 and trigTime > 0:  # send trigger for 50 ms and do not send the trigger before next flip time
            port.setData(int(trigN, 2))
            # print(trigN)
        else:
            port.setData(0)


def draw_ssvep(win, duration, ti, secondEventStart):
    cueDuration = 0.75
    text.color = "black"
    picStartTime = clock.getTime()
    text.pos, frameN, secondCueTime = (0, -horiz/boxdenom), 0, False
    secondCuePresented, contrastNotYetChanged, eventPos = False, True, 'first'
    time = clock.getTime() - picStartTime
    while (time) < duration:
        frameN += 1
        if not event.getKeys('q'):
            if expInfo['countFrames'] == '0':
                time = clock.getTime() - picStartTime  # win.getFutureFlipTime(clock='ptb')
                images[ti-picCount].contrast = (1-A) + \
                    (A*sin(2*pi*f * time + theta))
            elif expInfo['countFrames'] == '1':
                if frameN % moduloNr == 0:  # waits until the remainder of the devision between frameN and moduloNr is 0
                    if contrastNotYetChanged:
                        images[ti-picCount].contrast, contrastNotYetChanged = 1, False
                    else:
                        images[ti-picCount].contrast, contrastNotYetChanged = 1 - \
                            (2*A), True

            # Draw frame, image, subtitle box and text on top of each other
            background.draw(), images[ti-picCount].draw()

            if clock.getTime()-(picStartTime+cueDuration) <= 0:
                subbox.draw(), text.draw()
            elif clock.getTime()-(secondCueTime+cueDuration) <= 0:
                subbox.draw(), text.draw()
            # flip and send the trigger
            win.flip()
            if not secondCuePresented:
                eventPos = 'first'
                trigger = trigdic[routinedic[gIndx]] + trigdic[condic[condData['cond'][ti]][0]] + \
                    trigdic[condData['emo'][ti]] + trigdic[condData['picset']
                                                           [ti]] + trigdic[eventPos]
                sendTrigger(picStartTime, trigger, expInfo['EEG'])
                firstCue = True
            else:
                if firstCue:
                    secondCueTime = clock.getTime()
                eventPos = 'second'
                trigger = trigdic[routinedic[gIndx]] + trigdic[condic[condData['cond'][ti]][0]] + \
                    trigdic[condData['emo'][ti]] + \
                    trigdic[condData['picset'][ti]] + trigdic[eventPos]
                sendTrigger(secondCueTime, trigger, expInfo['EEG'])
                firstCue = False

            # present 2nd cue at secondEventStart time
            if (clock.getTime() - picStartTime) > secondEventStart and not secondCuePresented:

                if condic[condData['cond'][ti]][1] == 'LOENDA':
                    shuffle(intOnScreen)
                    numTxt = ': ' + \
                        str(randint(intOnScreen[0], intOnScreen[0]+50))
                    text.setText(condic[condData['cond'][ti]][1] + numTxt)
                else:
                    text.setText(condic[condData['cond'][ti]][1])

                # change the frame colour
                background.fillColor, secondCuePresented = coldic[condData['cond'][ti]][1], True
                subbox.fillColor = coldic[condData['cond'][ti]][1]
        else:
            if expInfo['EEG'] == '1':
                port.setData(0)
                # print('port quit')
            core.quit()
        # update time
        time = clock.getTime() - picStartTime
    text.color = "white"

# fixation


def draw_fix(win, fixation, duration):
    fixStartTime = clock.getTime()
    time = clock.getTime() - fixStartTime
    while (time) < duration:
        if not event.getKeys('q'):

            fixation.draw()
            # flip and send the trigger
            win.flip()
        else:
            if expInfo['EEG'] == '1':
                port.setData(0)
                # print('port quit')
            core.quit()
        time = clock.getTime() - fixStartTime

# inter-trial-interval


def draw_iti(win, iti_dur):
    iti_time = clock.getTime()  # win.getFutureFlipTime(clock='ptb')  #
    time = clock.getTime() - iti_time
    while (time) < iti_dur:

        # flip and send the trigger
        win.flip()
        time = clock.getTime() - iti_time


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


def draw_VAS(win, question_text, label_low, label_high, item, scale_low, scale_high, slf_scale, slf_set, countingQ, sendTriggers):

    # Initialize components for Routine "VAS"
    VAS_startTime = clock.getTime()
    VAS_noResponse = True
    eventPos = 'question'
    # if button is down already this ISN'T a new click
    prevButtonState = mouse.getPressed()
    # on_scale = 0
    mouse.setPos([0, scale_y_pos])
    # mouse.setVisible(False)
    item.setText(question_text)
    scale_low.setText(label_low)
    scale_high.setText(label_high)

    if sendTriggers:
        trigger = trigdic[routinedic[gIndx]] + trigdic[condic[condData['cond'][ti]][1]] + \
            trigdic[condData['emo'][ti]] + \
            trigdic[condData['picset'][ti]] + trigdic[eventPos]
        sendTrigger(VAS_startTime, trigger, expInfo['EEG'])

    if expInfo['testMonkey'] == '1':
        VAS_noResponse = False
        VAS_resp = 'test'
        VAS_RT = 0

    while VAS_noResponse:
        if not event.getKeys('q'):

            # cursor updates
            mx = mouse.getPos()
            mx[1] = scale_y_pos

            if mx[0] <= -scale_width:
                mx[0] = -scale_width
            elif mx[0] >= scale_width:
                mx[0] = scale_width

            buttons = mouse.getPressed()
            if buttons != prevButtonState:  # button state changed?
                prevButtonState = buttons
                if sum(buttons) > 0:  # state changed to a new click
                    # check if the mouse was inside our 'clickable' objects
                    VAS_noResponse = False
                    VAS_RT = clock.getTime() - VAS_startTime
                    if countingQ:
                        VAS_resp = int(
                            round((mx[0]/scale_width)*100)+intOnScreen[0])
                    else:
                        VAS_resp = (mx[0]/scale_width)*100

            # update/draw components on each frame
            item.draw(), scale_low.draw(), scale_high.draw(), slf_scale.draw()
            # draw cursor
            slf_set.setPos(mx, log=False)
            slf_set.draw()
            # draw value
            if countingQ:
                text.pos = (mx[0], mx[1]+1)
                text.text = int(round((mx[0]/scale_width)*100)+intOnScreen[0])
                text.draw()

            win.flip()
        else:
            core.quit()

    # save the rating and RT
    thisExp.addData('vas_response', VAS_resp)
    thisExp.addData('vas_RT', VAS_RT)
    mouse.setVisible(False)
    core.wait(0.25)


def loadpics(picture_directory, pics, endindx, listname, units, picSize):
    for file in range(0, endindx):
        listname.append(visual.ImageStim(win=win, image=picture_directory + '\\' + str(
            pics[file]), units=units, size=picSize, name=str(pics[file])))

# endregion (DEFINE FUNCTIONS)


# region SET UP THE TRAINING TRIALS
trials_training = range(0, len(trainingfiles))
nTrials_training = len(trials_training)

if noData == False:
    trainingTable = pd.DataFrame(data=np.zeros(
        (nTrials_training, len(newTable.columns))), columns=newTable.columns)
    trainingTable.loc[:] = 'training'
else:
    dataCols = ['imageFile', 'valence', 'arousal', 'aff_cv', 'emo', 'semantic',
                'picset', 'cond', 'presentVAS', 'secondCueTime', 'trialID']
    trainingTable = pd.DataFrame(data=np.zeros(
        (nTrials_training, len(dataCols))), columns=dataCols)

trainingTable['imageFile'], trainingTable['trialID'], trainingTable['secondCueTime'] = trainingfiles, trials_training, secondCueTime[1]
trainingcondlist = list(range(1, 5)) * int(np.ceil(len(trainingfiles)/4))
trainingQList = list(np.ones(int(np.ceil(len(trainingfiles))))
                     )  # list(zeros(int(np.ceil(len(trainingfiles)/2)))) + \

trainingTable['presentVAS'], trainingTable['cond'] = trainingQList[0:len(
    trainingfiles)], trainingcondlist[0:len(trainingfiles)]

# emoSetInCurrent['countingQuestion'] = zeros(nTrials_training)
# emoSetInCurrent['countingQuestion'][randint(nTrials_training)] = 1

trainingTable['imageFile'] = trainingTable['imageFile'].sample(frac=1).values
trainingTable['cond'] = trainingTable['cond'].sample(frac=1).values.astype(str)
trainingTable['presentVAS'] = trainingTable['presentVAS'].sample(
    frac=1).values

if noData:
    newTable = trainingTable

# endregion (TRAINING TRIALS)

# Performe trigger test

if expInfo['triggerTest'] == '1':
    draw_text('Sündmussignaalide testimiseks vajuta palun tühikuklahvi...',
              float('inf'), 0, [])  #

    for expphase in {'training', 'experiment'}:
        # print(expphase)
        for condition in {'VAATA PILTI', 'LOENDA'}:
            # print(condition)
            for emo in {'NEG', 'NEUTRAL'}:
                # print(emo)
                for picset in {'a', 'b', 'c', 'd'}:
                    # print(picset)
                    for trphase in {'first', 'second', 'question'}:
                        # print(trphase)
                        trigger = trigdic[expphase] + trigdic[condition] + \
                            trigdic[emo] + trigdic[picset] + trigdic[trphase]
                        print(
                            ' '.join([expphase, condition, emo, picset, trphase]))
                        print(trigger)
                        trigTestTime = clock.getTime()
                        if expInfo['EEG'] == '1':
                            sendTrigger(trigTestTime, trigger, expInfo['EEG'])
                            core.wait(0.05)
                            port.setData(0)
                            # print('port quit')


# region LOAD IMAGES
draw_text('Palun oota. Laen pildid mällu...', 1, 1, [])  #

# python_pic_dir = sys.executable[0:-10] + 'Lib\site-packages\psychopy\demos\coder\stimuli'

# intro_image = PIL.Image.open(intro_dir+'\\'+introfiles[0])
# intro_width, intro_height = intro_image.size


intropics = []
loadpics(intro_dir, introfiles, len(introfiles),
         intropics, 'pix', None)  # [1024*1.2, 768*1.2]

trainingpics = []
loadpics(training_dir, trainingTable['imageFile'], len(trainingTable['imageFile']),
         trainingpics, 'deg', (picSize[0],  picSize[1]))

images_experiment = []
for file in newTable['trialID'][0:pauseAfterEvery]:
    images_experiment.append(visual.ImageStim(win=win, image=pic_dir + '\\' + str(
        newTable['imageFile'][file]), units='deg', size=picSize, name=str(newTable['imageFile'][file])))  # + '.jpg'

# endregion (LOAD IMAGES)

# region PRESENT INSTRUCTIONS

if expInfo['showIntro'] == '1':
    text.color = 'black'
    presentIntroPics, countIntroPics = True, 0
    while presentIntroPics == True:
        # for indx in range(0, len(intropics)):
        core.wait(0.25)
        presentPic = True
        picStart = clock.getTime()
        shuffle(intOnScreen)
        numTxt = ': ' + str(randint(intOnScreen[0], intOnScreen[0]+50))

        while presentPic:
            intropics[countIntroPics].draw()
            # (countIntroPics == 5 or countIntroPics == 8 or countIntroPics == 11)
            if (countIntroPics == 4 or countIntroPics == 6 or countIntroPics == 8) and clock.getTime()-picStart <= 0.75:
                text.setText('VAATA PILTI')
                subbox.fillColor = coldic['1'][1]
                subbox.draw(), text.draw()
                #(countIntroPics == 19 or countIntroPics == 22 or countIntroPics == 25)
            elif (countIntroPics == 15 or countIntroPics == 17 or countIntroPics == 19) and clock.getTime()-picStart <= 0.75:
                text.setText('LOENDA'+numTxt)
                subbox.fillColor = coldic['3'][1]
                subbox.draw(), text.draw()
            win.flip()

            buttons, theseKeys = mouse.getPressed(
            ), event.getKeys(keyList=['q', 'space'])
            if len(theseKeys) > 0 and theseKeys[0] == 'q':
                if expInfo['EEG'] == '1':
                    port.setData(0)
                    # print('port quit')
                core.quit()
            elif len(buttons) > 0:
                if buttons[0] == 1:
                    countIntroPics += 1
                    presentPic = False
                elif buttons[2] == 1:
                    if countIntroPics > 0:
                        countIntroPics -= 1
                    presentPic = False

        if countIntroPics == len(intropics):
            presentIntroPics = False
            core.wait(0.25)
# endregion (PRESENT INSTRUCTIONS)

# region THIS IS THE EXPERIMENT LOOP
text.color = 'white'
routinedic = {'0': 'training', '1': 'experiment'}

for gIndx in routinedic:
    runExperiment = True
    if routinedic[gIndx] == 'training':
        condData, trials, nTrials, images, current_pic_dir = \
            trainingTable, trainingTable['trialID'], len(
                trials_training), trainingpics, training_dir
        TextDic = practiceTextDic
    elif routinedic[gIndx] == 'experiment':
        condData, trials, nTrials, images, current_pic_dir, TextDic = \
            newTable, newTable['trialID'], len(
                newTable['trialID']), images_experiment, pic_dir, expTextDic

    text.pos = (0, 0)
    for text2present in TextDic:
        if routinedic[gIndx] == 'experiment' and int(text2present) == len(TextDic):
            mouse_resp = 0
            cText = ' '
        else:
            mouse_resp = 1
            cText = clickMouseText
        if routinedic[gIndx] == 'training' and int(text2present) == len(TextDic):
            draw_VAS(win, self_VAS, self_VAS_min, self_VAS_max, item,
                     scale_low, scale_high, slf_scale, slf_set, 0, 0)
        draw_text(TextDic[text2present], float('inf'), mouse_resp, cText)  #
        core.wait(0.25)

    picCount, ti, apCounterNeg, apCounterNtr = 0, 0, 0, 0
    while runExperiment:
        expInfo['globalTime'] = clock.getTime()  # save data
        mouse.setVisible(False)  # hide the cursor
        if ti == nTrials and routinedic[gIndx] == 'experiment':
            # close and quit
            if expInfo['reExposure'] == '0':
                draw_text(goodbye_text, float('inf'), 1, [])
                if expInfo['EEG'] == '1':
                    port.setData(0), port.close()
                    # print('port quit')
                win.close(), core.quit()
            else:
                break
        elif ti == nTrials:
            break

        # Draw FIXATION
        draw_fix(win, fixation, fixDuration)

        # Draw flickering PICTURE

        if condic[condData['cond'][ti]][0] == 'LOENDA':
            shuffle(intOnScreen)
            numTxt = ': ' + str(randint(intOnScreen[0], intOnScreen[0]+50))
            text.setText(condic[condData['cond'][ti]][0] + numTxt)
        else:
            text.setText(condic[condData['cond'][ti]][0])

        subbox.fillColor = coldic[condData['cond'][ti]][0]
        background.fillColor = coldic[condData['cond'][ti]][0]
        secondCueStart = condData['secondCueTime'][ti]
        # draw the flickering picture
        draw_ssvep(win, stimDuration, ti, secondCueStart)
        text.pos = (0, 0)  # change text position back

        # Define picture name for saving
        picName = images[ti-picCount].name

        # SAVE SOME DATA
        thisExp.addData('trialType', routinedic[gIndx]), thisExp.addData(
            'secondCueTime', condData['secondCueTime'][ti])
        thisExp.addData('picset', condData['picset'][ti]), thisExp.addData(
            'cond', condic[condData['cond'][ti]])
        thisExp.addData('Question', condData['presentVAS'][ti]), thisExp.addData(
            'valence', condData['emo'][ti])
        thisExp.addData('pictureID', picName), thisExp.addData(
            'fixDuration', fixDuration)
        thisExp.addData('triaslN', ti+1), thisExp.addData('picBytes',
                                                          os.stat(current_pic_dir + '\\' + picName).st_size)

        if condData['presentVAS'][ti] == 1:
            draw_VAS(win, self_VAS, self_VAS_min,
                     self_VAS_max, item, scale_low, scale_high, slf_scale, slf_set, 0, 1)

        # ITI
        if expInfo['testMonkey'] == '0':
            iti_dur = random() + iti_dur_default
        else:
            iti_dur = iti_dur_default

        draw_iti(win, iti_dur)

        # PAUSE (preloading next set of N (pauseAfterEvery) images to achive better timing)
        pauseStart = clock.getTime()  # win.getFutureFlipTime(clock='ptb')
        try:
            if (ti+1) % pauseAfterEvery == 0:
                # text.pos = (0, 0)  # change text position back
                if ti < nTrials:
                    if expInfo['testMonkey'] == '0':
                        draw_text(pause_text, float('inf'), 0, [])
                        draw_text(clickMouseText, float('inf'), 1, [])
                    else:
                        draw_text(pause_text, 0.2, 0, [])

                picCount += pauseAfterEvery
                images = []
                start = ti+1
                end = start+pauseAfterEvery

                if end > nTrials:
                    end = nTrials
                # PRELOAD PICTURES FOR EACH BLOCK
                for file in condData['trialID'][start:end]:
                    images.append(visual.ImageStim(win=win, image=current_pic_dir + '\\' + str(
                        condData['imageFile'][file]), units='deg', size=picSize, name=str(condData['imageFile'][file])))  # + '.jpg'
        except:
            print(
                'Variable "pauseAfterEvery" empty or smaller than 1 - pause will be skipped')
        thisExp.nextEntry()
        ti += 1
# endregion (EXPERIMENT LOOP)

# region RE-EXPOSURE
if expInfo['reExposure'] == '1':
    draw_text('Re-exposure intro (jätkamiseks vajuta tühukut)',
              float('inf'), mouse_resp, [])  #

    reexpopics = []
    newTable = newTable.sample(frac=1).reset_index(drop=True)
    loadpics(pic_dir, newTable['imageFile'], len(newTable['imageFile']),
             reexpopics, 'deg', (picSize[0], picSize[1]))

    for indx in range(0, len(reexpopics)):

        # draw fixation
        draw_fix(win, fixation, 0.5, 0)
        reexpopics[indx].draw(), win.flip()

        # SAVE SOME DATA
        thisExp.addData('trialType', 're-exposure'), thisExp.addData(
            'secondCueTime', newTable['secondCueTime'][indx])
        thisExp.addData('picset', newTable['picset'][indx]), thisExp.addData(
            'cond', condic[newTable['cond'][indx]])
        thisExp.addData('Question', newTable['presentVAS'][indx]), thisExp.addData(
            'valence', newTable['emo'][indx])
        thisExp.addData('pictureID', picName), thisExp.addData(
            'fixDuration', fixDuration)
        thisExp.addData('triaslN', indx+1), thisExp.addData('picBytes',
                                                            os.stat(current_pic_dir + '\\' + picName).st_size)

        pause_time, pause_dur = clock.getTime(), 3.5
        while (clock.getTime() - pause_time) < pause_dur:
            reexpopics[indx].draw(), win.flip()

            buttons, theseKeys = mouse.getPressed(
            ), event.getKeys(keyList=['q', 'space'])

            if len(theseKeys) > 0 and theseKeys[0] == 'q':
                if expInfo['EEG'] == '1':
                    port.setData(0)
                    # print('port quit')
                core.quit()

        # draw iti
        iti_dur = random() + iti_dur_default
        draw_iti(win, iti_dur, 0)

        thisExp.nextEntry()

    if indx == len(reexpopics)-1:
        draw_text(goodbye_text, float('inf'), 1, [])
        if expInfo['EEG'] == '1':
            port.setData(0)
            # print('port quit')
            core.quit()
    # draw VAS
    # VAS_text.text = 'Siia tuleb küsimus...'
    # draw_VAS(win, VAS, VAS_text, 'Question_1')

# endregion (RE-EXPOSURE)

# region CLOSE AND QUIT
# these shouldn't be strictly necessary (should auto-save)
# thisExp.saveAsWideText(filename+'.csv')
# thisExp.saveAsPickle(filename)

# close and quit
