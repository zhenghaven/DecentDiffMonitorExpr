#include <cmath>
#include <cstdint>

#include <array>
#include <vector>
#include <thread>
#include <fstream>
#include <iostream>
#include <algorithm>

#include "ConstParameters.hpp"
#include "CommonFunc.hpp"

namespace
{
	//static constexpr uint64_t ETH_MAX_DIFFICULTY     = 8447394615662442;
	static constexpr uint64_t ETH_MAX_DIFFICULTY     = 9000000000000000;
	static constexpr uint64_t ETH_DIFF_1DPREC_ENDS   =       1000000000;
	static constexpr uint64_t ETH_DIFF_1DPREC_MAX    = ETH_MAX_DIFFICULTY / ETH_DIFF_1DPREC_ENDS;

#ifdef USE_ATTACK_BLOCK_LUT
	static constexpr uint64_t ETH_DIFF_2DPREC_ENDS   =      10000000000;
	static constexpr uint64_t ETH_DIFF_2DPREC_MAX    = ETH_MAX_DIFFICULTY / ETH_DIFF_2DPREC_ENDS;
#endif

	size_t gs_totalLutSize = 0;
}

#ifdef USE_ATTACK_BLOCK_LUT
void InitLutAttBloc(std::vector<std::vector<double> >& lutPosAttBlock, size_t maxWaitTime)
{
	lutPosAttBlock.resize(maxWaitTime);

	for (int i = 0; i < lutPosAttBlock.size(); ++i)
	{
		lutPosAttBlock[i].resize(ETH_DIFF_2DPREC_MAX);

		gs_totalLutSize += ETH_DIFF_2DPREC_MAX * sizeof(*lutPosAttBlock[i].data());
	}
}
#endif

void InitLutAttSucc(std::array<std::vector<double>, 2>& lutPosSucc)
{
	lutPosSucc[0].resize(ETH_DIFF_1DPREC_MAX);
	gs_totalLutSize += ETH_DIFF_1DPREC_MAX * sizeof(*lutPosSucc[0].data());
	lutPosSucc[1].resize(ETH_DIFF_1DPREC_MAX);
	gs_totalLutSize += ETH_DIFF_1DPREC_MAX * sizeof(*lutPosSucc[1].data());
}

void FillLutDiffChg(std::vector<double>& lutDiffChg)
{
	for (size_t i = 0; i < lutDiffChg.size(); ++i)
	{
		lutDiffChg[i] = EthExpr::DiffChange(i + 1);
	}
	gs_totalLutSize += lutDiffChg.size() * sizeof(*lutDiffChg.data());
}

double cdf(double lmd, uint64_t x)
{
	double p = -1 * lmd * x;
	double res = 1 - std::exp(p);
	return res;
}

double PosAttBloc(size_t blockTime, uint64_t diff, uint64_t hashRate)
{
	double lmd = EthExpr::ExpoDistLambda(hashRate, diff);
	double p1 = cdf(lmd, blockTime);
	double p0 = cdf(lmd, blockTime - 1);
	return p1 - p0;
}

#ifdef USE_ATTACK_BLOCK_LUT
void FillLutAttBloc(size_t beginLine, size_t endLine, uint64_t hashRate, std::vector<std::vector<double> >& lutPosAttBlock)
{
	for (size_t i = beginLine; i < endLine; ++i)
	{
		for (uint64_t j = 0; j < ETH_DIFF_2DPREC_MAX; ++j)
		{
			size_t blockTime = i + 1;
			uint64_t diff = (j + 1) * ETH_DIFF_2DPREC_ENDS;

			lutPosAttBlock[i][j] = PosAttBloc(blockTime, diff, hashRate);
		}
	}
}

void FillLutAttBlocThreads(uint64_t hashRate, size_t maxWaitTime, std::vector<std::vector<double> >& lutPosAttBlock, size_t maxNumOfThreads)
{
	std::vector<std::thread> ths;
	ths.reserve(maxNumOfThreads);

	size_t totalJobs = maxWaitTime;
	size_t step = EthExpr::CaclJobPerThread(totalJobs, maxNumOfThreads);

	for (size_t i = 0; i < maxNumOfThreads; ++i)
	{
		size_t beginLine = i * step;

		if (beginLine < totalJobs)
		{
			size_t left = totalJobs - beginLine;
			size_t endLine = left > step ? (beginLine + step) : (beginLine + left);

			//std::cout << "DEBUG: (" << beginLine << ", " << endLine << ")" << std::endl;
			ths.emplace_back(
				[beginLine, endLine, hashRate, &lutPosAttBlock]()
				{
					FillLutAttBloc(beginLine, endLine, hashRate, lutPosAttBlock);
				}
			);
		}
	}

	for (auto& t : ths)
	{
		t.join();
	}
}

