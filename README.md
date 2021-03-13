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

## Possibility of Successful Attack (False Negative Rate)

- Use CMake to initialize the C++ project
- We are only use target `AttackPossTestDyn` for this experiment
	- Where `Dyn` stands for Dynamic Programming
- Inside `AttackPossTestDyn.cpp`, you can configure the experiment
	- *Line 18*: adjusting the precision. Default is 6; add/remove zeros at the
	end to reduce/increase precision.
	- *Line 305*: Maximum wait time.
	- *Line 306*: Number of threads used for testing.
	- *Line 307*: Maximum number of blocks (N<sub>c</sub>) to test on.
	- *Line 308*: Output file name.
	- *Line 310*: Percentage of attacker's hash rate (default to 30%).
	- *Line 311*: Percentage of &theta;<sub>min</sub> (default to 80%).
- Run the compiled/built binary, and wait for the experiment to end.
- The explanation of the formula we are using is also available at
