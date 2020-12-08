#! /usr/bin/python3

import os
import time
from concurrent.futures import ThreadPoolExecutor

import pandas      # python3 -m pip install pandas
import progressbar # python3 -m pip install progressbar2

import ProgBarConfig
import DiffMonTest

# Basic configurations
MAX_NUM_OF_THREADS  = 4
INPUT_CSV_FILE_PATH = os.path.join(os.path.abspath('..'), 'DiffSummary.csv')
OUTPUT_DIR_PATH     = os.path.abspath('.')

# Global variables
print('INFO:', 'Loading CSV file...')
DIFF_DATASET = pandas.read_csv(INPUT_CSV_FILE_PATH)
print('INFO:', 'Done.')

# Tests configurations
TEST_LIST = [
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 1000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 2000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 3000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 4000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 5000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 6000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 7000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 8000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 9000, 20, 900, True, 2),
	DiffMonTest.DiffMonTest(OUTPUT_DIR_PATH, DIFF_DATASET, INPUT_CSV_FILE_PATH, 10000, 20, 900, True, 2),
]

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
			while currentStep < totalSteps:
				time.sleep(0.1)

				currentStep = sum([test.currentStep for test in TEST_LIST])
				bar.update(currentStep)

		print('INFO:', 'Done.')

	return None

if __name__ == '__main__':
	exit(main())