double PosAttackerBlock(int64_t blockTime, uint64_t diff, const std::vector<std::vector<double> >& lutPosAttBlock)
{
	uint64_t diffLowPrec = diff / ETH_DIFF_2DPREC_ENDS;
	if (diffLowPrec == 0 || diffLowPrec > ETH_DIFF_2DPREC_MAX)
	{
		throw std::out_of_range("The difficulty value is out of range of LUT.");
	}

	return lutPosAttBlock[blockTime - 1][diffLowPrec - 1];
}
#endif

void FillLutAttSucc(size_t beginRow, size_t endRow, std::array<std::vector<double>, 2>& lutPosAttSucc, uint64_t diffMin)
{
	for (uint64_t j = beginRow; j < endRow; ++j)
	{
		uint64_t diff = (j + 1) * ETH_DIFF_1DPREC_ENDS;

		if (diffMin > diff)
		{
			lutPosAttSucc[0][j] = 0.0;
		}
		else
		{
			lutPosAttSucc[0][j] = 1.0;
		}
	}
}

void FillLutAttSuccThreads(std::array<std::vector<double>, 2>& lutPosAttSucc, uint64_t diffMin, size_t maxNumOfThreads)
{
	std::vector<std::thread> ths;
	ths.reserve(maxNumOfThreads);

	constexpr size_t totalJobs = ETH_DIFF_1DPREC_MAX;
	size_t step = EthExpr::CaclJobPerThread(totalJobs, maxNumOfThreads);

	for (size_t i = 0; i < maxNumOfThreads; ++i)
	{
		size_t begin = i * step;

		if (begin < totalJobs)
		{
			size_t left = totalJobs - begin;
			size_t end = left > step ? (begin + step) : (begin + left);

			//std::cout << "DEBUG: (" << begin << ", " << end << ")" << std::endl;
			ths.emplace_back(
				[begin, end, &lutPosAttSucc, diffMin]()
				{
					FillLutAttSucc(begin, end, lutPosAttSucc, diffMin);
				}
			);
		}
	}

	for (auto& t : ths)
	{
		t.join();
	}
}

uint64_t DiffNext(uint64_t diff, int64_t blockTime, const std::vector<double>& lutDiffChg)
{
	return static_cast<uint64_t>(diff * lutDiffChg[blockTime - 1]);
	//return static_cast<uint64_t>(diff * EthExpr::DiffChange(blockTime));
}

void PosAttSucc(size_t beginRow, size_t endRow, std::array<std::vector<double>, 2>& lutPosAttSucc, uint64_t& prevUpperBound, uint64_t diffMin, uint64_t attHashRate, size_t maxWaitTime, const std::vector<std::vector<double> >& lutPosAttBlock, const std::vector<double>& lutDiffChg)
{
	int test = 1;
	uint64_t currUpperBound = 0;
	for (uint64_t j = beginRow; j < endRow && currUpperBound == 0; ++j)
	{
		uint64_t diff = (j + 1) * ETH_DIFF_1DPREC_ENDS;

		if (j == 0 || j == 10000 || j == 283729 || j == 293729 ||
			diff > ETH_MAX_DIFFICULTY) // 700ms
		{
			test = test + 1;
		}

		if (diffMin > diff)
		{
			lutPosAttSucc[1][j] = 0.0;
		}
		else
		{
			double res = 0.0;

			for (size_t i = 0; i < maxWaitTime; ++i)
			{
				size_t blockTime = i + 1;
				uint64_t diffNext = DiffNext(diff, i + 1, lutDiffChg);
				size_t diffNextIdx = diffNext / ETH_DIFF_1DPREC_ENDS;
				if (diffNextIdx >= prevUpperBound)
				{
					currUpperBound = j;
				}
				else
				{
#ifdef USE_ATTACK_BLOCK_LUT
					//res += (lutPosAttBlock[i][(diff / ETH_DIFF_2DPREC_ENDS) - 1] * lutPosAttSucc[0][diffNextIdx]);
					res += (PosAttackerBlock(blockTime, diff, lutPosAttBlock) * lutPosAttSucc[0][diffNextIdx]);
#else
					res += (PosAttBloc(blockTime, diff, attHashRate) * lutPosAttSucc[0][diffNextIdx]);
#endif
				}
			}

			lutPosAttSucc[1][j] = res;
		}
	}

	prevUpperBound = (currUpperBound == 0) ? prevUpperBound : currUpperBound;
}

