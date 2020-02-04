% 20-RE-SSVEP

datDir = 'C:\Users\Richard Naar\Documents\dok\ssvep\Proof of concept\artiklid ja raamatud (Liisa)\20-RE-SSVEP\'; % data (light sensor) dir
eeglabDir = ' C:\Program Files\MATLAB\R2014a\toolbox\eeglab13_6_5b\';                                               % eeglab program directory
locfile =   ' C:\Program Files\MATLAB\R2014a\toolbox\eeglab13_6_5b\32_4EOG.ced';                                    % dir of the electrode location file 

% IMPORT LIGHT SENSOR DATA

impdir = [datDir, 'Light\'];                                                % import directory
implist = dir([impdir, '*.bdf']);                                           % make a fresh list of the contents of the raw files directory (input of this loop)

ALLEEG = []; EEG = [];                                                      % erase anything in the eeglab. 
        
dat = openbdf([impdir, implist(1).name]);                                   % avab faili, et lugeda kanalite arvu
event = strmatch('Status', {dat.Head.Label},'exact');                       % leiab event kanali asukoha
erg1 = strmatch('Erg1', {dat.Head.Label}, 'exact');                         % leiab Erg1 kanali asukoha
clear dat;                                                                  % kuna see fail võib ruumi võtta, kustutame ära

EEG = pop_biosig([impdir, implist(1).name]); 

% FIND EVENTS
trig.tSeq = {'1' 'fix'; '2' 'pic'; '3' 'sound'; '4' 'iti'; '5' 'pause'};
trig.cond = {'1' 'neg'; '2' 'pos'; '3' 'distr'; '6' 'non-distr'};

for eventi = 1:length(EEG.event)
    
    eString = num2str(EEG.event(eventi).type);
    conNum = str2num(eString(2));
    
    seq = trig.tSeq(strcmp(trig.tSeq, eString(1)),2); % first string keeps track of the trial sequence
    
    if conNum < 6 % if it's smaller than 6 it must be distraction condition
        cond = 'distr';
        val = trig.cond(strcmp(trig.cond, num2str(conNum-3)), 2);
    else % otherwise it's the non-distraction condition
        cond = 'non-distr';
        val = trig.cond(strcmp(trig.cond, num2str(conNum-6)), 2);
    end

EEG.event(eventi).type = [seq{:},'_',cond,'_',val{:}];
end

eegplot(EEG.data, 'events', EEG.event) % see the raw file

