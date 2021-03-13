# DecentDiffMonitorExpr
Experimental code for Decent Difficulty Monitor.

## Possibility of Successful Attack (False Negative Rate)

### Configure/Build/Run the Experiment

- The related source code is located in `PossibilityTest` directory
- Use CMake to initialize the C++ project
- We are only use target `AttackPossTestDyn` for this experiment
	- Where `Dyn` stands for Dynamic Programming
- Inside `AttackPossTestDyn.cpp`, you can configure the experiment
	- *Line 18*: adjusting the precision. Default is 6; add/remove zeros at the
	end to reduce/increase precision
	- *Line 305*: Maximum wait time
	- *Line 306*: Number of threads used for testing
	- *Line 307*: Maximum number of blocks (N<sub>c</sub>) to test on
	- *Line 308*: Output file name
	- *Line 310*: Percentage of attacker's hash rate (default to 30%)
	- *Line 311*: Percentage of &theta;<sub>min</sub> (default to 80%)
- Run the compiled/built binary, and wait for the experiment to end

### Explanation of the Formula We Are Using

- The detail is provided in [./docs/poss-succ-attack.md](./docs/poss-succ-attack.md)

## False Detections

### Requirements

- The code has been run and tested under Python 3.8
- Python 3rd-party Module Dependencies
	- pandas
	- progressbar2
	- The following are required by *GethDBReader*
		- rlp
		- web3
		- readerwriterlock
		- python-snappy
		- leveldb

### Step 1. `GenerateDiffCsv.py`

- This python script will pull all block numbers, timestamps,
  and difficulty values from the Geth's backend storage, and write them
  into a CSV file
- Configurations:
	- *Line 16*: Replace the first path to Geth's backend LevelDB in your local drive,
	  and replace the second path to the  Geth's backend Ancient database in your local drive
		- The second path can be omitted if it's the `ancient` directory under the LevelDB path
- A CSV file named `DiffSummary.csv` will be generated under the current working directory

### Step 2. `MainTester.py`

- This python script is the main testing program
- Make sure `DiffSummary.csv` generated from previous step is available under
  the current working directory
  (unless you have specified a different path in `INPUT_CSV_FILE_PATH`)
- Difficulty Monitor Test (`DiffMonTest`)
	- *line 45*: The minimum checkpoint size (N<sub>c</sub>) to test on
	- *line 46*: The maximum checkpoint size (N<sub>c</sub>) to test on
	- *line 47*: The step to increase from minimum to maximum
- Additional sub-tests:
	- `BlockTimeDistTest`
		- Count number of blocks that has block time of i seconds,
		  where i is from 1 to 900 seconds.
		- Generate a CSV file showing the distribution of block time among
		  history blocks
	- `BlockTimeTest`
		- Find top/bottom X block times
		- The one configured in *line 29* will find the top 100 block times
- Other configurations:
	- `MAX_NUM_OF_THREADS`: Maximum number of threads created by the thread pool;
	                        Each test case occupies one thread
	- `INPUT_CSV_FILE_PATH`: The path to the CSV file generated from previous
	                         step
	- `OUTPUT_DIR_PATH`: The path to the output directory
	- `TEST_LIST`: List of test cases
- Run the python script, and the result will be generated under `results`
  directory in the current working directory

## Discussion on Forked Chain

A blockchain may fork if miners find multiple blocks having the same predecessor.
Most blockchain protocols address this by requesting honest miners to
mine on the longest fork [[1], [2]].
Because our approach relies on recording arrival times, if a chain
becomes (even temporarily) forked, we must either monitor each fork
simultaneously to record block arrival times, or repeat the
Bootstrap-II and Sync phases if a chain is discovered that is longer
than the chain (or chains) we are currently monitoring.

Our monitor also supports monitoring multiple forks simultaneously.
When the chain is forked, the monitor also forks into identical sub-monitors,
each monitoring their own fork.
Any sub-monitor that has detected an eclipse attack will terminate,
and when there are no active sub-monitors, meaning the entire chain is under
attack, the enclave will shutdown to prevent further attacks.

In case a fork is found that is longer than all monitored forks,
it is necessary to add this fork to the monitor to start monitoring.
However, we cannot directly add this fork because its difficulty value has
not been monitored; we can only consider it if it satisfies two conditions.
First, the predecessor of the new fork must not be any block before the
checkpoint, since all blocks before the checkpoint should be finalized and
any modification made to blocks before the checkpoint is uncommon and suspicious.
Second, the new fork must be longer than all monitored forks,
because adding a shorter fork is meaningless since honest miners mine on
the longest fork.
Once these conditions are satisfied, the new fork can be added by using
the same steps as those in Bootstrap-II phase and Sync phase.

## References

- [[1]] [Block Height And Forking - Bitcoin Developer: Developer Guides](https://developer.bitcoin.org/devguide/block_chain.html#block-height-and-forking)
- [[2]] [A Next Generation Smart Contract \& Decentralized Application Platform](https://cryptorating.eu/whitepapers/Ethereum/Ethereum_white_paper.pdf)

[1]: https://developer.bitcoin.org/devguide/block_chain.html#block-height-and-forking "Block Height And Forking - Bitcoin Developer: Developer Guides"
[2]: https://cryptorating.eu/whitepapers/Ethereum/Ethereum_white_paper.pdf "A Next Generation Smart Contract \& Decentralized Application Platform"
