# DecentDiffMonitorExpr
Experiment code for Decent Difficulty Monitor.

## `GenerateDiffCsv.py`

- Pull all block numbers, timestamps, and difficulty values from the Geth's
  backend storage, and write them to a CSV file in the current working
  directory.

## `MainTester.py`

- Loads the CSV file generated from previous step.
- Then, it will run all test cases.
- Configurable parameters/variables:
	- `MAX_NUM_OF_THREADS`: Maximum number of threads created by the thread pool.
	                        Each test case occupies one thread.
	- `INPUT_CSV_FILE_PATH`: The path to the CSV file generated from previous
	                         step.
	- `OUTPUT_DIR_PATH`: The path to the output directory.
	- `TEST_LIST`: List of test cases.
