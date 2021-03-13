#! /usr/bin/python3

import os

import pandas # python3 -m pip install pandas

RESULT_DIR_PATH = os.path.join(os.path.abspath('.'), 'results')
COMBINED_FILENAME = 'Combined_MCTestResult.csv'

FILENAME_LIST = []

for filename in os.listdir(RESULT_DIR_PATH):
	if filename.startswith('p_MCTestResult_') and filename.endswith('.csv'):
		FILENAME_LIST.append(filename)

#print(FILENAME_LIST)
COMBINED = []

def ExpandCombinedList(list, size):
	while len(list) < size:
		list.append([0, 0]) # [count, round]

for filename in FILENAME_LIST:
	df = pandas.read_csv(os.path.join(RESULT_DIR_PATH, filename))

	blnumIndex = df.columns.get_loc('Num_Of_Block')
	countIndex = df.columns.get_loc('Count')
	roundIndex = df.columns.get_loc('Rounds')

	for row in df.itertuples(index=False):

		num = row[blnumIndex]
		ct = row[countIndex]
		rd = row[roundIndex]

		ExpandCombinedList(COMBINED, num)

		COMBINED[num - 1][0] += ct
		COMBINED[num - 1][1] += rd

#print(COMBINED)

with open(os.path.join(RESULT_DIR_PATH, COMBINED_FILENAME), 'w') as file:
	file.write('\"Num_Of_Block\",\"Count\",\"Rounds\",\"Possibility\"\n')
	for i in range(len(COMBINED)):
		file.write('{num},{ct},{rd},{poss}\n'.format(
			num  = i + 1,
			ct   = COMBINED[i][0],
			rd   = COMBINED[i][1],
			poss = COMBINED[i][0] / COMBINED[i][1]
		))
