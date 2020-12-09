import os
from datetime import datetime

import pandas      # python3 -m pip install pandas
import progressbar # python3 -m pip install progressbar2

import DiffMon

class DiffMonTest:

	def __init__(self,
		outputDir,
		diffDataset,
		diffDatasetPath,
		chkptSize,
		maxDiffDrop,
		maxWaitTime,
		waitTimeEnable,
		restartAppr):

		"""
		Construct a difficulty monitor tester class.

		Args:
			outputDir       : The path to the output directory.
			diffDataset     : The dataset that contains all historical
			                  block difficulty values and block times,
			                  in Pandas object.
			diffDatasetPath : The path to the dataset that contains all
			                  historical block difficulty values and block times.
			                  (optional, ignored if `diffDataset` is not `None`)
			chkptSize       : Checkpoint size.
			maxDiffDrop     : Maximum difficulty drop allowed, in percentage.
			maxWaitTime     : Maximum wait time.
			waitTimeEnable  : Do we want to enable maximum wait time or not?
			restartAppr     : Approach of restart process.
			                  Integer begin from 1.
			                  Currently there're two different approaches.
		"""

		self.diffDataset = diffDataset if diffDataset is not None else pandas.read_csv(diffDatasetPath)

		self.diffMon = DiffMon.DiffMon(chkptSize,
						maxDiffDrop,
						maxWaitTime,
						waitTimeEnable,
						restartAppr)

		self.outFileName = 'chkpt_{chkpt}_maxdrop_{maxdrop}_maxwait_{maxwait}_wait_{wait}_rs_{rs}.csv'.format(
			chkpt=chkptSize,
			maxdrop=maxDiffDrop,
			maxwait=maxWaitTime,
			wait=waitTimeEnable,
			rs=restartAppr)
		self.testName = self.outFileName

		self.outFile = open(os.path.join(outputDir, self.outFileName), 'w')
		self.outFile.write('\"Block_Number\",\"Block_Time\",\"Timestamp\",\"Diff_Ref\",\"Diff_Drop\",\"BTime_Shutdown\",\"Diff_Shutdown\",\"Checkpt_Start\",\"Checkpt_End\",\"Ref_BlockNum\",\"At_Checkpt\"\n')
		self.outFile.flush()

		# Number of shutdown we found
		self.shutdownCount = 0
		self.btShutdownCount = 0
		self.dfShutdownCount = 0

		self.totalSteps = len(self.diffDataset.index)
		self.currentStep = 0;
		self.maxDiffDrop = 0;

	def __del__(self):
		self.outFile.close()

	def Begin(self):
		"""
		Start the test
		"""

		try:
			bnumIndex = self.diffDataset.columns.get_loc('Block_Number')
			timeIndex = self.diffDataset.columns.get_loc('Block_Time')
			diffIndex = self.diffDataset.columns.get_loc('Difficulty')

			self.currentStep = 0
			prevTime = 0
			#with progressbar.ProgressBar(max_value=self.totalSteps) as bar:
			for block in self.diffDataset.itertuples(index=False):

				# Getting basic values
				bNum = block[bnumIndex]
				time = block[timeIndex]
				diff = block[diffIndex]

				blockTime = time - prevTime

				# Send to difficulty monitor
				res = self.diffMon.Update(bNum, diff, blockTime)
				if res is not None:

					# Count num of shutdowns
					self.shutdownCount += 1
					if res[2] is True:
						self.btShutdownCount += 1
					elif res[3] is True:
						self.dfShutdownCount += 1

					# check max drop
					if res[1] < self.maxDiffDrop:
						self.maxDiffDrop = res[1]

					timeReadable = datetime.fromtimestamp(time)
					self.outFile.write('{bNum},{bTime},\"{time}\",{diffRef},{diffDrop},{btDown},{dfDown},{chkpt_s},{chkpt_e},{ref_bnum},{chkpt_pos}\n'.format(
						bNum    = bNum,
						bTime   = blockTime,
						time    = str(timeReadable),
						diffRef = res[0],
						diffDrop= res[1],
						btDown  = res[2],
						dfDown  = res[3],
						chkpt_s = res[4],
						chkpt_e = res[5],
						ref_bnum= res[6],
						chkpt_pos=self.diffMon.chkptCount))

				# Updates for the loop
				prevTime = time

				self.currentStep += 1
				#bar.update(self.currentStep)

			# Finished processing all blocks
			self.outFile.write('\"#####TABLE_ENDS#####\"\n\n')
			# output summary
			self.outFile.write('\"Num of Shutdown: {shutdownCount}\"\n'.format(shutdownCount=self.shutdownCount))
			self.outFile.write('\"Max Diff. Drop : {maxDiffDrop}\"\n'.format(maxDiffDrop=self.maxDiffDrop))
			self.outFile.write('\"Num of Chkpts  : {chkptCount}\"\n'.format(chkptCount=self.diffMon.chkptCount))
			self.outFile.write('\n')
			self.outFile.write('\"Num of BlockTime  Shutdown: {shutdownCount}\"\n'.format(shutdownCount=self.btShutdownCount))
			self.outFile.write('\"Num of Difficulty Shutdown: {shutdownCount}\"\n'.format(shutdownCount=self.dfShutdownCount))
			self.outFile.flush()

		except:
			self.currentStep = self.totalSteps
			raise
