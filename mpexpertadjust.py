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
SAMPLE_QTY=9

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
	res.reverse()
	return res


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
		if len(line_ar)>21:
			# this means that there are some commas in the SAMPLE_NAME and we have to handle this case
			tmp_line = []
			tmp_line.append(' '.join(line_ar[0:(len(line_ar)-21+1)]))
			tmp_line += line_ar[24-21+1:]
			line_ar = tmp_line
		samples.append([elem.strip() for elem in line_ar])
	f.close()
except:
	tkinter.messagebox.showinfo(title="MPExpertAdjust Error", message='Malformed input file '+SAMPLE_FILE)
	sys.exit(1)

# Make sure to create always a new file
if os.path.exists(OUTPUT_FILE):
	os.unlink(OUTPUT_FILE)

break_flag = False
with open(OUTPUT_FILE,'a+') as f:
	standards_present=[]
	for row in samples:
		if break_flag==True: break
		found = False
		std = is_standard(row[SAMPLE_NAME],row[SAMPLE_ELEMENT],standards)
		if std[0]==True:
			f.write(row[SAMPLE_NAME]+','+row[SAMPLE_ELEMENT]+','+row[SAMPLE_QTY]+','+std[1]+','+row[SAMPLE_DATE]+'\n')
			continue
		out_rev = written_lines_reversed(f)
		# now we reverse the already written output file and we parse it
		# searching for the first standard with the current element
		for line_string in out_rev:
			if break_flag==True: break
			line = [elem.strip() for elem in line_string.split(',')]
			if row[SAMPLE_ELEMENT]==line[1] and is_standard(line[0],line[1],standards)[0]==True:
				# standard found! Applying the forumula
				res = (float(line[3])*float(row[SAMPLE_QTY]))/float(line[2])
				diluition_factor = row[SAMPLE_NAME].split(' ')[-1]
				if diluition_factor.isdigit()==False:
					tkinter.messagebox.showinfo(title="MPExpertAdjust Error", message='Test "'+row[SAMPLE_NAME]+'" does not have a diluition factor')
					break_flag=True
					break
				diluition = float(row[SAMPLE_NAME].split(' ')[-1])
				res = res*diluition
				f.write(row[SAMPLE_NAME]+','+row[SAMPLE_ELEMENT]+','+row[SAMPLE_QTY]+','+str(res)+','+row[SAMPLE_DATE]+'\n')
				found = True
				break
		# if we are here it means that we didn't find the associated standard for the sample
		# or the sample does not have a diluition set
		if break_flag==True: break # we exit with error and we remove the output file
		if found==False:
			f.write(row[SAMPLE_NAME]+','+row[SAMPLE_ELEMENT]+','+row[SAMPLE_QTY]+',???????,'+row[SAMPLE_DATE]+'\n')


# remove the output file in case of error
if break_flag==True:
	os.unlink(OUTPUT_FILE)

