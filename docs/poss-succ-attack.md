# Possibility of Successful Attacks

## Fundamental Theories

1. "The time between every two consecutive Bitcoin blocks is an exponentially distributed random variable." [1]

## Formulas

### Possibility of finding a block at time T<sub>&Delta;</sub>

![attack-succ-poss-p1](./figures/attack-succ-poss-p1.svg)

- Table Legends:

|       Symbol       |                        Meaning                       |     Unit     |
|--------------------|------------------------------------------------------|--------------|
|      &theta;       | The network difficulty value                         | `# of hashes`|
|   Q<sub>a</sub>    | The hashpower/hashrate controlled by the attacker    | `hashes/sec` |
|  T<sub>a_exp</sub> | The expected block time for attacker                 | `sec/block`  |
|&lambda;<sub>a</sub>| Attacker's parameter for *Exponential Distribution*  | `block/sec`  |
|  CDF(T, &lambda;)  | *Cumulative Distribution Function*                   | N/A          |

The possibility of a miner mining a block within a given time follows
the exponential distribution[1], where the parameter
&lambda; is the inverse of the expected block time.

Thus, as shown in the formula above,
to find the exponential distribution for an attacker mining a block,
we need to calculate the expected block time (T<sub>a_exp</sub>)
in terms of the attacker.
T<sub>a_exp</sub> can be obtained by dividing
the current difficulty value (&theta;) with the hash power/hash rate (Q<sub>a</sub>)
controlled by the attacker.
Next, we inverse the expected block time to get the &lambda;<sub>a</sub> of the
exponential distribution.
Nonetheless, the timestamps recorded in the block header is an integer value
in seconds.
Therefore, we can get the possibility of the attacker mining a new block with
a given block time (Pr[T<sub>a&Delta;</sub> = T<sub>block</sub>]) by subtracting
the result of two Cumulative Distribution Functions (CDFs), given two
consecutive block times (T<sub>a&Delta;</sub> and T<sub>a&Delta;</sub> - 1).

In Ethereum, the difficulty value changes from block to block.
Hence, based on the formula we have, we can see that the
distribution will also change from block to block.
Thus, we need the transition function for difficulty value (&theta;)
that can be plugged into the formula above.

### Transition of difficulty value

![attack-succ-poss-p2](./figures/attack-succ-poss-p2.svg)

As shown above, we first get the difficulty transition function
(&theta;<sub>&Delta;%</sub>(T<sub>&Delta;</sub>))
from Ethereum's DAA \cite{ether2013whitepaper, ether2020consensusgo}.
This function accepts the block time (T<sub>&Delta;</sub>), and calculates the
change of difficulty in percentage (&theta;<sub>&Delta;%</sub>).
We can then obtain the next block's difficulty value (&theta;<sub>N + 1</sub>)
given the current difficulty value (&theta;<sub>N</sub>) by using this function.

In addition, we assume there is no uncle block on the malicious fork;
otherwise,
attackers have to spend part of their hash power to mine for uncle blocks.

### Possibility of attacker finding the next N blocks, while keeping up the difficulty value

![attack-succ-poss-p3](./figures/attack-succ-poss-p3.svg)

Finally, we want to find the possibility of the attacker finding the next
N blocks without having the difficulty value drop lower than the minimum
value (Pr[&theta;<sub>N</sub> > &theta;<sub>min</sub>]).
This formula shown above is a recursive function.
In the first base case, if the difficulty value of the N-th block is lower
than the minimum, the possibility will be zero, since the condition
fails the assertion that &theta;<sub>N</sub> > &theta;<sub>min</sub>.
In the second base case, if there is no block that the attacker needs to mine
(N = 0), the possibility will be 1, meaning that after the attacker has mined
n blocks (from N = n to N = 0), since the attack is successful as long as
&theta;<sub>N</sub> > &theta;<sub>min</sub>.
For all other cases, we multiply the possibility of mining a block with
block time i seconds by the possibility of attacker mining the next
N-1 blocks with the updated difficulty value,
then we sum them from i = 0 to 900 seconds.

Using the given formula to calculate on a commodity PC, we use the
Dynamic Programming (DP) technique.
To fit the DP table into memory and get the result within a reasonable
amount of time, we reduce the DP table's size by keeping the
highest 6 or 7 digits of the difficulty value and assume the rest are zeros.

## References

[1] [Tesseract: Real-Time Cryptocurrency Exchange Using Trusted Hardware](https://dl.acm.org/doi/10.1145/3319535.3363221)
