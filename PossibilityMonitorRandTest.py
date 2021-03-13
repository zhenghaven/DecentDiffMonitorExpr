import math
import statistics
import numpy as np
from numpy import random

import progressbar # python3 -m pip install progressbar2
import ProgBarConfig

############################################################
# Some basic configurations
############################################################

# The percentage of the hash rate, used for sampling
# default to 100% of network hash rate, so assuming there is no attack
SAMPLE_HR         = 1.0
# Total iteration of tests, so we can get a average value of num of blocks needed
TOTAL_ITERATIONS  = 5000
# Max number of blocks for each test, which should be N_c, since N_c is the num
# of blocks needed in worst case
MAX_BLOCKN        = 430
# False Negative rate that we want
# default to 2^(-128)
SECURE_RATE       = 2 ** (-128)
# Do we need to write results of each iteration to the file?
# If enabled, the output file will be huge.
WRITE_FULL_RESULT = False
OUTPUT_FILE_NAME = 'Poss_Monitor_MaxN_{}_SampleHR_{}.md'.format(
	MAX_BLOCKN,
	str(SAMPLE_HR).replace('.', 'd')
)

TOTAL_HASHRATE  =  285898364400000
INIT_DIFFICULTY = 3546605094014496

def GetAvgBlockTime(diff, hashR):
	return float(diff) / float(hashR)

def GetLambda(avg):
	return 1.0 / avg

def GetHashRate(isAttakcer, attackerR = 0.30):
	if isAttakcer:
		return int(TOTAL_HASHRATE * attackerR)
	else:
		return TOTAL_HASHRATE

def GetNewDiff(initDiff, blockT):
	return int(initDiff * (1 + ((9 - math.ceil(blockT)) / (18432.0))))

def CalcCdf(lmd, t):
	p = -1 * lmd * t
	res = 1 - math.exp(p)
	return res

def CalcPdf(lmd, t):
	p = -1 * lmd * t
	res = lmd * math.exp(p)
	return res

def CalcPossTimeGivenAttacker(avg, blockT):
	return CalcCdf(GetLambda(avg), blockT)

def CalcPossTimeGivenMiner(avg, blockT):
	return CalcCdf(GetLambda(avg), blockT)

def CalcPossAttackerGivenTime(attackerPos, minerPos, attackerPrior = 0.5):
	return (attackerPos * attackerPrior) / ((attackerPos * attackerPrior) + (minerPos * (1 - attackerPrior)))

def CalcPossMinerGivenTime(attackerPos, minerPos, attackerPrior = 0.5):
	return (minerPos * (1 - attackerPrior)) / ((attackerPos * attackerPrior) + (minerPos * (1 - attackerPrior)))

def LogSumExp(x):
	c = x.max()
	return c + np.log(np.sum(np.exp(x - c)))

