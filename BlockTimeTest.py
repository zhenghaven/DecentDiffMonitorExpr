import os
from datetime import datetime

import pandas      # python3 -m pip install pandas

class BlockTimeTest:

	def __init__(self,
		outputDir,
		btDataset,
		btDatasetPath,
		isBigOrder,
		count,
		unique):

		"""
		Construct a block time tester class.

		Args:
			outputDir       : The path to the output directory.
			btDataset       : The dataset that contains all historical
			                  time values, in Pandas object.
			btDatasetPath   : The path to the dataset that contains all
			                  historical block times.
			                  (optional, ignored if `btDataset` is not `None`)
			isBigOrder      : Is the result in biggest to small order?
			                  If not, the result will be in smallest to big order.
			count           : Number of top block time to record.
			unique          : Does the order needs to be unique?
		"""

		self.btDataset = btDataset if btDataset is not None else pandas.read_csv(btDatasetPath)

		self.outFileName = '{order}_{count}_blocktime_unique_{unique}.csv'.format(
			order='top' if isBigOrder is True else 'bottom',
			count=count,
			unique=unique)
		self.testName = self.outFileName

		self.outFile = open(os.path.join(outputDir, self.outFileName), 'w')
		self.outFile.write('\"Block_Number\",\"Block_Time\",\"Timestamp\"\n')
		self.outFile.flush()

		self.totalSteps = len(self.btDataset.index)
		self.currentStep = 0;

		self.FindPos2Insert = getattr(BlockTimeTest, 'FindPos2InsertBig') \
			if isBigOrder is True else \
				getattr(BlockTimeTest, 'FindPos2InsertSmall')
		self.unique  = unique
		self.count   = count
		self.records = list()

	def __del__(self):
		self.outFile.close()

	def FindPos2InsertBig(self, bNum, blocktime, time, insertAnyway):
		"""
		Find the position to insert the new values, in the list of records that
		is ordered from biggest to smaller values.

		Args:
			bNum         : block number.
			blocktime    : blocktime.
			time         : UNIX timestamp.
			insertAnyway : insert the value to the tail if the given value is
			               smaller than all values in the list.
		"""

		for i in range(len(self.records)):
			if self.unique is True and blocktime == self.records[i][0][1]:
				# unique is on, and we found a repeated items.
				# append to the position of other repeated items.
				timeReadable = datetime.fromtimestamp(time)
				self.records[i].append((bNum, blocktime, timeReadable))

				return (True, False) # (Inserted, Length unchanged)
			if blocktime >= self.records[i][0][1]:
				# [6, 5, 5, 4, 2, 1] [3]
				# [6, 5, 5, 4, 2, 1] [4]
				timeReadable = datetime.fromtimestamp(time)
				self.records = self.records[:i] + [[(bNum, blocktime, timeReadable)]] + self.records[i:]

				return (True, True) # (Inserted, Length changed)

		# we have iterated through all items
		if insertAnyway:
			# insert to the tail
			timeReadable = datetime.fromtimestamp(time)
			self.records.append([(bNum, blocktime, timeReadable)])

			return (True, True) # (Inserted, Length changed)
		else:
			return (False, False) # (No insertion, Length unchanged)

	def FindPos2InsertSmall(self, bNum, blocktime, time, insertAnyway):
		"""
		Find the position to insert the new values, in the list of records that
		is ordered from smallest to bigger values.

		Args:
			bNum         : block number.
			blocktime    : blocktime.
			time         : UNIX timestamp.
			insertAnyway : insert the value to the tail if the given value is
			               bigger than all values in the list.
		"""

		for i in range(len(self.records)):
			if self.unique is True and blocktime == self.records[i][0][1]:
				# unique is on, and we found a repeated items.
				# append to the position of other repeated items.
				timeReadable = datetime.fromtimestamp(time)
				self.records[i].append((bNum, blocktime, timeReadable))

				return (True, False) # (Inserted, Length unchanged)
			if blocktime <= self.records[i][0][1]:
				# [1, 2, 4, 5, 5, 6] [3]
				# [1, 2, 4, 5, 5, 6] [4]
				timeReadable = datetime.fromtimestamp(time)
				self.records = self.records[:i] + [[(bNum, blocktime, timeReadable)]] + self.records[i:]

				return (True, True) # (Inserted, Length changed)

		# we have iterated through all items
		if insertAnyway:
			# insert to the tail
			timeReadable = datetime.fromtimestamp(time)
			self.records.append([(bNum, blocktime, timeReadable)])

			return (True, True) # (Inserted, Length changed)
		else:
			return (False, False) # (No insertion, Length unchanged)

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
				bNum = block[bnumIndex]
				time = block[timeIndex]

				blockTime = time - prevTime

				# Compare
				if self.currentStep < 2:
					pass
				elif len(self.records) < self.count:
					self.FindPos2Insert(self, bNum, blockTime, time, True)
				else:
					insertRes = self.FindPos2Insert(self, bNum, blockTime, time, False)
					if insertRes[1] is True:
						self.records.pop()

				# Updates for the loop
				prevTime = time
				self.currentStep += 1
				#bar.update(self.currentStep)

			# Finished processing all blocks
			for l1 in self.records:
				for rec in l1:
					self.outFile.write('{bNum},{bTime},\"{time}\"\n'.format(
						bNum = rec[0],
						bTime= rec[1],
						time = rec[2]
					))
			self.outFile.write('\"#####TABLE_ENDS#####\"\n\n')
			self.outFile.flush()

		except:
			self.currentStep = self.totalSteps
			raise
