#! /usr/bin/python3

import os
import sys

import progressbar # python3 -m pip install progressbar2

import ProgBarConfig

sys.path.append(os.path.join('.', 'libs', 'GethDBReader'))

from GethDBReader import GethDB

# ZERO_HASH_256 = b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'

GETH_BACKEND_DB = GethDB.GethDB('/mnt/d/gethdb/geth/chaindata', '/home/public/geth-ancient')

with open('DiffSummary.csv', 'w') as outCsv:

	# Write CSV file header
	outCsv.write('\"Block_Number\",\"Block_Time\",\"Difficulty\"\n')
	outCsv.flush

	# Start to iterate through the DB
	print('INFO:', 'Iterating through the GethDB...')
	estMaxBlockCount = GETH_BACKEND_DB.AncientBlockCount() + (20 *  6000)
	with progressbar.ProgressBar(max_value=estMaxBlockCount, **ProgBarConfig.PROGBAR_ARGS) as bar:
		IsEnded = False
		i = 0
		while not IsEnded:
			try:
				outCsv.write('{num},'.format(num=GETH_BACKEND_DB.GetHeaderByNum(i)['Number']))
				outCsv.write('{time},'.format(time=GETH_BACKEND_DB.GetHeaderByNum(i)['Time']))
				outCsv.write('{diff}\n'.format(diff=GETH_BACKEND_DB.GetHeaderByNum(i)['Difficulty']))
				#outCsv.write('\n')
				i += 1
				bar.update(i)
			except KeyError:
				IsEnded = True
				bar.update(estMaxBlockCount)
				print('INFO:', 'DONE.')
