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

#define TBL_ELM 256
#define crc32_table_slice_size (TBL_ELM * sizeof(uint32_t))

#ifndef USE_CRC32_X86_ASM
# if __BYTE_ORDER == __BIG_ENDIAN
# warning "USE_CRC32_X86_ASM is incompatible with BIG_ENDIAN"
# define USE_CRC32_X86_ASM 0
# else
# define USE_CRC32_X86_ASM 0 /* 1, for testing */
# endif
#endif

#if USE_CRC32_X86_ASM
#undef  ENABLE_CRC32_4BYTES
#define ENABLE_CRC32_4BYTES 0
#endif

#if !USE_CRC32_X86_ASM && defined(__x86_64__) && defined(__SSE4_2__) ///////////////////////
#include <nmmintrin.h>
# undef  ENABLE_CRC32_4BYTES
# define ENABLE_CRC32_4BYTES 0
#else
# ifdef  CONFIG_FEATURE_CRC32_4BYTES
# define ENABLE_CRC32_4BYTES 1
# else
# define ENABLE_CRC32_4BYTES 0
# endif
#endif

#if ENABLE_CRC32_4BYTES
// Source for the table:
// https://raw.githubusercontent.com/stbrumme/crc32/refs/heads/master/Crc32.cpp
//
#include "crc32_table.h"
uint32_t *global_crc32_table ALIGN_PTR = (uint32_t *)crc32_lookup_table[0];
#else
uint32_t *global_crc32_table ALIGN_PTR = NULL;
#endif

static ALWAYS_INLINE
uint32_t* crc32_filltable_endian0(uint32_t *crc_table)
{
	if(global_crc32_table) {
		crc_table = __builtin_memmove(crc_table,
			global_crc32_table, crc32_table_slice_size);
	} else {
		uint32_t polynomial = 0xedb88320;
		uint32_t c;
		unsigned i, j;

		for (i = 0; i < TBL_ELM; i++) {
			c = i;
			for (j = 8; j; j--) {
				c = (c&1) ? ((c >> 1) ^ polynomial) : (c >> 1);
			}
			*crc_table++ = c;
		}
	}
	return crc_table;
}

#if 0
/* RAF, TODO: testing populated-on-the-fly 4 and 8-slice CRC32 against big files
 *
 * When populating a table on-the-fly, the start time delay is competing with the
 * faster usage. The outcome is file size dependent. However small files take a
 * little time, and the difference can be noticed on the bigger ones. Those for which
 * pre-computing a 8-slice table and using it, can be faster in throughput (CPU).
 */
{
	/* After computing the base table[0..255], derive the others */
	for (short s = 0; s < 7; s++) {
		for (short i = 0; i < 256; i++) {
		    register uint32_t tbl = table[s-1][i];
		    table[s][i] = (tbl >> 8) ^ table[0][(uint8_t)tbl];
		}
	}
}
#endif

static ALWAYS_INLINE
uint32_t* crc32_filltable_endian1(uint32_t *crc_table)
{
	uint32_t polynomial = 0x04c11db7;
	uint32_t c;
	unsigned i, j;

	for (i = 0; i < TBL_ELM; i++) {
		c = (i << 24);
		for (j = 8; j; j--) {
			c = (c&0x80000000) ? ((c << 1) ^ polynomial) : (c << 1);
		}
		*crc_table++ = c;
	}

	return crc_table;
}

FAST_FUNC
uint32_t* crc32_filltable(uint32_t *crc_table, int endian)
{
#if !USE_CRC32_X86_ASM
	if (!crc_table)
		crc_table = xmalloc(crc32_table_slice_size);

	if(endian)
		crc32_filltable_endian1(crc_table);
	else
		crc32_filltable_endian0(crc_table);
#endif
	return crc_table;
}

FAST_FUNC
uint32_t crc32_block_endian1(uint32_t val, const void *buf, unsigned len, uint32_t *crc_table)
{
	const void *end = (uint8_t*)buf + len;

	while (buf != end) {
		val = (val << 8) ^ crc_table[(val >> 24) ^ *(uint8_t*)buf];
		buf = (uint8_t*)buf + 1;
	}

	return val;
}

#if defined(__x86_64__) && defined(__SSE4_2__) /////////////////////////////////////////////
#include <nmmintrin.h>

FAST_FUNC
uint32_t* global_crc32_new_table_le(void) { return NULL; }

