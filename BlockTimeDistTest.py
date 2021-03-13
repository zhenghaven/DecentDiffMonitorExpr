import os
from datetime import datetime

import pandas      # python3 -m pip install pandas

class BlockTimeDistTest:

	def __init__(self,
		outputDir,
		btDataset,
		btDatasetPath,
		maxTime = 900):

		"""
		Construct a block time distribution tester class.

		Args:
			outputDir       : The path to the output directory.
			btDataset       : The dataset that contains all historical
			                  time values, in Pandas object.
			btDatasetPath   : The path to the dataset that contains all
			                  historical block times.
			                  (optional, ignored if `btDataset` is not `None`)
			maxTime         : Max block time to count; Any block time over this
			                  maximum limit will be kept in a single counter.
		"""

		self.btDataset = btDataset if btDataset is not None else pandas.read_csv(btDatasetPath)

		self.outFileName = 'blocktimedist_{maxTime}.csv'.format(
			maxTime=maxTime)
		self.testName = self.outFileName

		self.outFile = open(os.path.join(outputDir, self.outFileName), 'w')
		self.outFile.write('\"Block_Time\",\"Block_Count\"\n')
		self.outFile.flush()

		self.totalSteps = len(self.btDataset.index)
		self.currentStep = 0

		self.maxTime = maxTime
		self.countList = []
		for i in range(0, maxTime + 1):
			self.countList.append(0)
		self.overMaxCount = 0

	def __del__(self):
		self.outFile.close()

	def Begin(self):
		"""
		Start the test
		"""

		try:
			bnumIndex = self.btDataset.columns.get_loc('Block_Number')
			timeIndex = self.btDataset.columns.get_loc('Block_Time')

			self.currentStep = 0
			prevTime = 0
			#with progressbar.ProgressBar(max_value=self.totalSteps) as bar:
			for block in self.btDataset.itertuples(index=False):

				# Getting basic values
				#bNum = block[bnumIndex]
				time = int(block[timeIndex])

				blockTime = time - prevTime

				# Compare
				if self.currentStep < 2:
					pass
				else:
					if blockTime > self.maxTime:
						self.overMaxCount += 1
					else:
						self.countList[blockTime] += 1

				# Updates for the loop
				prevTime = time
				self.currentStep += 1
				#bar.update(self.currentStep)

			# Finished processing all blocks
			for i in range(0, self.maxTime + 1):
				self.outFile.write('{bTime},{count}\n'.format(
					bTime= i,
					count = self.countList[i]
				))
			self.outFile.write('"{bTime}+",{count}\n'.format(
				bTime= self.maxTime,
				count = self.overMaxCount
			))
			self.outFile.write('\"#####TABLE_ENDS#####\"\n\n')
			self.outFile.flush()

		except:
			self.currentStep = self.totalSteps
			raise
