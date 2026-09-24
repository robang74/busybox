/* vi: set sw=4 ts=4: */
/*
 * Fast acquisition of d_namlen
 *
 * Copyright (C) 2024 by Jody Bruchon <jody@jodybruchon.com>
 * Copied from libjodycode for use with BusyBox
 *
 * Licensed under GPLv2 or later, see file LICENSE in this source tree.
 */

#include "libbb.h"

/* Extract d_namlen from struct dirent */
size_t get_d_namlen(const struct dirent * const dirent)
{
#ifdef _DIRENT_HAVE_D_NAMLEN
	return dirent->d_namlen;
#elif defined _DIRENT_HAVE_D_RECLEN
	const size_t base = (sizeof(struct dirent) - sizeof(((struct dirent *)0)->d_name)) - offsetof(struct dirent, d_name) - 1;
	size_t skip;

	skip = dirent->d_reclen - (sizeof(struct dirent) - sizeof(((struct dirent *)0)->d_name));
	if (skip > 0) skip -= base;
	return skip + strlen(dirent->d_name + skip);
#else
	return strlen(dirent->d_name);
#endif
	return 0;
}
