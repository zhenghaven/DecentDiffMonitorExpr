#include <cmath>
#include <ctime>
#include <cstring>
#include <cstdint>

#include <array>
#include <vector>
#include <string>

#include <iomanip>
#include <fstream>
#include <sstream>
#include <iostream>

#include <chrono>
#include <thread>
#include <random>
#include <algorithm>
#include <functional>

#include "ConstParameters.hpp"
#include "CommonFunc.hpp"

namespace
{
	static constexpr std::array<uint8_t, 400> PRESET_SEEDS {
		0x0e, 0x36, 0xd0, 0x75, 0xb4, 0x59, 0x1d, 0xbf, 0xc2, 0x17, 0xae, 0xa0, 0x09, 0x21, 0x62, 0x74, 0x30, 0x2f, 0xbb, 0x62, 0x06, 0xec, 0x82, 0x55, 0x8e, 0x4c, 0xca, 0x78, 0x31, 0xac, 0x54, 0x83,
		0x01, 0x26, 0xa2, 0x24, 0x44, 0x0a, 0x42, 0xc7, 0x1f, 0xab, 0xf9, 0x40, 0x00, 0xb3, 0xb0, 0xb2, 0x68, 0xa3, 0xfd, 0xf8, 0xc6, 0xd1, 0x54, 0x0d, 0xe6, 0xc5, 0xac, 0xbf, 0x09, 0x70, 0x8e, 0x42,
		0x93, 0x20, 0xb1, 0x9c, 0xaf, 0x4e, 0xea, 0xba, 0x6f, 0x34, 0x31, 0xfc, 0x7e, 0x87, 0x19, 0x72, 0xd2, 0x58, 0xe6, 0x70, 0x84, 0xb5, 0xf3, 0x9e, 0x9f, 0xc0, 0x03, 0x1c, 0xc1, 0xba, 0xa0, 0xf9,
		0x88, 0x69, 0x8a, 0x63, 0x08, 0x79, 0x08, 0x7b, 0xac, 0x19, 0xa4, 0x01, 0xb1, 0x9c, 0x2c, 0xe3, 0xa4, 0xf3, 0x3d, 0xb9, 0xd7, 0x6b, 0x82, 0xbc, 0xbd, 0xf4, 0xf2, 0x86, 0x56, 0xd5, 0xbd, 0x3c,
		0x46, 0x08, 0xa8, 0xad, 0x0c, 0xfc, 0x40, 0x7d, 0xba, 0x1f, 0xd6, 0x49, 0x4d, 0x3d, 0x0f, 0xf0, 0xbe, 0xa1, 0x63, 0x82, 0x7f, 0xd9, 0xf6, 0x27, 0x18, 0xa1, 0xb0, 0xac, 0xf3, 0x6d, 0x0b, 0x9c,
		0x8f, 0x20, 0x89, 0x06, 0x18, 0x03, 0x4a, 0x33, 0x44, 0xbd, 0x34, 0x76, 0x2b, 0x6a, 0x7e, 0x53, 0x00, 0x60, 0xba, 0xa4, 0x0d, 0x7c, 0x5f, 0x65, 0x77, 0xd9, 0x33, 0xb4, 0x2c, 0x25, 0x1b, 0x8e,
		0x06, 0x9a, 0x8f, 0x1a, 0x0a, 0xf3, 0xe0, 0xcb, 0x5c, 0xe7, 0x4f, 0xed, 0x24, 0x7a, 0xd6, 0x97, 0x5a, 0x5c, 0x95, 0x1b, 0x2e, 0x00, 0x8c, 0xfd, 0x90, 0x16, 0xd7, 0xbd, 0x89, 0x2a, 0xf0, 0x9d,
		0x22, 0xe4, 0x7d, 0x93, 0x35, 0x2a, 0xdb, 0x84, 0x7c, 0x6e, 0xca, 0xd1, 0xdf, 0xc6, 0x5d, 0x30, 0x4c, 0x08, 0x54, 0x5a, 0x79, 0x9c, 0x11, 0x48, 0x3e, 0xf9, 0x91, 0x6d, 0xd2, 0x9d, 0x33, 0x2d,
		0x4d, 0x32, 0xb6, 0x82, 0x3a, 0x3a, 0x2a, 0x96, 0xfa, 0xea, 0x56, 0x00, 0xc5, 0xc2, 0x2c, 0x8a, 0x35, 0x04, 0x84, 0xaa, 0x38, 0xc2, 0x68, 0x8c, 0xff, 0x13, 0x9f, 0x9c, 0x2d, 0x3c, 0x13, 0x6a,
		0x0a, 0xb8, 0x9e, 0xff, 0x4a, 0xde, 0x93, 0xd9, 0x43, 0x09, 0x6a, 0x5a, 0x01, 0x30, 0xaa, 0x88, 0x49, 0xa1, 0xa8, 0xf2, 0x36, 0x01, 0xd7, 0x16, 0x0b, 0xf1, 0x77, 0xcf, 0x8a, 0xcb, 0xdc, 0x7b,
		0xbb, 0x53, 0x51, 0xca, 0x23, 0x7c, 0x35, 0x82, 0x57, 0x92, 0xb9, 0x82, 0x1d, 0x09, 0x3f, 0x49, 0xf5, 0x94, 0x3c, 0x10, 0xc5, 0x34, 0x60, 0xbf, 0x35, 0xf0, 0xd7, 0x5e, 0x29, 0x83, 0x2f, 0x04,
		0x80, 0x8d, 0x00, 0x53, 0xcb, 0xa6, 0xf6, 0x50, 0x20, 0xc9, 0x23, 0xee, 0x19, 0xc1, 0xdb, 0x4f, 0x9e, 0xe6, 0x37, 0x4c, 0xfa, 0x69, 0xec, 0x09, 0x3a, 0xfc, 0x52, 0xb1, 0x5f, 0xdc, 0xc4, 0xa0,
		0xfc, 0x46, 0xe4, 0xb9, 0x19, 0x57, 0xa5, 0x0b, 0x65, 0xd4, 0x05, 0xce, 0x9a, 0x79, 0x16, 0x32,
	};