def main():

	outStr = '# Test Report' + '\n'
	outErrStr = ''

	outCfgStr = '## Configurations' + '\n'
	outCfgStr += '| | | ' + '\n'
	outCfgStr += '|-:|-:| ' + '\n'
	outCfgStr += '| Total Hash Rate        | {val:>25} | \n'.format(val=TOTAL_HASHRATE)
	outCfgStr += '| Honest Miner Hash Rate | {val:>25} | \n'.format(val=GetHashRate(False))
	outCfgStr += '| Attacker Hash Rate     | {val:>25} | \n'.format(val=GetHashRate(True))
	outCfgStr += '| Sample Hash Rate       | {val:>25} | \n'.format(val=GetHashRate(True, SAMPLE_HR))
	outCfgStr += '| Initial Diff           | {val:>25} | \n'.format(val=INIT_DIFFICULTY)
	outCfgStr += '| Max Number of Blocks   | {val:>25} | \n'.format(val=MAX_BLOCKN)
	outCfgStr += '| False Negative  Rate   | {val:>25} | \n'.format(val=SECURE_RATE)
	outCfgStr += '| Totoal Iterations      | {val:>25} | \n'.format(val=TOTAL_ITERATIONS)
	outCfgStr += '| Write Full Result      | {val:>25} | \n'.format(val=str(WRITE_FULL_RESULT))

	outCfgStr += '\n'

	# outCfgStr += '- **A**: ' + 'Attacker generates the blocks' + '\n'
	# outCfgStr += '- **B**: ' + 'Honest miner generates the blocks' + '\n'
	# outCfgStr += '- **C**: ' + 't < t_n' + '\n'

	# outCfgStr += '\n'

	print(outCfgStr)

	numBlockNeeded = []

	if WRITE_FULL_RESULT:
		outFullResStr = '## Full Test Results' + '\n'

	with progressbar.ProgressBar(max_value=TOTAL_ITERATIONS, **ProgBarConfig.PROGBAR_ARGS) as bar:
		for itCount in range(0, TOTAL_ITERATIONS):

			if WRITE_FULL_RESULT:
				outFullResStr += '- **Iteration {}** \n'.format(itCount)
				fullResIdent = '\t'
				outFullResStr += fullResIdent + '| | | Attacker | Honest Miner | Sample |' + '\n'
				outFullResStr += fullResIdent + '|:-|-:|-:|-:|-:|' + '\n'

			try:

				diff = INIT_DIFFICULTY
				pCAN = 1
				pCBN = 1
				pACN = 1
				pBCN = 1

				likelyASum = 0
				likelyBSum = 0

				CurrentAttackPoss = 1.0
				i = 0
				while (CurrentAttackPoss > SECURE_RATE) and (i < MAX_BLOCKN):

					attckerAvgBlockTime = GetAvgBlockTime(diff, GetHashRate(True))
					minerAvgBlockTime = GetAvgBlockTime(diff, GetHashRate(False))
					sampleAvgBlockTime = GetAvgBlockTime(diff, GetHashRate(True, SAMPLE_HR))

					blockTime = math.ceil(random.exponential(scale=sampleAvgBlockTime))

					# pCA = CalcPossTimeGivenAttacker(attckerAvgBlockTime, blockTime)
					# pCB = CalcPossTimeGivenMiner(minerAvgBlockTime, blockTime)
					# pAC = CalcPossAttackerGivenTime(pCA, pCB)
					# pBC = CalcPossMinerGivenTime(pCA, pCB)

					# pCAN = pCAN * pCA
					# pCBN = pCBN * pCB
					# pACN = CalcPossAttackerGivenTime(pCAN, pCBN)
					# pBCN = CalcPossMinerGivenTime(pCAN, pCBN)

					# outFullResStr += '- **Block ' + str(i) + str(':') + '**\n'
					# outFullResStr += fullResIdent + 'P(C|A)    :' + str(pCA) + '\n'
					# outFullResStr += fullResIdent + 'P(C|B)    :' + str(pCB) + '\n'
					# outFullResStr += fullResIdent + 'P(A|C)    :' + str(pAC) + '\n'

					# outFullResStr += '\n'

					# outFullResStr += fullResIdent + 'P(C|A)^N  :' + str(pCAN) + '\n'
					# outFullResStr += fullResIdent + 'P(C|B)^N  :' + str(pCBN) + '\n'

					# outFullResStr += '\n'

					likelyASum = likelyASum + np.log(CalcPdf(GetLambda(attckerAvgBlockTime),blockTime))
					likelyBSum = likelyBSum + np.log(CalcPdf(GetLambda(minerAvgBlockTime), blockTime))
					likelyArray = np.array([likelyASum, likelyBSum])
					likelyA, likelyB = np.exp(likelyArray - LogSumExp(likelyArray))
					CurrentAttackPoss = likelyA


					diff = GetNewDiff(diff, blockTime)
					diffChg = (diff - INIT_DIFFICULTY) / INIT_DIFFICULTY

					if WRITE_FULL_RESULT:
						outFullResStr += fullResIdent + '|  **Block {bIdx}** <br> (T<sub>sample</sub> = {bTime})  |'.format(
							bIdx = i,
							bTime = blockTime,
						) + '\n'
						outFullResStr += fullResIdent + '| | Avg Block Time | {aBT:20.5f} | {mBT:20.5f} | {sBT:20.5f} |'.format(
							aBT = attckerAvgBlockTime,
							mBT = minerAvgBlockTime,
							sBT = sampleAvgBlockTime,
						) + '\n'
						# outFullResStr += fullResIdent + '| | Lambda | {aBT:20.5f} | {mBT:20.5f} | |'.format(
						# 	aBT = GetLambda(attckerAvgBlockTime),
						# 	mBT = GetLambda(minerAvgBlockTime),
						# ) + '\n'
						# outFullResStr += fullResIdent + '| | PDF(T)         | {aBT:20.5f} | {mBT:20.5f} | |'.format(
						# 	aBT = CalcPdf(GetLambda(attckerAvgBlockTime), blockTime),
						# 	mBT = CalcPdf(GetLambda(minerAvgBlockTime), blockTime),
						# ) + '\n'
						# outFullResStr += fullResIdent + '| | LogSum(PDF(T)) | {aBT:20.5f} | {mBT:20.5f} | |'.format(
						# 	aBT = likelyASum,
						# 	mBT = likelyBSum,
						# ) + '\n'
						outFullResStr += fullResIdent + '| | Likelihood     | {aBT:>20} | {mBT:>20} | |'.format(
							aBT = '**{:.5e}**'.format(likelyA),
							mBT = '**{:.5e}**'.format(likelyB),
						) + '\n'

						outFullResStr += fullResIdent + '| | Diff Chg       | {:19.2f}% |'.format(
							diffChg * 100
						) + '\n'

					i += 1

				numBlockNeeded.append(i)

			except Exception as e:

				outErrStr += '{}'.format(e)
				outErrStr += '\n'

			bar.update(itCount)

	outSumResStr = '## Summarized Test Results' + '\n'
	outSumResStr += '| Iteration | # of Block Needed|' + '\n'
	outSumResStr += '|-:|-:|' + '\n'
	outSumResStr += '| {idx:>7} | {val:>10} |'.format(
		idx='Avg',
		val=sum(numBlockNeeded) / len(numBlockNeeded)
	) + '\n'
	outSumResStr += '| {idx:>7} | {val:>10} |'.format(
		idx='Max',
		val=max(numBlockNeeded)
	) + '\n'
	outSumResStr += '| {idx:>7} | {val:>10} |'.format(
		idx='Min',
		val=min(numBlockNeeded)
	) + '\n'
	outSumResStr += '| {idx:>7} | {val:>10} |'.format(
		idx='Mid',
		val=statistics.median(numBlockNeeded)
	) + '\n'
	for i in range(0, len(numBlockNeeded)):
		outSumResStr += '| {idx:>7} | {val:>10} |'.format(
			idx=i + 1,
			val=numBlockNeeded[i]
		) + '\n'
	outSumResStr += '\n'

	with open(OUTPUT_FILE_NAME, 'w') as file:
		file.write(outStr)
		file.write(outCfgStr)
		if len(outErrStr) > 0:
			outErrStr = '## Exceptions during test' + '\n' + outErrStr
		file.write(outErrStr)
		file.write(outSumResStr)
		if WRITE_FULL_RESULT:
			file.write(outFullResStr)

if __name__ == '__main__':
	exit(main())