FAST_FUNC
uint32_t crc32_block_endian0(uint32_t crc, const void *data, unsigned len,
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

#else //////////////////////////////////////////////////////////////////////////////////////

static ALWAYS_INLINE
uint32_t* crc32_new_table_le(void)
{
	return crc32_filltable(NULL, 0);
}

FAST_FUNC
uint32_t* global_crc32_new_table_le(void)
{
#if !USE_CRC32_X86_ASM
	if (!global_crc32_table)
		global_crc32_table = crc32_new_table_le();
#endif
	return global_crc32_table;
}

#if ENABLE_CRC32_4BYTES && __BYTE_ORDER == __BIG_ENDIAN
static ALWAYS_INLINE
uint32_t swap(uint32_t x)
{
	// swap endianess
	#if defined(__GNUC__) || defined(__clang__)
	return __builtin_bswap32(x);
	#else
	return (x >> 24) |
	      ((x >>  8) & 0x0000FF00) |
	      ((x <<  8) & 0x00FF0000) |
	       (x << 24);
	#endif
}
#endif

#if USE_CRC32_X86_ASM
/*
 * RAF: this branch has no practical use (-164b) apart from checking the
 *      impact of a CRC32 performance degration on varios decompressors.
 *
 * Source: https://wiki.osdev.org/CRC32#Without_table
 */
static ALWAYS_INLINE
uint32_t crc32_ref_asm(uint32_t crc, const uint8_t *data, uint64_t len)
{
	uint32_t result;

	__asm__ volatile (
	    "mov    %1, %%eax\n\t"           /* incoming crc -> eax */
	    "mov    %2, %%rsi\n\t"           /* data -> rsi */
	    "mov    %3, %%rcx\n\t"           /* len -> rcx */
	    "jrcxz  2f\n\t"                  /* if len==0, skip */
	    "lea    (%%rsi, %%rcx), %%rdi\n" /* rdi = end pointer */
	    "1:\n\t"
	    "xorb   (%%rsi), %%al\n\t"
	    "inc    %%rsi\n\t"
	    "movl   $8, %%ecx\n\t"
	    "3:\n\t"
	    "movl   %%eax, %%edx\n\t"
	    "andl   $1, %%edx\n\t"
	    "negl   %%edx\n\t"
	    "andl   $0xEDB88320, %%edx\n\t"
	    "shrl   $1, %%eax\n\t"
	    "xorl   %%edx, %%eax\n\t"
	    "loop   3b\n\t"
	    "cmp    %%rdi, %%rsi\n\t"
	    "jne    1b\n"
	    "2:\n\t"
	    "movl   %%eax, %0"               /* eax -> result */
	    : "=r" (result)
	    : "r" (crc), "r" (data), "r" (len)
	    : "rax", "rcx", "rdx", "rsi", "rdi", "cc", "memory"
	);

	return result;
}
#endif

FAST_FUNC
uint32_t crc32_block_endian0(uint32_t val, const void *buf,
	unsigned len, uint32_t *table UNUSED_PARAM)
{
#if USE_CRC32_X86_ASM
	val = crc32_ref_asm(val, buf, len);
#else
	#if ENABLE_CRC32_4BYTES // compute CRC32 by slicing-by-4 algorithm
	const uint32_t *cur = (const uint32_t *)buf;
	const uint32_t *end = cur + (len >> 2);

	// process four bytes each cycle
	while (end != cur)
	{
	    #if __BYTE_ORDER == __BIG_ENDIAN
	    uint32_t one = *cur++ ^ swap(val);
	    val = crc32_lookup_table[0][(uint8_t) one     ] ^
	          crc32_lookup_table[1][(uint8_t)(one>> 8)] ^
	          crc32_lookup_table[2][(uint8_t)(one>>16)] ^
	          crc32_lookup_table[3][(uint8_t)(one>>24)];
	    #else
	    uint32_t one = *cur++ ^      val;
	    val = crc32_lookup_table[0][(uint8_t)(one>>24)] ^
	          crc32_lookup_table[1][(uint8_t)(one>>16)] ^
	          crc32_lookup_table[2][(uint8_t)(one>> 8)] ^
	          crc32_lookup_table[3][(uint8_t) one     ];
	    #endif
	} // possibly 1 to 3 bytes remain, fallback
	#else
	#define cur buf
	#endif
	{
	    const uint8_t *curc = (const uint8_t *) cur;
	    uint8_t *endc = (uint8_t *)buf + len;
	    while (curc != endc)
	      val = global_crc32_table[(uint8_t)val
	                       ^ *(uint8_t*)curc++] ^ (val >> 8);
	}
#endif
	return val;
}


#endif /////////////////////////////////////////////////////////////////////////////////////

