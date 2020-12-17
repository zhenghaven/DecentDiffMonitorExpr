import os
from datetime import datetime

import pandas      # python3 -m pip install pandas

ETH_EXPECTED_TIME = 20

class TesseractTest:

	def __init__(self,
		outputDir,
		btDataset,
		btDatasetPath,
		configList):

		"""
		Construct a Tesseract tester class.

		Args:
			outputDir       : The path to the output directory.
			btDataset       : The dataset that contains all historical
			                  time values, in Pandas object.
			btDatasetPath   : The path to the dataset that contains all
			                  historical block times.
			                  (optional, ignored if `btDataset` is not `None`)
			configList      : List of configuration in tuples (delta, skip N (0 for no skip)).
		"""

		self.btDataset = btDataset if btDataset is not None else pandas.read_csv(btDatasetPath)

		self.outFileName = 'Tesseract_blocktime.csv'
		self.testName = self.outFileName

		self.recList = [[d, int(d * ETH_EXPECTED_TIME), n, 0, 0] for (d, n) in configList]

		self.outFile = open(os.path.join(outputDir, self.outFileName), 'w')
		self.outFile.write('\"Delta\",\"Time_Limit\", \"N\",\"Counts\"\n')
		self.outFile.flush()

		self.totalSteps = len(self.btDataset.index)
		self.currentStep = 0;

	def __del__(self):
		self.outFile.close()

	def Begin(self):
		"""
		Start the test
		"""

		try:
			timeIndex = self.btDataset.columns.get_loc('Block_Time')

			self.currentStep = 0
			prevTime = 0

			#with progressbar.ProgressBar(max_value=self.totalSteps) as bar:
			for block in self.btDataset.itertuples(index=False):

				# Getting basic values
				time = block[timeIndex]

				blockTime = time - prevTime

				# Compare
				if self.currentStep < 2:
					pass
				else:
					for rec in self.recList:
						if rec[4] > 0:
							rec[4] -= 1
						elif blockTime > rec[1]:
							rec[3] += 1
							rec[4] = rec[2]

				# Updates for the loop
				prevTime = time
				self.currentStep += 1
				#bar.update(self.currentStep)

			# Finished processing all blocks
			for rec in self.recList:
				self.outFile.write('{delta},{timeLimit},{n},{count}\n'.format(
					delta     = rec[0],
					timeLimit = rec[1],
					n         = rec[2],
					count     = rec[3]
				))
			self.outFile.write('\"#####TABLE_ENDS#####\"\n\n')
			self.outFile.flush()

		except:
			self.currentStep = self.totalSteps
			raise