	using SeedType  = uint32_t;
	using RandEng = std::mt19937;

	static_assert(sizeof(SeedType) == sizeof(std::random_device::result_type), "Random number must in the same type.");
	//static_assert(sizeof(SeedType) == sizeof(RandEng::result_type), "Random number must in the same type.");

	static constexpr size_t MAX_NUM_OF_THREAD_CAP = 50;
}

void MCSimulate(uint64_t diff, uint64_t diffMin, uint64_t aHashR, int64_t maxWaitTime, size_t numOfBlock, size_t round, RandEng& randEng, std::vector<size_t>& counts)
{
	counts.resize(numOfBlock);
	std::vector<uint64_t> diffs(numOfBlock + 1);
	diffs[0] = diff;

	int64_t blockTime = 0;
	bool    detected = false;
	for (size_t r = 0; r < round; ++r)
	{
		detected = false;
		for (size_t i = 0; (i < numOfBlock) && !detected; ++i)
		{
			std::exponential_distribution<double> expoDist(EthExpr::ExpoDistLambda(aHashR, diffs[i]));
			blockTime = static_cast<int64_t>(expoDist(randEng)) + 1;

			diffs[i + 1] = static_cast<uint64_t>(diffs[i] * EthExpr::DiffChange(blockTime));

			if (blockTime > maxWaitTime ||
				diffs[i + 1] <= diffMin)
			{
				detected = true;
			}
			else
			{
				counts[i]++;
			}
		}
	}
}

