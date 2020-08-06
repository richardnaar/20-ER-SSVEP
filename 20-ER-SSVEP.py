#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSVEP task 05/08/2020
monitor setting (e.g. testMonitor to smtn else)
set up the folders (ssvep_iaps, training_pics, intro_pics)
viewing angle: 34x28 (Hajcak jt 2013) 
"""

# region IMPORT MODULES

# future should make it possible to run the same code under Python 2
# from __future__ import absolute_import, division
import psychopy
from psychopy import locale_setup, gui, visual, core, data, event, logging, sound, monitors

import os  # system and path functions
import pandas as pd  # data structures
import serial
import platform

from numpy import pi, sin, random, zeros
from numpy.random import random, randint, shuffle

import numpy as np


# endregion (IMPORT MODULES)

# region SET UP THE INFO DIALOG AND EXPERIMENT HANDLER
# get the current directory
dirpath = os.getcwd()

# Information about the experimental session
psychopyVersion = psychopy.__version__
print('PsychoPy version: ' + psychopy.__version__)

# filename of the script
expName = os.path.basename(__file__)  # + data.getDateStr()

expInfo = {'participant': 'rn', 'session': '001', 'EEG': '0', 'Chemicum': '0',
           'stimFrequency': '15', 'frame': '0', 'testMonkey': '1', 'pauseAfterEvery': '32', 'countFrames': '1', 'reExposure': '1'}

dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
if dlg.OK == False:
    core.quit()  # user pressed cancel

expInfo['date'] = data.getDateStr()  # add a simple timestamp
expInfo['expName'] = expName

# Set durartions
if expInfo['testMonkey'] == '1':
    fixDuration = 0.1  # fixation duration (will change on every iteration)
    stimDuration = 1  # 0.126  # stim duration
    iti_dur_default = 0.2
    # soundStart = 0.65
    secondCueTime = [0.1, 0.2, 0.3]
    expInfo['participant'] = 'Monkey'
else:
    # just the first iti, later will change on every trial (random()+0.5)
    fixDuration = 1.5  #
    stimDuration = 12.6  # stim duration
    iti_dur_default = 3.5  # +/- 0.5
    # soundStart = 6.5
    secondCueTime = [6, 6.5, 7]

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

# region SIMULUS TIMING AND SET UP THE EEG PORT

expInfo['stimDuration'] = stimDuration  # save data
expInfo['itiDuration'] = str(iti_dur_default) + '+/- 0.5'  # save data

if expInfo['EEG'] == '1':
    from psychopy import parallel
    if expInfo['Chemicum'] == '1':
        port = parallel.ParallelPort(address=0x378)
    else:
        port = parallel.ParallelPort(address=0xe010)
        port.setData(0)
    trigNum = 0
# endregion (SIMULUS TIMING AND SET UP THE EEG PORT)

# region FIND FILES
# Find stimuli and create a list of all_files

print("current directory is : " + dirpath)

# pictures (pptx slides convered to pictures) used in the introduction
intro_dir = dirpath + '\\intro_pics'
introfiles = list(filter(lambda x: x.endswith('.JPG'), os.listdir(intro_dir)))
# pictures used in the training loop
training_dir = dirpath + '\\training_pics'
trainingfiles = list(
    filter(lambda x: x.endswith('.jpg'), os.listdir(training_dir)))
# pictures used in the experiment
pic_dir = dirpath + '\\ssvep_iaps'
all_files = list(filter(lambda x: x.endswith('.jpg'), os.listdir(pic_dir)))
picFolder = ['ssvep_iaps']

# Import the condion file
xls_file = pd.ExcelFile('ERSSVEP_images.xlsx')
table = xls_file.parse('ERSSVEP_images')

# endregion (FIND FILES)

# region RANDOMIZATION
# sort by emo and picset
table = table.sort_values(['emo', 'picset']).reset_index(drop=True)
# define newTable as data frame in pandas
newTable = pd.DataFrame()
picsets = np.unique(table['picset'])
# randomize picsets
shuffle(picsets)
trueSetSize = int(len(table)/len(picsets))
counter = 0  # keeps track of the number sets iterated
tilist = list()
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
        emoSetInCurrent['presentQuestion'] = np.squeeze(
            np.asarray(rndQM)).reshape(-1).astype(int)

        # randomize condition and question presentation
        emoSetInCurrent[['cond', 'presentQuestion']] = emoSetInCurrent[[
            'cond', 'presentQuestion']].sample(frac=1).reset_index(drop=True)

        # define 2nd cue times similarly for each emotion category in each set separately
        secondCueRndList = secondCueTime * \
            int(np.ceil(setSize/len(secondCueTime)))
        secondCueRndList = secondCueRndList[0:setSize]
        shuffle(secondCueRndList)
        emoSetInCurrent['secondCueTime'] = secondCueRndList

        # this randomization is not strictly nessesary since 'tilist' (see below) shuffles the trials within each set already
        emoSetInCurrent = emoSetInCurrent.sample(frac=1).reset_index(drop=True)
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
else:
    monSettings = {'size': (1920, 1080), 'fullscr': True}

win = visual.Window(
    size=monSettings['size'], fullscr=monSettings['fullscr'], screen=0, color='black',
    blendMode='avg', useFBO=True, monitor='testMonitor',
    units='deg')

# Hide mouse

mouse = event.Mouse(win=win)
mouse.setVisible(False)

expInfo['frameRate'] = win.getActualFrameRate()
print(expInfo['frameRate'])
if expInfo['frameRate'] != None:
    frameDur = round(expInfo['frameRate'])  # save data
else:
    frameDur = 'NaN'  # could not measure, so NaN
print('the monitor refresh rate is: ' + str(frameDur))

# Initiate clock to keep track of time
clock = core.Clock()

# use frameRate to add data and to define moduloNr

pauseAfterEvery = int(expInfo['pauseAfterEvery'])  # save data
if expInfo['frame'] == 0:
    # define parameters used to draw the flickering stimuli
    theta = pi/2  # constant phase offset
    f = float(expInfo['stimFrequency'])  # in Hz # save data
    # save these parameters to the file
    expInfo['phaseOffset'] = theta  # save data
    # 0.3 # can't be larger than 0.5 (min = 0.5-0.5 and max = 0.5+0.5)
    A = 0.20
    expInfo['flickeringAmplitude'] = A  # save data
else:
    # 0.3 # can't be larger than 0.5 (min = 0.5-0.5 and max = 0.5+0.5)
    moduloNr = int(
        np.ceil(round(float(expInfo['frameRate'])) / float(expInfo['stimFrequency'])))
    A = 0.20
    expInfo['contrastChange'] = A*2  # save data
    expInfo['actualFrequency'] = np.ceil(
        round(float(expInfo['frameRate'])))/((moduloNr-1)*2)

# endregion (SETUP WINDOW)

# region INITIALIZE TASK COMPONENTS

horiz = 34
vert = 28
picSize = (horiz, vert)

pause_text = 'See on paus. Jätkamiseks vajuta palun hiireklahvi . . .'
start_text = 'Palun oota kuni eksperimentaator käivitab mõõtmise . . . \n\n Programmi sulgemiseks vajuta: "q"'
goodbye_text = 'Aitäh! Katse on läbi! Kutsu katse läbiviija. \n\nPärast mõõtevahendite eemaldamist palume Sul vastata teises ruumis lühikesele küsimustikule \
\n\nProgrammi sulgemiseks vajuta palun hiireklahvi . . . '

text = visual.TextStim(win=win,
                       text='insert txt here',
                       font='Arial',
                       pos=(0, 0), height=1, wrapWidth=30, ori=0,
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
    width=(8, 8)[0], height=(2, 2)[1],
    ori=0, pos=(0, -horiz/2.8),
    lineWidth=0, lineColor=[1, 1, 1], lineColorSpace='rgb',
    fillColor=[-1, -1, -1], fillColorSpace='rgb',
    opacity=1, depth=0.0, interpolate=True)

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

# endregion (TASK COMPONENTS)

# region DEFINE FUNCTIONS


def sendTrigger(trigStart, trigN, EEG):
    trigTime = clock.getTime() - trigStart
    if EEG == '1':
        if trigTime < 0.025 and trigTime > 0:  # send trigger for 25 ms and do not send the trigger before next flip time
            port.setData(trigN)
        else:
            port.setData(0)


def draw_ssvep(win, duration, ti, trigNum):
    text.pos = (0, -horiz/2.8)
    picStartTime = clock.getTime()
    frameN = 0
    secondCuePresented = False
    contrastNotYetChanged = True
    time = clock.getTime() - picStartTime
    while (time) < duration:
        frameN += 1
        if not event.getKeys('q'):
            if expInfo['frame'] == '0' and expInfo['countFrames'] == '0':
                time = clock.getTime() - picStartTime  # win.getFutureFlipTime(clock='ptb')
                images[ti-picCount].contrast = (1-A) + \
                    (A*sin(2*pi*f * time + theta))
            elif expInfo['countFrames'] == '1':
                if frameN % moduloNr == 0:  # waits until the remainder of the devision between frameN and moduloNr is 0
                    images[ti-picCount].contrast = 1
                    contrastNotYetChanged = True
                elif contrastNotYetChanged:
                    images[ti-picCount].contrast = 1-(2*A)
                    contrastNotYetChanged = False

            # Draw frame, image, subtitle box and text on top of each other
            background.draw()
            images[ti-picCount].draw()
            subbox.draw()
            text.draw()

            # flip and send the trigger

            win.flip()
            if not secondCuePresented:
                sendTrigger(picStartTime, trigNum, expInfo['EEG'])

            # play sound half way through
            if (clock.getTime() - picStartTime) > secondCueStart and not secondCuePresented:
                trigNum += 10
                # print('secondCue_'+ str(trigNum))
                cueTime = win.getFutureFlipTime(
                    clock='ptb')
                # send the trigger and present the random integer
                sendTrigger(cueTime, trigNum, expInfo['EEG'])
                if condic[condData['cond'][ti]][1] == 'LOENDA':
                    shuffle(intOnScreen)
                    numTxt = ': ' + \
                        str(randint(intOnScreen[0], intOnScreen[0]+50))
                    text.setText(condic[condData['cond'][ti]][1] + numTxt)
                else:
                    text.setText(condic[condData['cond'][ti]][1])

                # change the frame colour
                background.fillColor = coldic[condData['cond'][ti]][1]
                secondCuePresented = True
            elif secondCuePresented:
                sendTrigger(cueTime, trigNum, expInfo['EEG'])
        else:
            if expInfo['EEG'] == '1':
                port.setData(0)
            core.quit()
        # update time
        time = clock.getTime() - picStartTime


# fixation
def draw_fix(win, fixation, duration, trigNum):
    # print('fix_'+ str(trigNum))
    fixStartTime = clock.getTime()
    time = clock.getTime() - fixStartTime
    while (time) < duration:
        if not event.getKeys('q'):

            fixation.draw()
            # flip and send the trigger
            win.flip()
            sendTrigger(fixStartTime, trigNum, expInfo['EEG'])
        else:
            if expInfo['EEG'] == '1':
                port.setData(0)
            core.quit()
        time = clock.getTime() - fixStartTime

# inter-trial-interval


def draw_iti(win, iti_dur, trigNum):
    # print('iti_'+str(trigNum))
    iti_time = clock.getTime()  # win.getFutureFlipTime(clock='ptb')  #
    time = clock.getTime() - iti_time
    while (time) < iti_dur:
        if expInfo['frame'] == '1':
            time = clock.getTime() - iti_time  # win.getFutureFlipTime(clock='ptb')

        # flip and send the trigger
        win.flip()
        sendTrigger(iti_time, trigNum, expInfo['EEG'])
        time = clock.getTime() - iti_time


def draw_text(txt, pause_dur, mouse_resp):
    pause_time = clock.getTime()
    while (clock.getTime() - pause_time) < pause_dur:
        buttons = mouse.getPressed()
        theseKeys = event.getKeys(keyList=['q', 'space'])
        if len(theseKeys) == 0 and sum(buttons) == 0:
            text.setText(txt)
            text.draw()
            win.flip()
        elif len(theseKeys) > 0 and theseKeys[0] == 'space' and mouse_resp == 0:
            break
        elif len(theseKeys) > 0 and theseKeys[0] == 'q':
            if expInfo['EEG'] == '1':
                port.setData(0)
            core.quit()
        elif sum(buttons) > 0 and mouse_resp == 1:
            break


def draw_VAS(win, VAS, VAS_text, colName):
    # Initialize components for Routine "VAS"
    VAS.reset()
    VASstartTime = clock.getTime()
    mouse.setVisible(True)

    if expInfo['testMonkey'] == '1':
        VAS.noResponse = False

    while VAS.noResponse:
        if not event.getKeys('q'):
            VAS_text.draw()
            VAS.draw()
            win.flip()
        else:
            core.quit()
    mouse.setVisible(False)
    # write average srate to the file
    thisExp.addData(colName, VAS.getRating())
    thisExp.addData(colName+'_RT', VAS.getRT())
    core.wait(0.25)


def loadpics(picture_directory, pics, endindx, listname, picSize):
    for file in range(0, endindx):
        listname.append(visual.ImageStim(win=win, image=picture_directory + '\\' + str(
            pics[file]), units='deg', size=picSize, name=str(pics[file])))

# endregion (DEFINE FUNCTIONS)


# region SET UP THE TRAINING TRIALS
trials_training = range(0, len(trainingfiles))
nTrials_training = len(trials_training)

trainingTable = pd.DataFrame(data=np.zeros(
    (nTrials_training, len(newTable.columns))), columns=newTable.columns)
trainingTable.loc[:] = 'training'

trainingTable['imageFile'] = trainingfiles
trainingcondlist = list(range(1, 5)) * int(np.ceil(len(trainingfiles)/4))
trainingTable['cond'] = trainingcondlist[0:len(trainingfiles)]
trainingTable['trialID'] = trials_training
trainingQList = list(zeros(int(np.ceil(len(trainingfiles)/2)))) + \
    list(np.ones(int(np.ceil(len(trainingfiles)/2))))
trainingTable['presentQuestion'] = trainingQList[0:len(trainingfiles)]
trainingTable['secondCueTime'] = secondCueTime[1]

trainingTable['imageFile'] = trainingTable['imageFile'].sample(frac=1).values
trainingTable['cond'] = trainingTable['cond'].sample(frac=1).values.astype(str)
trainingTable['presentQuestion'] = trainingTable['presentQuestion'].sample(
    frac=1).values
# endregion (TRAINING TRIALS)

# region LOAD IMAGES
draw_text('Palun oota. Laen pildid mällu...', 1, 1)  #

intropics = []
loadpics(intro_dir, introfiles, len(introfiles),
         intropics, (picSize[0], picSize[1]))

trainingpics = []
loadpics(training_dir, trainingTable['imageFile'], len(trainingTable['imageFile']),
         trainingpics, (picSize[0], picSize[1]))

images_experiment = []
for file in newTable['trialID'][0:pauseAfterEvery]:
    images_experiment.append(visual.ImageStim(win=win, image=pic_dir + '\\' + str(
        newTable['imageFile'][file]), units='deg', size=picSize, name=str(newTable['imageFile'][file])))  # + '.jpg'

# endregion (LOAD IMAGES)

# region PRESENT INSTRUCTIONS

# only if actually testing
if expInfo['testMonkey'] == '0':
    for indx in range(0, len(intropics)):
        core.wait(0.25)
        presentPic = True

        while presentPic:
            intropics[indx].draw()
            win.flip()

            buttons = mouse.getPressed()
            theseKeys = event.getKeys(keyList=['q', 'space'])

            if len(theseKeys) > 0 and theseKeys[0] == 'q':
                if expInfo['EEG'] == '1':
                    port.setData(0)
                core.quit()
            elif sum(buttons) > 0:
                presentPic = False
# endregion (PRESENT INSTRUCTIONS)

# region THIS IS THE EXPERIMENT LOOP

routinedic = {'0': 'training', '1': 'experiment'}

for gIndx in routinedic:
    runExperiment = True
    if routinedic[gIndx] == 'training':
        condData = trainingTable
        trials = trainingTable['trialID']
        nTrials = len(trials_training)
        images = trainingpics
        current_pic_dir = training_dir
        instructions = 'Järgmised esitused on harjutamiseks...'
        mouse_resp = 1
    elif routinedic[gIndx] == 'experiment':
        condData = newTable
        trials = newTable['trialID']  # list(range(0, len(picSeries)))
        nTrials = len(trials)
        images = images_experiment
        current_pic_dir = pic_dir
        instructions = start_text
        mouse_resp = 0

    draw_text(instructions, float('inf'), mouse_resp)  #

    picCount = 0
    ti = 0
    apCounterNeg = 0
    apCounterNtr = 0
    while runExperiment:
        expInfo['globalTime'] = clock.getTime()  # save data
        mouse.setVisible(False)  # hide the cursor
        if ti == nTrials and routinedic[gIndx] == 'experiment':
            # close and quit
            draw_text(goodbye_text, float('inf'), 1)
            if expInfo['EEG'] == '1':
                port.setData(0)
                port.close()
            win.close()
            core.quit()
        elif ti == nTrials:
            break

        # NB! Triggering is deprecated, but I keep them for now since they may come in handy later on...
        trigNum = 1
        # Draw FIXATION
        trigNum += 10
        draw_fix(win, fixation, fixDuration, trigNum)

        # Draw flickering PICTURE

        trigNum += 10
        if condic[condData['cond'][ti]][0] == 'LOENDA':
            shuffle(intOnScreen)
            numTxt = ': ' + str(randint(intOnScreen[0], intOnScreen[0]+50))
            text.setText(condic[condData['cond'][ti]][0] + numTxt)
        else:
            text.setText(condic[condData['cond'][ti]][0])

        background.fillColor = coldic[condData['cond'][ti]][0]
        secondCueStart = condData['secondCueTime'][ti]
        draw_ssvep(win, stimDuration, ti, trigNum)
        text.pos = (0, 0)

        # Define picture name for saving
        picName = images[ti-picCount].name

        # SAVE SOME DATA
        thisExp.addData('trialType', routinedic[gIndx])
        thisExp.addData('2ndCueTime', condData['secondCueTime'][ti])
        thisExp.addData('picset', condData['picset'][ti])
        thisExp.addData('cond', condic[condData['cond'][ti]])
        thisExp.addData('Question', condData['presentQuestion'][ti])
        thisExp.addData('valence', condData['emo'][ti])
        thisExp.addData('pictureID', picName)
        thisExp.addData('fixDuration', fixDuration)
        thisExp.addData('triaslN', ti+1)
        thisExp.addData('picBytes', os.stat(
            current_pic_dir + '\\' + picName).st_size)

        # ITI
        if expInfo['testMonkey'] == '0':
            iti_dur = random() + iti_dur_default
        else:
            iti_dur = iti_dur_default

        trigNum += 20
        draw_iti(win, iti_dur, trigNum)

        # Draw QUESTION
        if condData['presentQuestion'][ti] == 1:
            VAS_text.text = 'Siia tuleb küsimus...'
            draw_VAS(win, VAS, VAS_text, 'Question_1')

        # PAUSE (preloading next set of N (pauseAfterEvery) images to achive better timing)
        pauseStart = clock.getTime()  # win.getFutureFlipTime(clock='ptb')
        if (ti+1) % pauseAfterEvery == 0:
            trigNum += 10
            # print('pause_'+str(trigNum))

            sendTrigger(pauseStart, trigNum, expInfo['EEG'])
            if expInfo['testMonkey'] == '0':
                draw_text(pause_text, float('inf'), 1)
            else:
                draw_text(pause_text, 0.2, 1)

            picCount += pauseAfterEvery
            images = []
            start = ti+1
            end = start+pauseAfterEvery

            if end > nTrials:
                end = nTrials
            # PRELOAD PICTURES FOR EACH BLOCK
            for file in trials[start:end]:
                images.append(visual.ImageStim(win=win, image=pic_dir + '\\' + str(
                    picSeries[file]), units='deg', size=picSize, name=str(picSeries[file])))  # + '.jpg'

        thisExp.nextEntry()
        ti += 1

# endregion (EXPERIMENT LOOP)

# region RE-EXPOSURE
if expInfo['reExposure'] == '1':
    reexpopics = []
    loadpics(pic_dir, all_files, len(all_files),
             reexpopics, (picSize[0], picSize[1]))

    for indx in range(0, len(reexpopics)):

        # draw fixation
        draw_fix(win, fixation, 0.5, 0)

        reexpopics[indx].draw()
        win.flip()

        pause_time = clock.getTime()
        pause_dur = 0.5
        while (clock.getTime() - pause_time) < pause_dur:
            reexpopics[indx].draw()
            win.flip()

            buttons = mouse.getPressed()
            theseKeys = event.getKeys(keyList=['q', 'space'])

            if len(theseKeys) > 0 and theseKeys[0] == 'q':
                if expInfo['EEG'] == '1':
                    port.setData(0)
                core.quit()

        # draw iti
        iti_dur = random() + iti_dur_default
        draw_iti(win, iti_dur, 0)

        # draw VAS
        # VAS_text.text = 'Siia tuleb küsimus...'
        # draw_VAS(win, VAS, VAS_text, 'Question_1')

# endregion (RE-EXPOSURE)

# region CLOSE AND QUIT
# these shouldn't be strictly necessary (should auto-save)
# thisExp.saveAsWideText(filename+'.csv')
# thisExp.saveAsPickle(filename)

# close and quit
