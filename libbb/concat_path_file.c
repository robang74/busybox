/* vi: set sw=4 ts=4: */
/*
 * Utility routines.
 *
 * Copyright (C) many different people.
 * If you wrote this, please acknowledge your work.
 *
 * Licensed under GPLv2 or later, see file LICENSE in this source tree.
 */
#include "libbb.h"

/* Concatenate path and filename to new allocated buffer.
 * Add '/' only as needed (no duplicate // are produced).
 * If path is NULL, it is assumed to be "/".
 * filename should not be NULL.
 */

char* FAST_FUNC concat_path_file(const char *path, const char *filename)
{
#if 0
	char *lc;

	if (!path)
		path = "";
	lc = last_char_is(path, '/');
	while (*filename == '/')
		filename++;
	return xasprintf("%s%s%s", path, (lc==NULL ? "/" : ""), filename);
#else
/* ^^^^^^^^^^^ timing of xasprintf-based code above:
 * real 7.074s
 * user 0.156s <<<
 * sys  6.394s
 *	"rm -rf" of a Linux kernel tree from tmpfs (run time still dominated by in-kernel work, though)
 * real 6.989s
 * user 0.055s <<< 3 times less CPU used
 * sys  6.450s
 * vvvvvvvvvvv timing of open-coded malloc+memcpy code below (+59 bytes):
 */
	char *buf, *p;
	size_t n1, n2, n3;

	while (*filename == '/')
		filename++;

	if (!path || !path[0])
		return xstrdup(filename);

	n1 = strlen(path);
	n2 = (path[n1 - 1] != '/'); /* 1: "path has no trailing slash" */
	n3 = strlen(filename) + 1;

	buf = xmalloc(n1 + n2 + n3);
	p = mempcpy(buf, path, n1);
	if (n2)
		*p++ = '/';
	memcpy(p, filename, n3);
	return buf;
#endif
}


/* Optimized concatenate for directory entries - uses d_reclen/d_namlen optimization */
char* FAST_FUNC concat_path_file_fast(const char *path, const struct dirent *dirp)
{
	const char *filename = dirp->d_name;
	char *buf, *p;
	int lc_slash = 0;
	int name_offset, end_offset;
	int pathlen, namelen;

	if (!path || !path[0])
		return xstrdup(filename);

	pathlen = strlen(path);
	namelen = get_d_namlen(dirp);

	if (path[pathlen - 1] != '/') lc_slash = 1;
	while (*filename == '/') {
		filename++;
		namelen--;
	}
	name_offset = pathlen + lc_slash;
	end_offset = name_offset + namelen;
	buf = (char *)xmalloc(end_offset + 1);
	p = mempcpy(buf, path, pathlen);
	if (lc_slash == 1) *p = '/';
	p++;
	memcpy(p, filename, namelen + 1);
	return buf;
}