std::vector<size_t> MCSimulateThreads(uint64_t diff, uint64_t diffMin, uint64_t aHashR, int64_t maxWaitTime, size_t numOfBlock, size_t round, std::vector<RandEng>& randEngs, size_t numOfThreads)
{
	size_t totalJobs = round;
	size_t step = EthExpr::CaclJobPerThread(totalJobs, numOfThreads);

	std::vector<std::thread> ths;
	ths.reserve(numOfThreads);

	std::vector<std::vector<size_t> > counts(numOfThreads);

	for (size_t i = 0; i < numOfThreads; ++i)
	{
		size_t begin = i * step;

		if (begin < totalJobs)
		{
			size_t subRound = totalJobs - begin;
			subRound = subRound > step ? step : subRound;

			ths.emplace_back(
				[i, diff, diffMin, aHashR, maxWaitTime, numOfBlock, subRound, &randEngs, &counts]()
				{
					MCSimulate(diff, diffMin, aHashR, maxWaitTime, numOfBlock, subRound, randEngs[i], counts[i]);
				}
			);
		}
	}

	for (auto& t : ths)
	{
		t.join();
	}
	
	std::vector<size_t> countRes(numOfBlock, 0);
	for (size_t bNum = 0; bNum < numOfBlock; ++bNum)
	{
		for (size_t trNum = 0; trNum < numOfThreads; ++trNum)
		{
			countRes[bNum] += counts[trNum][bNum];
		}
	}

	return countRes;
}

void WriteResult(const std::string& fileName, const std::vector<size_t>& counts, size_t rounds)
{
	std::ofstream file;
	file.open(fileName);
	file.precision(std::numeric_limits<double>::max_digits10);

	try
	{
		file << "Num_Of_Block,Count,Rounds,Possibility\n";

		for (size_t i = 0; i < counts.size(); ++i)
		{
			file << i + 1 << "," << counts[i] << "," << rounds << "," << counts[i] / static_cast<double>(rounds) << "\n";
		}
	}
	catch (...)
	{
		file.close();
		throw;
	}

	file.close();
}

size_t HashSeeds(const std::vector<SeedType>& seeds)
{
	size_t res = std::hash<SeedType>{}(seeds[0]);
	for (size_t i = 1; i < seeds.size(); ++i)
	{
		size_t upd = std::hash<SeedType>{}(seeds[i]);
		res = res ^ (upd << 1);
	}

	return res;
}

