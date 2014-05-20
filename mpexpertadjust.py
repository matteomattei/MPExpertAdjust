#!/usr/bin/env python

import os, sys, csv, time

path = os.path.dirname(os.path.abspath(sys.argv[0]))
STANDARD_FILE=os.path.join(path,'defstd.csv')
STANDARD_NAME=0
STANDARD_ELEMENT=1
STANDARD_QTY=2

SAMPLE_NAME=0
SAMPLE_DATE=2
SAMPLE_ELEMENT=4
SAMPLE_QTY=9

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

def print_error_and_exit(error):
	"""Generate an error file and exit"""
	path = os.path.dirname(os.path.abspath(sys.argv[0]))
	filepath = os.path.join(path,'Error.txt')
	date = time.strftime("%Y-%m-%d %H:%M:%S")
	f = open(filepath,'a+')
	f.write(date+' - Error: '+error+'\n')
	f.close()
	sys.exit(1)

### MAIN PROGRAM ###
if len(sys.argv) == 1:
	print_error_and_exit('No input file supplied')

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
	print_error_and_exit('Malformed standard file '+STANDARD_FILE)

# READ SAMPLE FILE
SAMPLE_FILE=sys.argv[1]
samples = []
try:
	f = open(SAMPLE_FILE,'r')
	while True:
		line = f.readline()
		if line == '': break
		if line.strip() == '': continue
		if line.startswith('Label,Type'): continue
		if line[0] == '\x00': continue
		if 'MP Expert worksheet exported' in line: continue
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
	print_error_and_exit('Malformed input file '+SAMPLE_FILE)

OUTPUT_FILE = os.path.join(path,'CALC_'+time.strftime("%Y%m%d_%H%M%S")+'_'+os.path.basename(SAMPLE_FILE))
with open(OUTPUT_FILE,'a+') as OUTPUT:
	standards_present=[]
	for row in samples:
		found = False
		std = is_standard(row[SAMPLE_NAME],row[SAMPLE_ELEMENT],standards)
		if std[0]==True:
			OUTPUT.write(row[SAMPLE_NAME]+';'+row[SAMPLE_ELEMENT]+';'+row[SAMPLE_QTY]+';'+std[1]+';'+row[SAMPLE_DATE]+'\n')
			continue
		out_rev = written_lines_reversed(OUTPUT)
		# now we reverse the already written output file and we parse it
		# searching for the first standard with the current element
		for line_string in out_rev:
			line = [elem.strip() for elem in line_string.split(',')]
			if row[SAMPLE_ELEMENT]==line[1] and is_standard(line[0],line[1],standards)[0]==True:
				# standard found! Applying the formula
				res = (float(line[3])*float(row[SAMPLE_QTY]))/float(line[2])
				diluition_factor = row[SAMPLE_NAME].split(' ')[-1]
				if diluition_factor.isdigit()==False:
					OUTPUT.close()
					os.unlink(OUTPUT_FILE)
					print_error_and_exit('Test "'+row[SAMPLE_NAME]+'" does not have a dilution factor')
				dilution = float(row[SAMPLE_NAME].split(' ')[-1])
				res = res * dilution
				OUTPUT.write(row[SAMPLE_NAME]+';'+row[SAMPLE_ELEMENT]+';'+row[SAMPLE_QTY]+';'+str(res)+';'+row[SAMPLE_DATE]+'\n')
				found = True
				break
		# if we are here it means that we didn't find the associated standard for the sample
		# or the sample does not have a dilution set
		if found==False:
			OUTPUT.write(row[SAMPLE_NAME]+';'+row[SAMPLE_ELEMENT]+';'+row[SAMPLE_QTY]+';???????;'+row[SAMPLE_DATE]+'\n')