void PosAttSuccThreads(std::array<std::vector<double>, 2>& lutPosAttSucc, uint64_t& prevUpperBound, uint64_t diffMin, uint64_t attHashRate, size_t maxWaitTime, const std::vector<std::vector<double> >& lutPosAttBlock, const std::vector<double>& lutDiffChg, size_t maxNumOfThreads)
{
	std::vector<std::thread> ths;
	ths.reserve(maxNumOfThreads);
	std::vector<uint64_t> upperBounds(maxNumOfThreads, prevUpperBound);

	constexpr size_t totalJobs = ETH_DIFF_1DPREC_MAX;
	size_t step = EthExpr::CaclJobPerThread(totalJobs, maxNumOfThreads);

	for (size_t i = 0; i < maxNumOfThreads; ++i)
	{
		size_t begin = i * step;

		if (begin < totalJobs)
		{
			size_t left = totalJobs - begin;
			size_t end = left > step ? (begin + step) : (begin + left);

			//std::cout << "DEBUG: (" << begin << ", " << end << ")" << std::endl;
			ths.emplace_back(
				[i, begin, end, &lutPosAttSucc, &upperBounds, diffMin, attHashRate, maxWaitTime, &lutPosAttBlock, &lutDiffChg]()
				{
					PosAttSucc(begin, end, lutPosAttSucc, upperBounds[i], diffMin, attHashRate, maxWaitTime, lutPosAttBlock, lutDiffChg);
				}
			);
		}
	}

	for (auto& t : ths)
	{
		t.join();
	}

	lutPosAttSucc[0].swap(lutPosAttSucc[1]);
	prevUpperBound = *std::min_element(upperBounds.begin(), upperBounds.end());
}

void WriteResult(const std::string& fileName, const std::vector<double>& poss)
{
	std::ofstream file;
	file.open(fileName);
	file.precision(std::numeric_limits<double>::max_digits10);

	try
	{
		file << "Num_Of_Block,Possibility\n";

		for (size_t i = 0; i < poss.size(); ++i)
		{
			file << i + 1 << "," << poss[i] << "\n";
		}
	}
	catch (...)
	{
		file.close();
		throw;
	}

	file.close();
}

