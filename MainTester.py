#! /usr/bin/python3

import os
import time
from concurrent.futures import ThreadPoolExecutor

import pandas      # python3 -m pip install pandas
import progressbar # python3 -m pip install progressbar2

import ProgBarConfig
import DiffMonTest
import BlockTimeTest
import BlockTimeDistTest
import TesseractTest

# Basic configurations
MAX_NUM_OF_THREADS  = 4
INPUT_CSV_FILE_PATH = os.path.join(os.path.abspath('.'), 'DiffSummary.csv')
OUTPUT_DIR_PATH     = os.path.join(os.path.abspath('.'), 'results')

# Global variables
print('INFO:', 'Loading CSV file...')
DIFF_DATASET = pandas.read_csv(INPUT_CSV_FILE_PATH)
print('INFO:', 'Done.')

# Tests configurations
TEST_LIST = [
	BlockTimeDistTest.BlockTimeDistTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH),
	BlockTimeTest.BlockTimeTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH,  True, 100, False),

	# DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH,  1000, 20, 900, True, 1), # take long time, repeatedly restart
	# DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH,   50, 20, 900, True, 2), # Added by the for loop
	# BlockTimeTest.BlockTimeTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH,  True,  50,  True),
	# BlockTimeTest.BlockTimeTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, False, 100, False),
	# BlockTimeTest.BlockTimeTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, False, 50, True), # too many records
	# TesseractTest.TesseractTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, [
	# 	(2,    60),
	# 	(2,   120),
	# 	(1.5,   0),
	# 	(1.5, 120),
	# 	(1.3, 120),
	# ]),
]

TEST_CHECKPOINT_SIZE_MIN  = 50
TEST_CHECKPOINT_SIZE_MAX  = 1500
TEST_CHECKPOINT_SIZE_STEP = 10

for size in range(TEST_CHECKPOINT_SIZE_MIN,
					TEST_CHECKPOINT_SIZE_MAX + TEST_CHECKPOINT_SIZE_STEP,
					TEST_CHECKPOINT_SIZE_STEP):
	TEST_LIST.append(
		DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, size, 20, 900, True, 2)
	)

def Tester(test):
	"""
	The tester function that should be given to the `ThreadPoolExecutor.submit`
	method. This function will call the `begin` method of the `test`.
	"""
	test.Begin()

def main():
	with ThreadPoolExecutor(max_workers=MAX_NUM_OF_THREADS) as testerPool:

		# Calculate total steps
		totalSteps  = sum([test.totalSteps for test in TEST_LIST])
		currentStep = 0

		# Fill in thread pool
		print('INFO:', 'Begin tests...')
		resList = [testerPool.submit(Tester, test) for test in TEST_LIST]

		# check status
		with progressbar.ProgressBar(max_value=totalSteps, **ProgBarConfig.PROGBAR_ARGS) as bar:
			finishedList = []
			while currentStep < totalSteps:
				time.sleep(0.1)

				finishedListLen = len(finishedList)
				for test in TEST_LIST:
					if test.currentStep == test.totalSteps and test not in finishedList:
						if finishedListLen == len(finishedList):
							print()
						print('INFO:', test.testName, 'is done.')
						finishedList.append(test)

				currentStep = sum([test.currentStep for test in TEST_LIST])
				bar.update(currentStep)

		# TEST_LIST[0].Begin()
		print('INFO:', 'Done.')

	return None

if __name__ == '__main__':
	exit(main())
