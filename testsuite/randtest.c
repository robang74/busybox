/*
 * (c) 2026, Roberto A. Foglietta <roberto.foglietta@gmail.com>, GPLv2
 *
 * compile & testing
 *
    cd testsuite; gcc -O2 randtest.c -o rtest
    for i in $(seq 1 1024); do ./rtest 0 0xf0000000 1024 2>&- | ent |
        grep Carlo| cut -d' ' -f9; sleep 0.0001; done| sort -n | tail
    ./rtest 0 0xffffffff $(( 1 << 31 )) | RNG_test stdin32
 */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stddef.h>
#include <stdint.h>
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
uint32_t random_in_range(uint32_t min, uint32_t max)
{
	uint32_t r = (rand() % RAND_MAX);

	/* RAND_MAX can be as small as 32767 */
  r ^= (uint32_t)(rand() % RAND_MAX) << 17;
  r ^= (uint32_t)(rand() % RAND_MAX) <<  7;
  r *= murmul1;
  r ^= r >> 16;
	r %= max-min;
	r += min;

	return r;
}
#endif

static inline
void srand_init(void)
{
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  srand( ts.tv_sec ^ ts.tv_nsec );
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

	min   = (unsigned)strtoul(argv[1], NULL, 0);
	max   = (unsigned)strtoul(argv[2], NULL, 0);
	count = (unsigned)strtoul(argv[3], NULL, 0);

	if (max <= min) {
		fprintf(stderr, "Error: max must be > min\n");
		return 1;
	}

	srand_init();

	n = 1 + ((max >> 8) ? ( (max >>16) ? 3 : 1 ) : 0);
	fprintf(stderr, "bytes in use: %u\n", n);
	for (i = 0; i < count; i++) {
		char *p = (char *)&val;
		val = random_in_range(min, max);
		if (fwrite(&p[4-n], n, 1, stdout) != 1) {
			perror("fwrite");
			return 1;
		}
	}

	return 0;
}