int main()
{
	std::cout.precision(std::numeric_limits<double>::max_digits10);

	constexpr size_t maxWaitTime     = 900;
	constexpr size_t maxNumOfThreads = 32;
	constexpr size_t maxNumOfBlock   = 1500;
	constexpr char const outFile[]   = "DynTestResult.csv";

	constexpr double aHashPer   = 0.3; // <- The percentage of total hashrate controlled by attacker.
	constexpr double diffMinPer = 0.8; // <- The percentage of minimum level of difficulty value that is allowed to drop to.

	std::cout << "INFO: " << "Network  Totoal Hashrate: " << EthExpr::TOTAL_HASHRATE             << std::endl;
	std::cout << "INFO: " << "Attacker Hashrate       : " << EthExpr::AttackerHashrate(aHashPer) << std::endl;

	std::cout << "INFO: " << "Network  Expected BlockTime: " << EthExpr::EXP_BLOCK_TIME                 << std::endl;
	std::cout << "INFO: " << "Attacker Expected BlockTime: " << EthExpr::AttackerExpBlockTime(aHashPer) << std::endl;

	std::cout << "INFO: " << "Network Difficulty         : " << EthExpr::DIFFICULTY                << std::endl;
	std::cout << "INFO: " << "Difficulty Min             : " << EthExpr::DifficultyMin(diffMinPer) << std::endl;
	std::cout << "INFO: " << "Difficulty Max             : " << ETH_MAX_DIFFICULTY                 << std::endl;

	const uint64_t ethCalcMaxDifficulty = static_cast<uint64_t>(EthExpr::DIFFICULTY * std::pow((1 + ((9 - 1) / (18432.0))), maxNumOfBlock));
	//const uint64_t ethCalcMinDifficulty = static_cast<uint64_t>(ETH_DIFFICULTY * std::pow((1 + ((9 - static_cast<int64_t>(ETH_MAX_WAIT_TIME)) / (18432.0))), maxNumOfBlock));

	//std::cout << "INFO: " << "Difficulty Min (Calculated): " << ethCalcMinDifficulty << std::endl;
	std::cout << "INFO: " << "Difficulty Max (Calculated): " << ethCalcMaxDifficulty << std::endl;

	if (EthExpr::DifficultyMin(diffMinPer) < ETH_DIFF_1DPREC_ENDS
#ifdef USE_ATTACK_BLOCK_LUT
		|| EthExpr::DifficultyMin(diffMinPer) < ETH_DIFF_2DPREC_ENDS
#endif
		)
	{
		throw std::range_error("The difficulty value could be smaller than the smallest value we can represent in our difficulty precision.");
	}

	if (ethCalcMaxDifficulty > ETH_MAX_DIFFICULTY)
	{
		throw std::range_error("The difficulty value could be larger than the biggest value we can represent in our difficulty precision.");
	}

	std::cout << "INFO: " << "Difficulty Ignored Digits (1D): " << ETH_DIFF_1DPREC_ENDS << std::endl;
#ifdef USE_ATTACK_BLOCK_LUT
	std::cout << "INFO: " << "Difficulty Ignored Digits (2D): " << ETH_DIFF_2DPREC_ENDS << std::endl;
#endif

	std::vector<double> lutDiffChgInc(maxWaitTime);
	FillLutDiffChg(lutDiffChgInc);

	std::vector<std::vector<double> >  lutPosAttBlock;
#ifdef USE_ATTACK_BLOCK_LUT
	InitLutAttBloc(lutPosAttBlock, maxWaitTime);
#endif

	std::array<std::vector<double>, 2> lutPosSucc;
	InitLutAttSucc(lutPosSucc);

	std::cout << "DEBUG: " << "LUT total size: " << (((gs_totalLutSize / 1024.0) / 1024)) / 1024 << "GB" << std::endl;

#ifdef USE_ATTACK_BLOCK_LUT
	FillLutAttBlocThreads(EthExpr::AttackerHashrate(aHashPer), maxWaitTime, lutPosAttBlock, maxNumOfThreads);

	double testDlb = 0.0;
	for (size_t i = 0; i < maxWaitTime; ++i)
	{
		testDlb += PosAttackerBlock(i + 1, EthExpr::DIFFICULTY, lutPosAttBlock);
	}
	std::cout << "DEBUG: " << "CDF(X <= 900, current diff): " << testDlb << std::endl;

	std::cout << std::endl;
#endif

	FillLutAttSuccThreads(lutPosSucc, EthExpr::DifficultyMin(diffMinPer), maxNumOfThreads);

	size_t i = 0;
	for (; i < ETH_DIFF_1DPREC_MAX && lutPosSucc[0][i] == 0.0; ++i)
	{}
	std::cout << "DEBUG: " << "Difficulty Min            : " << i * ETH_DIFF_1DPREC_ENDS << std::endl;
	if (i != EthExpr::DifficultyMin(diffMinPer) / ETH_DIFF_1DPREC_ENDS)
	{
		throw std::runtime_error("FillLutAttSucc Error.");
	}
	for (; i < ETH_DIFF_1DPREC_MAX; ++i)
	{
		if (lutPosSucc[0][i] < 1.0)
		{
			throw std::runtime_error("FillLutAttSucc Error.");
		}
	}
	
	uint64_t diffUpperBound = ETH_MAX_DIFFICULTY / ETH_DIFF_1DPREC_ENDS;
	std::vector<double> resList(maxNumOfBlock, 0.0);
	for (size_t i = 0; i < maxNumOfBlock; ++i)
	{
		PosAttSuccThreads(lutPosSucc, diffUpperBound, EthExpr::DifficultyMin(diffMinPer), EthExpr::AttackerHashrate(aHashPer), maxWaitTime, lutPosAttBlock, lutDiffChgInc, maxNumOfThreads);

		size_t diffIdx = EthExpr::DIFFICULTY / ETH_DIFF_1DPREC_ENDS;
		if (diffIdx > diffUpperBound)
		{
			throw std::runtime_error("PosAttSuccThreads Error.");
		}

		resList[i] = lutPosSucc[0][diffIdx];
		std::cout << "INFO: " << "PosAttackerSuccess(N=" << i + 1 << "): " << resList[i] << std::endl;
	}

	WriteResult(outFile, resList);

	return 0;
}
