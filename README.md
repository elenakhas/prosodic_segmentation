# prosodic_segmentation
A project for the class of Phonectics&Phonology, Master TAL(NLP), Lorrain University

Completed by Elena Khasanova and Siyana Pavlova

### The goal
given a text file with a specified format, to parse the file and collect the relevant information, split the provided signal into intonation groups according to a set of rules, and add this information to a .TextGrid file to further display in Praat.

### Rules:
Our program uses empirical rules based on prosodic features: VNDurNorm, the normalized duration of the last vowel; VNF0Delta, the F0 delta (difference between the last and the first syllable) of the last vowel of a word; VNF0SlopeT2, the F0 slope (VNF0Slope) on the last syllable multiplied by squared VNDurNorm; VNF0Level, F0 of the last vowel; lastF0Level, F0 of the last vowel normalized by speaker.

### Files:

AutomaticProsodicSegmentation.pdf - Project report;

ig_segmentation.py - the code;

ParolePreparee.wav - an example audio file;

PreparedSpeech_IG.TextGrid - the output file;

PreparedSpeech.proDataV3 - the input file containing speech and acoustic features;

PreparedSpeech.TextGrid - the input file with phone and word segmentation;

PreparedSpeechREF.ProsoGrid - reference file for comparison;

PreparedSpeechREF.TextGrid - reference file for comparison.
