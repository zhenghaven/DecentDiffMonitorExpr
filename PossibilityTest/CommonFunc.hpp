#pragma once

#include "ConstParameters.hpp"

namespace EthExpr
{
	inline constexpr uint64_t DifficultyMin(double percentage)
	{
		return static_cast<uint64_t>(percentage * DIFFICULTY);
	}

	inline constexpr uint64_t AttackerHashrate(double percentage)
	{
		return static_cast<uint64_t>(percentage * TOTAL_HASHRATE);
	}

	inline constexpr double AttackerExpBlockTime(double percentage)
	{
		return DIFFICULTY / static_cast<double>(AttackerHashrate(percentage));
	}

	inline constexpr double ExpoDistLambda(uint64_t hashrate, uint64_t diff)
	{
		return static_cast<double>(hashrate) / diff;
	}

	inline constexpr double DiffChange(int64_t blockTime)
	{
		return 1 + ((9 - blockTime) / (18432.0));
	}

	constexpr size_t CaclJobPerThread(size_t totalJobs, size_t numOfThreads)
	{
		return (totalJobs / numOfThreads) +
			((totalJobs % numOfThreads) != 0 ? 1 : 0);
	}
}
