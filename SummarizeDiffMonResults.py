#! /usr/bin/python3

import os

RESULT_DIR_PATH = os.path.join(os.path.abspath('.'), 'results')
SUMMARY_FILENAME = 'ChkptTestSummary.csv'

FILENAME_LIST = []

for filename in os.listdir(RESULT_DIR_PATH):
	if filename.startswith('chkpt_') and filename.endswith('.csv'):
		FILENAME_LIST.append(filename)

#print(FILENAME_LIST)
SUMMARIES = []

def RemoveNewLines(lines, sym = '\n'):
	return [line[:len(line) - 1]
			if line.endswith(sym)
			else line
			for line in lines]

def RemoveQuotes(lines):
	return [line[1 : len(line) - 1]
			if line.startswith('\"') and line.endswith('\"')
			else line
			for line in lines]

def Convert2Dict(lines):
	res = {}
	for line in lines:
		colPos = line.find(':')
		if colPos > 0:
			key = line[:colPos].strip()
			val = line[colPos + 1:].strip()
			res[key] = val
	return res

for filename in FILENAME_LIST:
	with open(os.path.join(RESULT_DIR_PATH, filename), 'r') as file:
		lines = file.readlines()
		startLine = 0
		line = lines[startLine]
		while not line.startswith('\"#####TABLE_ENDS#####\"'):
			startLine += 1
			line = lines[startLine]

		usefulLines = RemoveQuotes(RemoveNewLines(lines[startLine + 1:]))
		d = Convert2Dict(usefulLines)

		# print(usefulLines)
		# print(d)

		chkptSize   = int(d['Checkpoint Size'])
		numShutdown = int(d['Num of Shutdown'])
		numOfChkpt  = int(d['Num of Chkpts']  )
		SUMMARIES.append((chkptSize, numShutdown, numOfChkpt))

SUMMARIES = sorted(SUMMARIES, key=lambda rec: rec[0])

#print(SUMMARIES)

with open(os.path.join(RESULT_DIR_PATH, SUMMARY_FILENAME), 'w') as file:
	file.write('\"Checkpoint_Size\",\"Num_of_Shutdown\", \"Num_of_Checkpoints\"\n')
	for rec in SUMMARIES:
		file.write('{chkpt},{numOfSd},{numOfChkpt}\n'.format(
			chkpt      = rec[0],
			numOfSd    = rec[1],
			numOfChkpt = rec[2]
		))
