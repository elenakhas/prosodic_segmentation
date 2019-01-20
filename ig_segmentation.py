'''
    File name: ig_segmentation.py
    Author: Elena Khasanova and Siyana Pavlova
    Date created: 21/12/2018
    Date last modified: 26/12/2018
    Python Version: 3.5
'''

import re


def ig_parsing(filename):
    '''Takes a text file PreparedSpeech.proDataV3, which contains prosody feature vectors, and parses its content into a list of dictionaries
    Parameters:
    filename - a string, PreparedSpeech.proDataV3 file with path included
    Returns: list - list of dictionaries, each entry corresponds to a word, keys in the dictionary are keywords for the acoustic parameters, values - characters or numbers represented as strings'''

    #   regular expression that takes a line in the file
    pattern = re.compile(r'\b.+?=.+?;(?:\s|$)')
    #   initialize a list to store the valie
    list = []
    #   open the original file in the reading mode
    with open(filename, 'r', encoding="utf-8") as file:
        #   read each line (that represents a word and its parameters) in the file
        for line in file.readlines():
            #    find all occurrences of the pattern in each line
            items = pattern.findall(line)
            #   create a dictionary with keys = keywrods, values - numerical or alphabetic value from the file
            dictionary = {item.split('=')[0]: '='.join(item.split('=')[1:]).encode('utf-8')[:-2] for item in items}
            #   append each dictionary to a list that stores information about all the words in the file
            list.append(dictionary)
            #   return the list
        return list


def ig_building(filename):
    '''Takes a text file PreparedSpeech.proDataV3, which contains acoustic parameters, calls ig_parsing on this file, and defines whether a word forms an intonation group (IG) boundary.
    Parameters:
    filename - a string, PreparedSpeech.proDataV3 file with path included
    Returns: list - list of dictionaries, each entry corresponds to an IG, keys in the dictionary are keywords for the parameters of IGs: beginning, end, and type, values - corresponding values from the file'''
    #   create a list of parameters by calling ig_parsing on the file
    list = ig_parsing(filename)
    #   initialize a list to store intonation groups
    igs = []
    #   initialize the start time of the first word as ig_start
    ig_start = list[0]['WrdStart']
    #   for each dictionary in the list of parameters
    for dic in list:
        #   if the needed keys do not exist, give a default value of 0
        if dic.get("VNDurNorm", 0) and dic.get("VNF0Delta", 0) and dic.get("VNF0SlopeT2", 0) and dic.get("VNF0Level", 0) and dic.get("lastF0Level", 0):
        #   if the keys exist, take the values corresponding to the following keys, process values - remove extra characters such as whitespace or "%", convert numerical values to floats:
        #   VNDurNorm - the normalized duration of the last vowel;
        #   VNF0Delta - the F0 delta (difference between the last and the first syllable) of the last vowel of a word;
        #   VNF0SlopeT2 - the F0 slope (VNF0Slope) on the last syllable multiplied by squared VNDurNorm;
        #   compare the values to the known thresholds
            if float(dic['VNDurNorm'][:-1]) >= 150.0 or float(dic['VNF0Delta']) >= 8 or abs(float(dic['VNF0SlopeT2'])) > 16000.0:
                #   if there is a pause before an IG that has not beed marked as a pause before the previous IG
                if dic.get("VNPauseBefore", 0) and igs[-1]['label'] != '#':
                    pause_beg = float(dic['WrdStart']) - float(dic['VNPauseBefore'])
                    igs.append(({'beg':pause_beg, 'end': dic['WrdStart'], 'label': '#'}))
                #   determine the type of the IG if the word qualifies as an IG boundary by comparing VNF0Level (F0 of the last syllable) and lastF0Level(F0 of the last vowel normalized by speaker):
                if float(dic['VNF0Level'][:-1]) > 85.0 or float(dic['lastF0Level'][:-1]) > 20.0:
                    #   if a word qualifies as an IG of continuation type, add it to the igs dictionary with corresponding values of start, end, and type
                    igs.append({'beg': ig_start, 'end': dic['WrdEnd'], 'label': "IG_C"})
                    #   once the new IG is defined, its end value becomes the start value of the next IG
                    ig_start = dic['WrdEnd']
                    #   if a word qualifies as an IG of final type, add it to the igs dictionary with corresponding values of start, end, and type
                if float(dic['VNF0Level'][:-1]) < 15.0 or float(dic['lastF0Level'][:-1]) < 20.0:
                    igs.append({'beg': ig_start, 'end': dic['WrdEnd'], 'label': "IG_F"})
                    #   once the new IG is defined, its end value becomes the start value of the next IG
                    ig_start = dic['WrdEnd']
                #   if there is a pause after IG,
                if dic.get("VNPauseAfter", 0): # or dic.get("VNPauseBefore", 0):
                    pause_end = float(dic['WrdEnd']) + float(dic['VNPauseAfter'])
                    igs.append({'beg': dic['WrdEnd'], 'end': str(pause_end), 'label': "#"})
                    ig_start = str(pause_end)

        # pause - beg - end of previous IG - IG start, end - start of the word

    return igs

def copy_file(filename, igs):
	'''Takes a TextGrid file, copies its contents into another file
	and add an item to represent the intonation groups

	Parameters:
	filename - a string, the original TextGrid file (with path included)
	igs = a list/dictionary? of intonation groups

	Returns: String - the name of the new file created
	'''

	#Initialise a counter for the lines of the original file
	count = 0
	#Open the original file and the file to be created
	with open('./PreparedSpeech_IG.TextGrid', 'w', encoding="utf-8") as filewrite:
		with open(filename, encoding = "utf-8") as f:
			#For each line read it and copy it into the new file
			#but change it if it is the 7th line
			for line in f.readlines():
				count += 1
				filewrite.write("size = 3\n" if count == 7 else line)
		#Write the details of the IG item
		filewrite.write(' '*4+'item [3]:\n')
		filewrite.write(' '*8+'class = "IntervalTier"\n')
		filewrite.write(' '*8+'name = "IG"\n')
		filewrite.write(' '*8+'xmin = 0\n')
		filewrite.write(' '*8+'xmax = {0}\n'.format(igs[len(igs)-1]['end']))
		filewrite.write(' '*8+'intervals: size = {0}\n'.format(len(igs)))
		#For each IG, write its sequence number, beginning, end and label
		for i in range(len(igs)):
			filewrite.write(' '*8+'intervals [{0}]:\n'.format(i+1))
			filewrite.write(' '*12+'xmin = {0}\n'.format(str(float(igs[i]['beg']))))
			filewrite.write(' '*12+'xmax = {0}\n'.format(str(float(igs[i]['end']))))
			filewrite.write(' '*12+'text = "{0}"\n'.format(igs[i]['label']))
	#Return the name of the new file
	return 'File PreparedSpeech_IG.TextGrid created in current folder'

if __name__=="__main__":
    igs = ig_building('./PreparedSpeech.proDataV3')
    print(copy_file('./PreparedSpeech.TextGrid', igs))
