/* vi: set sw=4 ts=4: */
/*
 * CRC32 table fill function
 * Copyright (C) 2006 by Rob Sullivan <cogito.ergo.cogito@gmail.com>
 * (I can't really claim much credit however, as the algorithm is
 * very well-known)
 *
 * The following function creates a CRC32 table depending on whether
 * a big-endian (0x04c11db7) or little-endian (0xedb88320) CRC32 is
 * required. Admittedly, there are other CRC32 polynomials floating
 * around, but Busybox doesn't use them.
 *
 * endian = 1: big-endian
 * endian = 0: little-endian
 *
 * Licensed under GPLv2, see file LICENSE in this source tree.
 */
#include "libbb.h"

uint32_t *global_crc32_table = NULL;

static ALWAYS_INLINE uint32_t*
crc32_filltable_endian0(uint32_t *crc_table)
{
	uint32_t polynomial = 0xedb88320;
	uint32_t c;
	unsigned i, j;

	for (i = 0; i < 256; i++) {
		c = i;
		for (j = 8; j; j--) {
			c = (c&1) ? ((c >> 1) ^ polynomial) : (c >> 1);
		}
		*crc_table++ = c;
	}

	return crc_table;
}
static ALWAYS_INLINE uint32_t*
crc32_filltable_endian1(uint32_t *crc_table)
{
	uint32_t polynomial = 0x04c11db7;
	uint32_t c;
	unsigned i, j;

	for (i = 0; i < 256; i++) {
		c = (i << 24);
		for (j = 8; j; j--) {
			c = (c&0x80000000) ? ((c << 1) ^ polynomial) : (c << 1);
		}
		*crc_table++ = c;
	}

	return crc_table;
}
uint32_t* FAST_FUNC crc32_filltable(uint32_t *crc_table, int endian)
{
	if (!crc_table)
		crc_table = xmalloc(256 * sizeof(uint32_t));

	if(endian)
		crc32_filltable_endian1(crc_table);
	else
		crc32_filltable_endian0(crc_table);

	return crc_table;
}
/* Common uses: */
static ALWAYS_INLINE uint32_t* crc32_new_table_le(void)
{
	return crc32_filltable(NULL, 0);
}
uint32_t* FAST_FUNC global_crc32_new_table_le(void)
{
	if (!global_crc32_table)
	    global_crc32_table = crc32_new_table_le();
	return global_crc32_table;
}

uint32_t FAST_FUNC
crc32_block_endian1(uint32_t val, const void *buf, unsigned len, uint32_t *crc_table)
{
	const void *end = (uint8_t*)buf + len;

	while (buf != end) {
		val = (val << 8) ^ crc_table[(val >> 24) ^ *(uint8_t*)buf];
		buf = (uint8_t*)buf + 1;
	}
	return val;
}

#if defined(__x86_64__) && defined(__SSE4_2__)
#include <nmmintrin.h>
uint32_t FAST_FUNC
crc32_block_endian0(uint32_t crc, const void *data, unsigned len,
        uint32_t *table UNUSED_PARAM)
{
    const uint8_t *p = data;
    crc = ~crc;

    /* Align to 8 bytes */
    while (len && ((uintptr_t)p & 7)) {
        crc = _mm_crc32_u8(crc, *p++);
        len--;
    }

    /* 8-byte chunks */
    const uint64_t *q = (const uint64_t *)p;
    while (len >= 8) {
        crc = _mm_crc32_u64(crc, *q++);
        len -= 8;
    }

    /* Tail */
    p = (const uint8_t *)q;
    while (len--)
        crc = _mm_crc32_u8(crc, *p++);

    return ~crc;
}
#else
uint32_t FAST_FUNC
crc32_block_endian0(uint32_t val, const void *buf, unsigned len, uint32_t *crc_table)
{
	const void *end = (uint8_t*)buf + len;

	while (buf != end) {
		val = crc_table[(uint8_t)val ^ *(uint8_t*)buf] ^ (val >> 8);
		buf = (uint8_t*)buf + 1;
	}
	return val;
}
#endif

