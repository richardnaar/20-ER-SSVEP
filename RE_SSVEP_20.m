%% 20-RE-SSVEP
clear; close all

%%
datDir = 'C:\Users\Richard Naar\Documents\dok\ssvep\Proof of concept\artiklid ja raamatud (Liisa)\20-RE-SSVEP\'; % data (light sensor) dir
eeglabDir = ' C:\Program Files\MATLAB\R2014a\toolbox\eeglab13_6_5b\';                                               % eeglab program directory
locfile =   ' C:\Program Files\MATLAB\R2014a\toolbox\eeglab13_6_5b\32_4EOG.ced';                                    % dir of the electrode location file 

%% IMPORT LIGHT SENSOR DATA

% impdir = [datDir, 'Light\'];                                                % import directory
impdir = [datDir, 'Pilot\'];                                                % import directory
cleandir = [datDir, 'Clean\'];

implist = dir([impdir, '*.bdf']);                                           % make a fresh list of the contents of the raw files directory (input of this loop)

%% Import and find events

subi = 1;

ALLEEG = []; EEG = []; CURRENTSET = [];                                     % erase anything in the eeglab. 
        
dat = openbdf([impdir, implist(subi).name]);                                % avab faili, et lugeda kanalite arvu
event = strmatch('Status', {dat.Head.Label},'exact');                       % leiab event kanali asukoha
erg1 = strmatch('Erg1', {dat.Head.Label}, 'exact');                         % leiab Erg1 kanali asukoha
exg1 = strmatch('EXG1', {dat.Head.Label}, 'exact');
clear dat;                                                                  % kuna see fail võib ruumi võtta, kustutame ära

% EEG = pop_biosig([impdir, implist(subi).name]); 

EEG = pop_biosig([impdir, implist(subi).name], 'ref',exg1+4:exg1+5);        % reference at EXG5 and EXG6
% EEG = pop_biosig([impdir, implist(subi).name]); 
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, CURRENTSET, 'setname', implist(subi).name(1:end-4));% imporditud andmestiku salvestamine



EEG.data = EEG.data([1:64 exg1:exg1+3],:); EEG.nbchan = 68;                 % mittevajalike kanalite eemaldamine (32 peakanalit, 4 silma, täiendav EMG kanal, GSR 1 ja 2, Pletüsmograf)
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 

EEG = pop_chanedit(EEG, 'load',{[datDir 'BioSemi64_4.loc'] 'filetype' 'autodetect'});     % Edit the channel locations structure of an EEGLAB dataset, EEG.chanlocs. 
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 



% FIND EVENTS
trig.tSeq = {'1' 'fix'; '2' 'pic'; '3' 'sound'; '4' 'iti'; '5' 'pause'};
trig.cond = {'1' 'neg'; '2' 'pos'; '3' 'distr'; '6' 'non-distr'};

for eventi = 1:length(EEG.event)
    
    eString = num2str(EEG.event(eventi).type);
    conNum = str2num(eString(2));
    
    seq = trig.tSeq(strcmp(trig.tSeq, eString(1)),2); % first string keeps track of the trial sequence
    EEG.event(eventi).type = seq{:};
    
    if conNum < 6 % if it's smaller than 6 it must be distraction condition
        cond = 'distr';
        val = trig.cond(strcmp(trig.cond, num2str(conNum-3)), 2);
    else % otherwise it's the non-distraction condition
        cond = 'non-distr';
        val = trig.cond(strcmp(trig.cond, num2str(conNum-6)), 2);
    end
    
    EEG.event(eventi).valence = val{:};
    EEG.event(eventi).distrCond = cond;
    
%     EEG.event(eventi).type = [seq{:},'_',cond,'_',val{:}];
end

eegplot(EEG1.data, 'events', EEG.event) % see the raw file
%% ICA
% 
% ALLEEG = []; EEG = []; CURRENTSET = 1; % we clean the structure
% EEG = pop_loadset('filename', inlist(s).name, 'filepath', indir);         % we load the eeg lab .set file
% [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);             % save the change to eeglab (i guess). 

% Kui vajalik see on?
% [ALLEEG EEG1 CURRENTSET] = pop_copyset(ALLEEG, 1, 2);                        % this line makes a copy of the dataset for the high pass.                                                      % copy a separaate dataset for ICA training
% [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 
        
EEG = pop_eegfiltnew(EEG, [], 1, 6760, 1, [], 0);                           % half-amplitude at 0.75 Hz, transition band edge at 1 Hz                                                   % filter the training data at 1 Hz highpass
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 

EEG = pop_epoch(EEG, {'pic'}, [-0.5 13], 'epochinfo', 'yes');                 % we're defining the segments which will be used for the ICA                                           % extract training epochs 
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 

% EEG = pop_eegthresh(EEG,1,[1:EEG.nbchan-4] ,-1500, 1500, -1, 2,0,0);          % reject extreme values
% [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);               % whenever we see a lot of power for specific point.

[EEG ALLEEG(1).rejhist.preICA] = pop_rejspec(EEG, 1, [1:EEG.nbchan], -35, 35, 15, 30, 0, 1);   % cleaning the data of muscle noise        % remove segments with high muscle noise (15-30 Hz)
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);               % whenever we see a lot of power for specific point.

EEG1 = pop_runica(EEG, 'extended', 1, 'interupt', 'on');                     % actually running the ICA                                                % find an ICA solution
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 
        
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, CURRENTSET, 'retrieve', 1);   % write the solution of the ICA on the data.                            % write the ICA solution back to original data
EEG = pop_editset(EEG, 'icachansind', 'ALLEEG(2).icachansind', 'icaweights', 'ALLEEG(2).icaweights', 'icasphere', 'ALLEEG(2).icasphere'); 
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);     

