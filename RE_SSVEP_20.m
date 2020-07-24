%% 20-RE-SSVEP
clear; close all

%%
datDir = 'C:\Users\Richard Naar\Documents\dok\ssvep\Proof of concept\artiklid ja raamatud (Liisa)\20-ER-SSVEP\'; % data (light sensor) dir
eeglabDir = ' C:\Program Files\MATLAB\R2014a\toolbox\eeglab13_6_5b\';                                               % eeglab program directory
locfile =   ' C:\Program Files\MATLAB\R2014a\toolbox\eeglab13_6_5b\32_4EOG.ced';                                    % dir of the electrode location file 

%% IMPORT LIGHT SENSOR DATA
lightSensor = 1;

if lightSensor == 1; impdir = [datDir, 'Light\']; else impdir = [datDir, 'Pilot\']; end                                                % import directory

cleandir = [datDir, 'Clean\'];

implist = dir([impdir, '*.bdf']);                                           % make a fresh list of the contents of the raw files directory (input of this loop)

%%
events = {'pic'}; % 'pic_non-distr_pos'
segment = {'first', 'first-second', 'second'};
valence = {'ntr', 'neg'};
distrCond = {'non-distr', 'distr'};


dataStruct = {{implist.name}', segment', valence', distrCond'};

%% Import and find events

for subi = 1:length(implist);
fprintf('loading participant: %s \n', implist(subi).name);

ALLEEG = []; EEG = []; CURRENTSET = [];                                     % erase anything in the eeglab. 
        
dat2plot = openbdf([impdir, implist(subi).name]);                                % avab faili, et lugeda kanalite arvu
event = strmatch('Status', {dat2plot.Head.Label},'exact');                       % leiab event kanali asukoha
erg1 = strmatch('Erg1', {dat2plot.Head.Label}, 'exact');                         % leiab Erg1 kanali asukoha
exg1 = strmatch('EXG1', {dat2plot.Head.Label}, 'exact');
clear dat;                                                                  % kuna see fail võib ruumi võtta, kustutame ära

EEG = pop_biosig([impdir, implist(subi).name]); 
if lightSensor == 0
    
EEG = pop_biosig([impdir, implist(subi).name], 'ref',exg1+4:exg1+5);       % reference at EXG5 and EXG6
 
[ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, CURRENTSET, 'setname', implist(subi).name(1:end-4));% imporditud andmestiku salvestamine

EEG.data = EEG.data([1:64 exg1:exg1+3],:); EEG.nbchan = 68;                 % mittevajalike kanalite eemaldamine (32 peakanalit, 4 silma, täiendav EMG kanal, GSR 1 ja 2, Pletüsmograf)
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 

EEG = pop_chanedit(EEG, 'load',{[datDir 'BioSemi64_4.loc'] 'filetype' 'autodetect'});     % Edit the channel locations structure of an EEGLAB dataset, EEG.chanlocs. 
[ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 

else
EEG.data = EEG.data(erg1,:); EEG.chanlocs = EEG.chanlocs(erg1,:); EEG.nbchan = 1;
end

% FIND EVENTS
trig.tSeq = {'1' 'fix'; '2' 'pic'; '3' 'sound'; '4' 'iti'; '5' 'pause'};

if strcmp(implist(subi).name, '112_20_ER_SSVEP.bdf')
    trig.cond = {'1' 'neg'; '2' 'ntr'; '6' 'distr'; '3' 'non-distr'};
else
    trig.cond = {'1' 'neg'; '2' 'ntr'; '3' 'distr'; '6' 'non-distr'};
end

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
    
    EEG.event(eventi).tInfo = [seq{:},'_',cond,'_',val{:}];
end

% eegplot(EEG.data, 'events', EEG.event) % see the raw file

%%
% %% find events

events = {'pic'}; % 'pic_non-distr_pos'
% segment = {'first', 'first-second', 'second'}; segv = 0; % old segments
% segment = {'first', 'second', 'third', 'fourth', 'fifth'}; segv = 1;
segment = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'}; segv = 1;
% segment = {'1', '2', '3', '4', '5', '6'}; segv = 1;


segTime = (0:2:24)*EEG.srate;
valence = {'ntr', 'neg'};
distrCond = {'non-distr', 'distr'};


dataStruct = {{implist.name}', segment', valence', distrCond'};
typeIndx = 1;
for segIndx = 1:length(segment)
    for valIndx = 1:length(valence)
        for condIndx = 1:length(distrCond)

% currentIndx = 1;

    allIndx = find( strcmp({EEG.event.type}, events{typeIndx}) .*  strcmp({EEG.event.valence}, valence{valIndx}) ... 
        .* strcmp({EEG.event.distrCond}, distrCond{condIndx}) );

% new segments
if segv == 1
    eventOnset = {EEG.event(allIndx).latency}; % find start of the epoch 
else
%old segments    
if segIndx < 3
    eventOffset = {EEG.event(allIndx+segIndx).latency}; % find event offset (sound, iti == 2)
    eventOnset = {EEG.event(allIndx).latency}; % find start of the epoch 
else
    eventOffset = {EEG.event(allIndx+2).latency}; % iti
    eventOnset = {EEG.event(allIndx+1).latency}; % sound
end

end
% fprintf('Found %d events. \n', currentIndx-1)
fprintf('Found %d events. \n', length(eventOnset))

%% select channels
% electrodes = {'O1', 'Oz', 'O2', 'POz', 'P1', 'P2', 'PO3', 'PO4'};'P7','P8'
if lightSensor == 0
electrodes = {'O1', 'Oz', 'O2','PO3', 'PO4'}; %  'PO8' [0], ,'PO7'  
% electrodes = {'Oz'};
else
electrodes = {'Erg1'};    
end

elec2plot = find(ismember({EEG.chanlocs.labels}, electrodes)); % find electrode indexes
% elec2plot = 73;

fprintf('\nNumber of electrodes aggregated:  %d ', length(elec2plot)); fprintf('\n')

%%
if lightSensor == 1;transient = 0; else transient = 0.5; end % this is in seconds
srate = EEG.srate;
%%
thisCueEvent = 0;
meanComplexFFT = [];
while (thisCueEvent <= length(eventOnset)-2)
thisCueEvent = thisCueEvent + 1;
startSampleERP = round(eventOnset{thisCueEvent}+transient*srate);

if segv == 1
% new segments start
    startSample = round(eventOnset{thisCueEvent}+transient*srate + segTime(segIndx)); 
    trialDur = 2; % 
% new segments end
else    
% old segments      
     startSample = round(eventOnset{thisCueEvent}+transient*srate); % subtract the transient off from the start
     endSample = round(eventOffset{thisCueEvent});     
     trialDur = round((endSample-startSample)/srate); % 
% end of old segments 
end
     % redifine the end or the start (for coherent averaging)
     endSample = startSample+trialDur*srate; % find the event offset if the epoch is calculated from cue event
          
    % Pull out a timeseries that follows/preceeds the event 

    allSamples = EEG.data(elec2plot,startSample:endSample-1); % channels
    allSamplesERP = EEG.data(elec2plot,startSampleERP:endSample-1); %-mean(EEG.data(elec2plot,startSampleERP-(srate*0.25):startSampleERP-1),2);
%     allSamplesERP = bsxfun(@minus, EEG.data(elec2plot,startSampleERP:endSample-1), mean(EEG.data(elec2plot,startSampleERP-(srate*0.25):startSampleERP-1),2)); 
    % eventIndx = 1:length(event) % loop through the event categories

    if size(elec2plot,2) > 1
        allSamples=squeeze(mean(allSamples(1:end-1, :))); % mean of channels
        allSamplesERP=squeeze(mean(allSamples(1:end-1, :))); % mean of channels
    end
    
    allSamplesERP = allSamplesERP-mean(mean(EEG.data(elec2plot,startSampleERP-(srate*0.25):startSampleERP-1),2));
    
    % We can now bin into 1 second intervals
    rebinnedData=reshape(allSamples, EEG.srate*2,trialDur/2);
    fftRebinned=fft(rebinnedData); % Perform FFT down time
    
    meanERP{subi, segIndx, valIndx, condIndx, thisCueEvent} = allSamplesERP;
    meanComplexFFT(:,thisCueEvent) = mean(fftRebinned,2); % nb abs % This is the mean complex FFT for this trial (averaged across bins)
    grandAverageERP{subi, segIndx, valIndx, condIndx, thisCueEvent} = allSamplesERP; 
end

grandAverage{subi, segIndx, valIndx, condIndx} = mean(meanComplexFFT,2); % Average across trials - the abs means we do NOT still keep coherent information

%% SNR

fdat = abs(grandAverage{subi, segIndx, valIndx, condIndx}(1:99)).^2;
% proov = squeeze(mean(mean(cell2mat(grandAverage),2),3));
% fdat = abs(proov(1:99)).^2;

snrE = zeros(1,size(fdat,1));
skipbins =  1; % 1 Hz, hard-coded! (not skipping)
numbins  = 2; %  2 Hz, also hard-coded!

% loop over frequencies and compute SNR
for hzi=numbins+1:length(fdat)-numbins-1
    numer = fdat(hzi);
    denom = rms( fdat([hzi-numbins:hzi-skipbins hzi+skipbins:hzi+numbins]) ); 
    snrE(hzi) = numer./denom;
end  


nfft = ceil( EEG.srate/.5 ); % .5 Hz resolution
hz = linspace(0,EEG.srate,nfft);

stem(hz(1:size(snrE,2)),snrE)

%%
% %     subplot(2,2,eventIndx); hold on
% %     title(strrep(events{eventIndx}, '_',' '))

%    bar(abs(grandAverage(2:49)));

%     bar(abs(grandAverage{eventIndx}(2:60)));
allSnrE{subi, segIndx, valIndx, condIndx} = snrE;
% p.subject(subi).condition(eventIndx).data.EEG.average.snr = snrE; 

% %     bar(allSnrE{subi,eventIndx});

%     stem(abs(grandAverage{eventIndx}(2:60)),'k','linew',3,'markersize',2.5,'markerfacecolor','r')
%     bar(squeeze( mean(snrE(:, eventIndx, 1:end),1)));

        end % next comd
    end % next val
end % next segment
end % next sub

% save([datDir, 'grandAverage_pilot_lightSensor'], 'grandAverage', '-v7.3');
save([datDir, 'grandAverage_pilot_lightSensor_framesLong'], 'grandAverage', '-v7.3')
% save([datDir, 'grandAverage_pilot_segments'], 'grandAverage', '-v7.3');
% save([datDir, 'grandAverage_pilot'], 'grandAverage', '-v7.3');

%%
% dataStruct{:}

implistavg = dir([datDir, '*.mat']); 
load([datDir, implistavg(5).name]); % load data
%%
cd('C:\Users\Richard Naar\Documents\dok\ssvep\Proof of concept\artiklid ja raamatud (Liisa)\20-ER-SSVEP\Figures')
srate = 512;
%%

colors = {'k','m','b','g','y','r', '--k','--m','--b','--g','--y','--r'};
figure(2)
hold

N = 12;
ij = 1;
for ij = 1:N
subid = 1; fprintf( ['\nsubjects(s): ', dataStruct{1}{ subid }, '\n'] )
segment = ij; fprintf( ['segment(s): ', dataStruct{2}{ segment }, '\n'] )
valence = 1:2; fprintf( ['segment(s): ', dataStruct{3}{ valence }, '\n'] )
condition = 1:2; fprintf( ['condition(s): ', dataStruct{4}{ condition }, '\n'] )


dat2plot = grandAverage(subid, segment, valence, condition);
% size(dat2plot)

dat2plot = squeeze(cat(4,dat2plot{:}));
% dat2plot = abs(mean(dat2plot,2)).^2;
dat2plot = mean(dat2plot,2);

% 
% stem(dat2plot,['', colors{gcf}],'linew',3,'markersize',2.5)


fdat = abs(dat2plot(1:99)).^2; % fdat = dat2plot(1:99); %
% fdat = abs(dat2plot(1:99));
% hz = 0:.5:round((srate*2));
% plot(hz(2:99),fdat(2:99),['', colors{1}],'linew',3,'markersize',2.5) %+0.2*(ij-1)
% hold
% legend({'Sub1'; 'Sub2'},'FontSize',12)

snrE = zeros(1,size(fdat,1));
skipbins =  4; %2 2 Hz, hard-coded! (not skipping)
numbins  = 8; %4  4 Hz, also hard-coded!

% loop over frequencies and compute SNR
for hzi=numbins+1:length(fdat)-numbins-1
    numer = fdat(hzi);
    denom = rms( fdat([hzi-numbins:hzi-skipbins hzi+skipbins:hzi+numbins]) ); 
    snrE(hzi) = numer./denom;
end  


nfft = ceil( srate/.5 ); % .5 Hz resolution
% hz = linspace(0,round(srate),nfft);



% stem(hz(1:size(snrE,2)),snrE, 'r')
% % legend({'1st'; '2nd'; '3rd'; '4th'; '5th';},'FontSize',12)
% wins = 1:segment;
% legend({num2str(wins')},'FontSize',12)

stem(hz(1:size(snrE,2))+0.2*(ij-1),snrE,['', colors{ij}],'linew',3,'markersize',2.5) %+0.2*(ij-1)
% hold
%stem(hz(1:size(snrE,2)),snrE,['', colors{2}],'linew',3,'markersize',2.5)

% col = zeros(size(snrE)); col(find(hz == 37.5)) = 1; col = col .*snrE; col(find(col == 0)) = NaN;
% stem(hz(1:size(col,2)),col,'r','linew',3,'markersize',2.5)
% 
% 
% legend({'Other'; 'Stim'},'FontSize',12)
% ylabel('SNR','FontSize',12); xlabel('Frequency', 'FontSize',12)  

%legend({'Light sensor measurement'},'FontSize',12)
%legend({'LS (ntr)', 'LS (neg)'},'FontSize',12)


% set(gca,'ylim',[0 15], 'FontSize',12) % 
% set(gca,'ylim',[0 7000], 'FontSize',12) %
% set(gca,'ylim',[0 max(snrE)+1000], 'FontSize',12) %
set(gca,'xlim',[1 48], 'FontSize',12)
end

%% ntr vs neg
stem(hz(1:size(snrE,2)),snrE,'r','linew',3,'markersize',2.5)

legend({'Ntr'; 'Neg'},'FontSize',12)
ylabel('SNR','FontSize',12); xlabel('Frequency', 'FontSize',12)  


set(gca,'ylim',[0 10.6], 'FontSize',12)
set(gca,'xlim',[1 48], 'FontSize',12)

%% distr vs non-distr

col = zeros(size(snrE)); col(find(hz == 37.5)) = 1; col = col .*snrE; col(find(col == 0)) = NaN;
stem(hz(1:size(col,2)),col,'r','linew',3,'markersize',10)


stem(hz(1:size(snrE,2)),snrE,'--r','linew',3,'markersize',2.5)

legend({'Non-distr (other)'; 'Non-distr'; 'Distr (other)'; 'Distr'},'FontSize',12)
ylabel('SNR','FontSize',12); xlabel('Frequency', 'FontSize',12)  


set(gca,'ylim',[0 10.6], 'FontSize',12)
set(gca,'xlim',[1 48], 'FontSize',12)

%% first half vs second half
col = zeros(size(snrE)); col(find(hz == 37.5)) = 1; col = col .*snrE; col(find(col == 0)) = NaN;
stem(hz(1:size(col,2)),col,'r','linew',3,'markersize',2.5)


stem(hz(1:size(snrE,2)),snrE,'--r','linew',3,'markersize',2.5)

legend({'First-half(other)'; 'First-half'; 'Second-half (other)'; 'Second-Half'},'FontSize',12)
ylabel('SNR','FontSize',12); xlabel('Frequency', 'FontSize',12)  


set(gca,'ylim',[0 14.6], 'FontSize',12)
set(gca,'xlim',[1 48], 'FontSize',12)
%% ERP

% implistavg = dir([datDir, '*.mat']); 
% load([datDir, implistavg(3).name]); % load data

figure(1)
%%
f = 1;
colors = {'k','r'};
subid = 2; fprintf( ['\nsubjects(s): ', dataStruct{1}{ subid }, '\n'] )
segment = 2; fprintf( ['segment(s): ', dataStruct{2}{ segment }, '\n'] )
valence = 1; fprintf( ['segment(s): ', dataStruct{3}{ valence }, '\n'] )
condition = 1; fprintf( ['condition(s): ', dataStruct{4}{ condition }, '\n'] )

dat2plot = grandAverageERP(subid, segment, valence, condition, :);
dat2plot = cell2mat( squeeze(dat2plot) );
%col2avg = length(size(dat2plot))-1;

dat2plot = mean(dat2plot);
plot(dat2plot', colors{f})
hold
%% ICA

% Kui vajalik see on?
% [ALLEEG EEG1 CURRENTSET] = pop_copyset(ALLEEG, 1, 2);                        % this line makes a copy of the dataset for the high pass.                                                      % copy a separaate dataset for ICA training
% [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 
        
% % EEG = pop_eegfiltnew(EEG, [], 1, 6760, 1, [], 0);                           % half-amplitude at 0.75 Hz, transition band edge at 1 Hz                                                   % filter the training data at 1 Hz highpass
% % [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 
% % 
% % EEG = pop_epoch(EEG, {'pic'}, [-0.5 13], 'epochinfo', 'yes');                 % we're defining the segments which will be used for the ICA                                           % extract training epochs 
% % [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 

% EEG = pop_eegthresh(EEG,1,[1:EEG.nbchan-4] ,-1500, 1500, -1, 2,0,0);          % reject extreme values
% [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);               % whenever we see a lot of power for specific point.

% % [EEG ALLEEG(1).rejhist.preICA] = pop_rejspec(EEG, 1, [1:EEG.nbchan], -35, 35, 15, 30, 0, 1);   % cleaning the data of muscle noise        % remove segments with high muscle noise (15-30 Hz)
% % [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);               % whenever we see a lot of power for specific point.
% % 
% % EEG1 = pop_runica(EEG, 'extended', 1, 'interupt', 'on');                     % actually running the ICA                                                % find an ICA solution
% % [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET); 
% %         
% % [ALLEEG EEG CURRENTSET] = pop_newset(ALLEEG, EEG, CURRENTSET, 'retrieve', 1);   % write the solution of the ICA on the data.                            % write the ICA solution back to original data
% % EEG = pop_editset(EEG, 'icachansind', 'ALLEEG(2).icachansind', 'icaweights', 'ALLEEG(2).icaweights', 'icasphere', 'ALLEEG(2).icasphere'); 
% % [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);     
% % 
% % EEG = pop_saveset(EEG, 'filename', EEG.filename, 'filepath', icadir, 'savemode', 'twofiles');










% EEG.event = EEG.event(1:length(EEG.urevent));                               % kui salvestus on varem katkestatud, siis tekib ilma selleta viga
%         [ALLEEG EEG CURRENTSET] = eeg_store(ALLEEG, EEG, CURRENTSET);       % save changes to EEGLAB structure within Matlab
%         EEG = pop_saveset(EEG, 'filename', EEG.subject, 'filepath', indir, 'savemode', 'twofiles'); % save changes to the import directory on disk




