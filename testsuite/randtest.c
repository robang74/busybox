/*
 * (c) 2026, Roberto A. Foglietta <roberto.foglietta@gmail.com>, GPLv2
 *
 * compile & testing
 *
    gcc -O2 rtest.c -o rtest
    for i in $(seq 1 1024); do ./rtest 0 0xf0000000 1024 | ent |
        grep Carlo| cut -d' ' -f9; sleep 0.0001; done| sort -n | tail
 */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stddef.h>
#include <time.h>

#define murmul1 0xff51afd7UL

// RAF: artificially limiting the rand() output for testing the worst case
#undef  RAND_MAX
#define RAND_MAX 32768

#if 0
static inline
unsigned random_in_range(unsigned min, unsigned max)
{
	unsigned r = (rand() % RAND_MAX);
	/* RAND_MAX can be as small as 32767 */
	if (max > RAND_MAX)
		r ^= (rand() % RAND_MAX) << 15;
	return r % max;
}
#else
static inline
unsigned random_in_range(unsigned min, unsigned max)
{
	size_t k = 0, r = (rand() % RAND_MAX);
	int i;

	/* RAND_MAX can be as small as 32767 */
	if (max > RAND_MAX) {
		for(i = 1024; !r && i; i--)
			r = (rand() % RAND_MAX) << 17;
		for(i = 1024; !k && i; i--)
			k = (rand() % RAND_MAX) <<  7;
		r ^= k;
    r *= murmul1;
	}
	r %= max-min;
	r += min;

	return r;
}
#endif

static inline
unsigned long long monotonic_us(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC,&ts);
    return ts.tv_sec * 1000000ULL + ts.tv_nsec/1000;
}

int main(int argc, char *argv[])
{
	unsigned min, max, count;
	unsigned i, n;
	unsigned val;

	if (argc != 4) {
		fprintf(stderr, "Usage: %s <min> <max> <count>\n", argv[0]);
		return 1;
	}

	min = (unsigned)strtoul(argv[1], NULL, 0);
	max = (unsigned)strtoul(argv[2], NULL, 0);
	count = (unsigned)strtoul(argv[3], NULL, 0);

	if (max <= min) {
		fprintf(stderr, "Error: max must be > min\n");
		return 1;
	}

	srand((unsigned)monotonic_us());

	n = 1 + (max >> 8) ? ( (max >>16) ? 3 : 1 ) : 0;
	for (i = 0; i < count; i++) {
		val = random_in_range(min, max);
		if (fwrite(&val, n, 1, stdout) != 1) {
			perror("fwrite");
			return 1;
		}
	}

	return 0;
}