int main(int argc, char** argv)
{
	size_t  maxNumOfThreads = 0;
	std::string sessionID;

	try
	{
		if (argc != 2 && argc != 3)
		{
			throw std::invalid_argument("Wrong number of arguments.");
		}

		maxNumOfThreads = std::stoi(argv[1]);
		if (maxNumOfThreads == 0)
		{
			throw std::invalid_argument("Invalid input for number of threads.");
		}
		if (maxNumOfThreads > MAX_NUM_OF_THREAD_CAP)
		{
			throw std::invalid_argument("Is the number of threads too large?");
		}

		if (argc > 2)
		{
			sessionID = argv[2];
		}
		
		if (sessionID.size() == 0)
		{
			sessionID = "s";
		}

		std::random_device randDev;
		sessionID += std::to_string(static_cast<uint16_t>(randDev()));
	}
	catch (const std::exception& e)
	{
		std::cout << e.what() << std::endl;
		std::cout << "Usage: \n\t" << argv[0] << "\n\t\t<Int: Num of Threads>\n\t\t<Str: SessionID Prefix (Optional)>" << std::endl;
		return -1;
	}

	std::cout << "INFO: " << "Number of Threads: " << maxNumOfThreads << std::endl;
	std::cout << "INFO: " << "Session ID       : " << sessionID       << std::endl;
	std::cout << std::endl;

	std::cout.precision(std::numeric_limits<double>::max_digits10);

	constexpr int64_t maxWaitTime     = 900;
	constexpr size_t  maxNumOfBlock   = 500;
	
	//constexpr size_t maxSimRounds    = 1000000;      // 10^6,  ~1 sec
	//constexpr size_t maxSimRounds    = 10000000;     // 10^7,  ~10 sec
	//constexpr size_t maxSimRounds    = 100000000;    // 10^8,  ~100 sec = 1:40 min
	constexpr size_t maxSimRounds    = 1000000000;   // 10^9,  ~1000 sec = 16:40 min
	//constexpr size_t maxSimRounds    = 10000000000;  // 10^10, ~10000 sec = 2:46 hr
	//constexpr size_t maxSimRounds    = 30000000000;  // 10^10, ~30000 sec = 8:20 hr
	//constexpr size_t maxSimRounds    = 100000000000; // 10^11, ~100000 sec = 27:46 hr
	
	constexpr bool usePresetSeeds  = false;
	constexpr bool constantSim     = true;
	constexpr char const outFile[] = "MCTestResult";

	constexpr double aHashPer   = 0.3; // <- The percentage of total hashrate controlled by attacker.
	constexpr double diffMinPer = 0.8; // <- The percentage of minimum level of difficulty value that is allowed to drop to.

	std::cout << "INFO: " << "Network  Totoal Hashrate: " << EthExpr::TOTAL_HASHRATE             << std::endl;
	std::cout << "INFO: " << "Attacker Hashrate       : " << EthExpr::AttackerHashrate(aHashPer) << std::endl;

	std::cout << "INFO: " << "Network  Expected BlockTime: " << EthExpr::EXP_BLOCK_TIME                 << std::endl;
	std::cout << "INFO: " << "Attacker Expected BlockTime: " << EthExpr::AttackerExpBlockTime(aHashPer) << std::endl;

	std::cout << "INFO: " << "Network Difficulty         : " << EthExpr::DIFFICULTY                << std::endl;
	std::cout << "INFO: " << "Difficulty Min             : " << EthExpr::DifficultyMin(diffMinPer) << std::endl;

	auto startTime    = std::chrono::high_resolution_clock::now();
	auto startSysTime = std::chrono::system_clock::now();

	do
	{
		// Generate Seeds
		if (usePresetSeeds && (sizeof(SeedType) * maxNumOfThreads) > PRESET_SEEDS.size())
		{
			throw std::invalid_argument("There is no enough preset seeds.");
		}
		std::vector<SeedType> seeds;
		seeds.resize(maxNumOfThreads, 0);
		if (usePresetSeeds)
		{
			std::memcpy(seeds.data(), PRESET_SEEDS.data(), sizeof(SeedType) * maxNumOfThreads);
		}
		else
		{
			std::random_device randDev;
			for (auto& seed : seeds)
			{
				seed = randDev();
			}
		}

		uint32_t shortSeedHash = static_cast<uint32_t>(HashSeeds(seeds));
		std::cout << "INFO: " << "Seeds' Short Hash : " << shortSeedHash << std::endl;

		// Construct Random Engine
		std::vector<RandEng> randEngs;
		randEngs.reserve(maxNumOfThreads);
		for (size_t i = 0; i < maxNumOfThreads; ++i)
		{
			randEngs.emplace_back(seeds[i]);
		}

		// Run sim test
		std::vector<size_t> counts = MCSimulateThreads(EthExpr::DIFFICULTY, EthExpr::DifficultyMin(diffMinPer), EthExpr::AttackerHashrate(aHashPer), maxWaitTime, maxNumOfBlock, maxSimRounds, randEngs, maxNumOfThreads);

		auto endTime    = std::chrono::high_resolution_clock::now();
		auto endSysTime = std::chrono::system_clock::now();

		std::cout << "INFO: " << "Completed. Time used : " << std::chrono::duration<double>(endTime - startTime).count() / 60 << " Min." << std::endl;

		// Write the result
		std::time_t currTime = std::chrono::system_clock::to_time_t(startSysTime);
		std::tm     currTimeTm = *std::localtime(&currTime);

		std::ostringstream oss;
		oss << std::put_time(&currTimeTm, "%Y%m%d%H%M%S");
		std::string currTimeStr = oss.str();

		std::string taggedFileName = usePresetSeeds ? "x_" : "p_";
		taggedFileName += std::string(outFile) + "_" + sessionID + "_" + currTimeStr + "_sh" + std::to_string(shortSeedHash) + "_" + std::to_string(maxSimRounds) + ".csv";
		std::cout << "INFO: " << "Writing results to file: " << taggedFileName << std::endl;
		WriteResult(taggedFileName, counts, maxSimRounds);

		// Update time
		startTime = endTime;
		startSysTime = endSysTime;
	} 
	while (constantSim && !usePresetSeeds);

	return 0;
}
