#pragma once

#include <cstdint>

namespace EthExpr
{
	// The hashrate of the entire eth network, recorded as of Dec 13, 2020
	static constexpr uint64_t TOTAL_HASHRATE =  285898364400000;

	// The block difficulty, recorded as of Dec 13, 2020
	static constexpr uint64_t DIFFICULTY     = 3546605094014496;

	// The expected block time for the entire eth network.
	static constexpr double   EXP_BLOCK_TIME = DIFFICULTY / static_cast<double>(TOTAL_HASHRATE);
}
