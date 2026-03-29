/* vi: set sw=4 ts=4: */
/*
 * Mini remove_file implementation for busybox
 *
 * Copyright (C) 2001 Matt Kraai <kraai@alumni.carnegiemellon.edu>
 *
 * Licensed under GPLv2 or later, see file LICENSE in this source tree.
 */
#include "libbb.h"

/* Used from NOFORK applets. Must not allocate anything */

static int FAST_FUNC fileAction(struct recursive_state *state,
		struct stat *statbuf)
{
	int flags = *((int*)state->userData);
	int isdir = S_ISDIR(statbuf->st_mode);

	if (!isdir || (state->state & ACTION_DEPTH_PRE)) {
		if (isdir && !(flags & FILEUTILS_RECUR)) {
			bb_error_msg("'%s' is a directory", state->fileName);
			return FALSE;
		}

		if ((!(flags & FILEUTILS_FORCE)
		     && faccessat(state->dirfd, state->baseName, W_OK, 0) < 0
		     && !S_ISLNK(statbuf->st_mode)
		     && isatty(0))
		 || (flags & FILEUTILS_INTERACTIVE)
		) {
			fprintf(stderr, "%s: %s '%s'? ", isdir ? "remove" : "descend into directory", applet_name, state->fileName);
			if (!bb_ask_y_confirmation())
				return isdir ? SKIP : TRUE;
		}

		if (isdir)
			return TRUE;
	}

	// FIXME isdir && status == 0
	if (unlinkat(state->dirfd, state->baseName, isdir ? AT_REMOVEDIR : 0) < 0) {
		bb_perror_msg("can't remove '%s'", state->fileName);
		return FALSE;
	}

	if (flags & FILEUTILS_VERBOSE) {
		printf("removed %s'%s'\n", isdir ? "directory: " : "", state->fileName);
	}

	return TRUE;
}

int FAST_FUNC remove_file(const char *path, int flags)
{
	int ret = recursive_action(path,
		ACTION_QUIET|ACTION_DEPTH_PRE|ACTION_DEPTH_POST | ((flags & FILEUTILS_RECUR) ? ACTION_RECURSE : 0),
		fileAction, fileAction, &flags
	);
	return ret == FALSE ? -1 : 0;
}
