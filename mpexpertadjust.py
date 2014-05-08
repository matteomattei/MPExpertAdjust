#!/usr/bin/env python

import os, sys, csv
import tkinter, tkinter.messagebox

STANDARD_FILE='defstd.txt'
STANDARD_NAME=0
STANDARD_ELEMENT=1
STANDARD_QTY=2

SAMPLE_NAME=0
SAMPLE_DATE=2
SAMPLE_ELEMENT=4
SAMPLE_QTY=8

OUTPUT_FILE='output.csv'

def is_standard(label, element, standards):
	"""Check if a label is a standard"""
	for s in standards:
		if label.strip()==s[STANDARD_NAME].strip() and element.strip()==s[STANDARD_ELEMENT].strip():
			return (True,s[STANDARD_QTY])
	return (False,)

def written_lines_reversed(f):
	"""Return all lines written in the output file as a list in reverse order"""
	f.seek(0) # restart from the beginning of the file
	res = []
	while True:
		line = f.readline()
		if line=='': break
		res.append(line)
	f.seek(2) # set the pointer at the end of the file
	return res.reverse()


### MAIN PROGRAM ###
window = tkinter.Tk()
window.wm_withdraw()

if len(sys.argv) == 1:
	tkinter.messagebox.showinfo(title="MPExpertAdjust Error", message='No input file supplied')
	sys.exit(1)

# READ STANDARD FILE
standards = []
try:
	f = open(STANDARD_FILE,'r')
	reader = csv.reader(f, delimiter=';')
	for i in reader:
		if len(i)==0: continue
		standards.append([elem.strip() for elem in i])
	f.close()
except:
	tkinter.messagebox.showinfo(title="MPExpertAdjust Error", message='Malformed standard file '+STANDARD_FILE)
	sys.exit(1)

# READ SAMPLE FILE
SAMPLE_FILE=sys.argv[1]
samples = []
try:
	f = open(SAMPLE_FILE,'r')
	while True:
		line = f.readline()
		if line == '': break
		if line == '\n': continue
		if line.startswith('Label,Type'): continue
		if line[0] == '\x00': continue
		if line[0] == '\ufeff': continue
		line_ar = line.split(',')
		if len(line_ar)>=2 and (line_ar[1]=='STD' or line_ar[1]=='BLK'): continue
		samples.append([elem.strip() for elem in line_ar])
	f.close()
except:
	tkinter.messagebox.showinfo(title="MPExpertAdjust Error", message='Malformed input file '+SAMPLE_FILE)
	sys.exit(1)

#print(standards)
#Eprint(samples)

with open(OUTPUT_FILE,'w+') as f:
	standards_present=[]
	for row in samples:
		std = is_standard(row[SAMPLE_NAME],row[SAMPLE_ELEMENT],standards)
		if std[0]==True:
			f.write(row[SAMPLE_NAME]+','+row[SAMPLE_ELEMENT]+','+row[SAMPLE_QTY]+','+std[1]+','+row[SAMPLE_DATE]+'\n')
			continue
		out_rev = written_lines_reversed(f)
		# now we reverse the already written output file and we parse it
		# searching for the first standard with the current element
		for line in out_rev:
			if row[SAMPLE_ELEMENT]==line[1] and is_standard(line[0],row[1],standards)[0]==True:
				# standard found! Applying the forumula
				res = (line[3]*row[SAMPLE_QTY])/line[2]
				dilution = row[0].split(' ')[-1]
				res = res*dilution
				f.write(row[SAMPLE_NAME]+','+row[SAMPLE_ELEMENT]+','+row[SAMPLE_QTY]+','+res+','+row[SAMPLE_DATE]+'\n')