EEG = pop_saveset(EEG, 'filename', EEG.filename, 'filepath', icadir, 'savemode', 'twofiles');










% EEG.event = EEG.event(1:length(EEG.urevent));                               % kui salvestus on varem katkestatud, siis tekib ilma selleta viga
%         [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);       % save changes to EEGLAB structure within Matlab
%         EEG = pop_saveset(EEG, 'filename', EEG.subject, 'filepath', indir, 'savemode', 'twofiles'); % save changes to the import directory on disk


%%
% %% find events
% events = {'pic'};
% 
% currentIndx = 1;
% for eventi = 1:length(EEG.event)
%     if strfind(EEG.event(eventi).type, events{1})
%         eventOffset(currentIndx) = EEG.event(eventi+2).latency; % find event offset
%         eventOnset(currentIndx) = EEG.event(eventi).latency; % find previous event oncet (start of the epoch)
%         currentIndx = currentIndx + 1;
%     end
% end
% 
% fprintf('Found %d events. \n', currentIndx-1)
% 
% %% select channels
% 
% load([datDir, 'BioSemi64.mat'])
% % save([datDir 'BioSemi64.mat'], 'BioSemi64', '-v7.3');
% % fields = {'labels', 'ref', 'theta', 'radius', 'X', 'Y', 'Z', 'sph_theta', 'sph_phi', 'sph_radius', 'type', 'urchan'};
% % BioSemi64 = cell2struct(BioSemi64, fields, 2);    
% 
% EEG.chanlocs = struct(BioSemi64);
% 
% electrodes = {'O1', 'Oz', 'O2', 'POz', 'P1', 'P2', 'PO3', 'PO4'};
% elec2plot = find(ismember({EEG.chanlocs.labels}, electrodes)); % find electrode indexes
% 
% %%
% 
% if size(elec2plot,2) > 1
%     allSamples=squeeze(mean(allSamples(1:end-1, :))); % mean of channels
% end
%     
% % We can now bin into 1 second intervals
% rebinnedData=reshape(allSamples, EEG.srate,trialDur/EEG.srate);
% fftRebinned=fft(rebinnedData); % Perform FFT down time



