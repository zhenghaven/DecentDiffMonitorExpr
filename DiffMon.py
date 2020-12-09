import statistics

class DiffMon:

	def __init__(self,
		chkptSize,
		maxDiffDrop,
		maxWaitTime,
		waitTimeEnable,
		restartAppr):

		"""
		Construct a difficulty monitor class.

		Args:
			chkptSize     : Checkpoint size.
			maxDiffDrop   : Maximum difficulty drop allowed, in percentage.
			maxWaitTime   : Maximum wait time.
			waitTimeEnable: Do we want to enable maximum wait time or not?
			restartAppr   : Approach of restart process.
			                Integer begin from 1.
			                Currently there're two different approaches.
		"""

		self.chkptSize      = chkptSize
		self.maxDiffDrop    = maxDiffDrop / 100.00
		self.maxWaitTime    = maxWaitTime
		self.waitTimeEnable = waitTimeEnable
		self.restartAppr    = restartAppr

		self.restartFunc = [
			getattr(DiffMon, 'RestartApproach1'),
			getattr(DiffMon, 'RestartApproach2'),
		]

		# A list of difficulty values from previous checkpoint window
		self.prevChkDiff = []

		# A list of difficulty values for the next checkpoint window
		self.candChkDiff = []

		# median value of previous checkpoint window
		self.diffRef = None

		# Number of checkpoints we have tested
		self.chkptCount = 0

		# Number of shutdown we found
		self.shutdownCount = 0
		self.btShutdownCount = 0
		self.dfShutdownCount = 0

	def RestartApproach1(self):
		"""
		Restart Approach 1: Extend the previous checkpoint window, and get the
		new median value.
		(Internally used method)
		"""

		self.prevChkDiff = self.prevChkDiff + self.candChkDiff
		self.diffRef     = statistics.median(self.prevChkDiff)

	def RestartApproach2(self):
		"""
		Restart Approach 2: Use the faulty block diff value as the new reference.
		(Internally used method)
		"""

		self.diffRef = self.candChkDiff[len(self.candChkDiff) - 1]

	def Restart(self):
		"""
		Decide which restart approach to take, and call that method.
		(Internally used method)
		"""
		self.restartFunc[self.restartAppr - 1](self)

	def Init(self, diffVal):
		"""
		Initialize the difficulty monitor during the time when the first checkpoint
		window hasn't been filled yet. (Internally used method)
		"""
		self.prevChkDiff.append(diffVal)

		if len(self.prevChkDiff) == self.chkptSize:
			self.diffRef = statistics.median(self.prevChkDiff)
			self.chkptCount += 1

	def Update(self, diffVal, blockTime):
		"""
		Give a new block info to difficulty monitor for processing.

		Args:
			diffVal   : Difficulty value of the new block.
			blockTime : Block time of new block.
		"""
		# make sure there are enough difficulty values in previous checkpoint
		# (This is unique in experiment code)
		if len(self.prevChkDiff) < self.chkptSize:
			self.Init(diffVal)
			return None

		btShutdown = False
		dfShutdown = False

		# Check block time
		if self.waitTimeEnable and blockTime > self.maxWaitTime:
			btShutdown = True
			self.btShutdownCount += 1

		# Check Diff Drop
		diffDelta = (diffVal - self.diffRef) / float(self.diffRef)
		if diffDelta < 0:
			absDiffDelta = -diffDelta
			if absDiffDelta > self.maxDiffDrop:
				dfShutdown = True
				self.dfShutdownCount += 1

		# Add new diff value to next checkpoint window
		self.candChkDiff.append(diffVal)

		# Prepare return results
		res = None
		if btShutdown or dfShutdown:
			# there was a shutdown
			# return [Diff_Ref, Diff_Drop, btShutdown, dfShutdown]
			res = [self.diffRef, diffDelta * 100.0, btShutdown, dfShutdown]
			self.shutdownCount += 1

		# Should we switch to the next checkpoint window?
		if len(self.candChkDiff) == self.chkptSize:
			self.prevChkDiff, self.candChkDiff = self.candChkDiff, self.prevChkDiff
			self.candChkDiff = []
			self.diffRef = statistics.median(self.prevChkDiff)
			self.chkptCount += 1

		# Should we take the special restart routine?
		# (shutdowns right on checkpoint do not need special restart routine)
		# (shutdowns caused by block time do not need to special restart routine)
		elif dfShutdown:
			self.Restart()

		return res
