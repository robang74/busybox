/* vi: set sw=4 ts=4: */
/*
 * Utility routines.
 *
 * Copyright (C) 1999-2004 by Erik Andersen <andersen@codepoet.org>
 *
 * Licensed under GPLv2 or later, see file LICENSE in this source tree.
 */
#include "libbb.h"

#undef DEBUG_RECURS_ACTION

/*
 * Walk down all the directories under the specified
 * location, and do something (something specified
 * by the fileAction and dirAction function pointers).
 *
 * Unfortunately, while nftw(3) works very similar it does not expose
 * the file descriptors to allow safe usage.
 */

static int FAST_FUNC true_action(struct recursive_state *state UNUSED_PARAM,
		struct stat *statbuf UNUSED_PARAM)
{
	return TRUE;
}

/* fileName is (l)stat'ed (depending on ACTION_FOLLOWLINKS[_L0]).
 *
 * If it is a file: fileAction in run on it, its return value is returned.
 *
 * In case we are in a recursive invocation (see below):
 * normally, fileAction should return 1 (TRUE) to indicate that
 * everything is okay and processing should continue.
 * fileAction return value of 0 (FALSE) on any file in directory will make
 * recursive_action() also return 0, but it doesn't stop directory traversal
 * (fileAction/dirAction will be called on each file).
 *
 * [TODO: maybe introduce -1 to mean "stop traversal NOW and return"]
 *
 * If it is a directory:
 *
 * If !ACTION_RECURSE, dirAction is called and its
 * return value is returned from recursive_action(). No recursion.
 *
 * If ACTION_RECURSE, directory is opened, and recursive_action() is called
 * on each file/subdirectory.
 * If any one of these calls returns 0, current recursive_action() returns 0.
 *
 * If ACTION_DEPTH_PRE, dirAction is called before recurse.
 * Return value of 0 (FALSE) is an error: prevents recursion,
 * the warning is printed (unless ACTION_QUIET) and recursive_action() returns 0.
 * Return value of 2 (SKIP) prevents recursion, instead recursive_action()
 * returns 1 (TRUE, no error).
 *
 * If ACTION_DEPTH_POST, dirAction is called after recurse.
 * If it returns 0, the warning is printed and recursive_action() returns 0.
 *
 * ACTION_FOLLOWLINKS mainly controls handling of links to dirs.
 * 0: lstat(statbuf). Calls fileAction on link name even if points to dir.
 * 1: stat(statbuf). Calls dirAction and optionally recurse on link to dir.
 */

static int recursive_action1(recursive_state_t *state)
{
	struct stat statbuf;
	unsigned follow;
	int status, olddirfd = state->dirfd;
	DIR *dir;
	struct dirent *next;

	follow = ACTION_FOLLOWLINKS;
	if (state->depth == 0)
		follow = ACTION_FOLLOWLINKS | ACTION_FOLLOWLINKS_L0;
	follow &= state->flags;
	status = fstatat(state->dirfd, state->baseName, &statbuf, follow ? 0 : AT_SYMLINK_NOFOLLOW);
	if (status < 0) {
#ifdef DEBUG_RECURS_ACTION
		bb_error_msg("status=%d flags=%x", status, state->flags);
#endif
		if ((state->flags & ACTION_DANGLING_OK)
		 && errno == ENOENT
		 && fstatat(state->dirfd, state->baseName, &statbuf, AT_SYMLINK_NOFOLLOW) == 0
		) {
			/* Dangling link */
			return state->fileAction(state, &statbuf);
		}
		goto done_nak_warn;
	}

	/* If S_ISLNK(m), then we know that !S_ISDIR(m).
	 * Then we can skip checking first part: if it is true, then
	 * (!dir) is also true! */
	if ( /* (!(state->flags & ACTION_FOLLOWLINKS) && S_ISLNK(statbuf.st_mode)) || */
	 !S_ISDIR(statbuf.st_mode)
	) {
		return state->fileAction(state, &statbuf);
	}

	/* It's a directory (or a link to one, and followLinks is set) */

	if (!(state->flags & ACTION_RECURSE)) {
		return state->dirAction(state, &statbuf);
	}

	if (state->flags & ACTION_DEPTH_PRE) {
		state->state = ACTION_DEPTH_PRE;
		status = state->dirAction(state, &statbuf);
		if (status == FALSE)
			goto done_nak_warn;
		if (status == SKIP)
			return TRUE;
	}

	state->dirfd = openat(olddirfd, state->baseName, O_RDONLY | O_DIRECTORY | (follow ? 0 : O_NOFOLLOW));
	if (state->dirfd < 0)
		goto done_nak_warn;
	dir = fdopendir(state->dirfd);
	if (!dir) {
		/* findutils-4.1.20 reports this */
		/* (i.e. it doesn't silently return with exit code 1) */
		/* To trigger: "find -exec rm -rf {} \;" */
		goto done_nak_warn;
	}
	state->dirfd = dirfd(dir);
	status = TRUE;
	while ((next = readdir(dir)) != NULL) {
		size_t n1, n2, n3;
		int s;

		if (DOT_OR_DOTDOT(next->d_name))
			continue;

		n1 = strlen(state->fileName);
		n2 = (state->fileName[n1 - 1] != '/'); /* 1: "path has no trailing slash" */
		n3 = strlen(next->d_name) + 1;

		state->fileName = xrealloc(state->fileName, n1 + n2 + n3);
		if (n2)
			state->fileName[n1] = '/';
		state->baseName = &state->fileName[n1+n2];
		memcpy(state->baseName, next->d_name, n3);

		/* process every file (NB: ACTION_RECURSE is set in flags) */
		state->depth++;
		s = recursive_action1(state);
		if (s == FALSE)
			status = FALSE;
		state->depth--;

		state->fileName = xrealloc(state->fileName, n1 + 1);
		state->fileName[n1] = '\0';
		state->baseName = strrchr(state->fileName, '/');
		state->baseName = state->baseName ? state->baseName + 1 : state->fileName;

//#define RECURSE_RESULT_ABORT -1
//		if (s == RECURSE_RESULT_ABORT) {
//			closedir(dir);
//			return s;
//		}
	}
	state->dirfd = olddirfd;
	closedir(dir);

	if (state->flags & ACTION_DEPTH_POST) {
		state->state = ACTION_DEPTH_POST;
		if (!state->dirAction(state, &statbuf))
			goto done_nak_warn;
	}

	return status;

 done_nak_warn:
	if (!(state->flags & ACTION_QUIET))
		bb_simple_perror_msg(state->fileName);

	state->dirfd = olddirfd;
	return FALSE;
}

int FAST_FUNC recursive_action(const char *fileName,
		unsigned flags,
		int FAST_FUNC (*fileAction)(struct recursive_state *state, struct stat* statbuf),
		int FAST_FUNC  (*dirAction)(struct recursive_state *state, struct stat* statbuf),
		void *userData)
{
	int ret;
	/* Keeping a part of variables of recusive descent in a "state structure"
	 * instead of passing ALL of them down as parameters of recursive_action1()
	 * relieves register pressure, both in recursive_action1()
	 * and in every file/dirAction().
	 */
	recursive_state_t state;
	state.flags = flags | ((flags & (ACTION_DEPTH_PRE|ACTION_DEPTH_POST)) ? 0 : ACTION_DEPTH_PRE);
	state.depth = 0;
	state.userData = userData;
	state.fileName = xstrdup(fileName);
	state.baseName = state.fileName;
	state.dirfd = xopen(".", O_RDONLY|O_DIRECTORY);
	state.state = 0;
	state.fileAction = fileAction ? fileAction : true_action;
	state.dirAction  =  dirAction ?  dirAction : true_action;

	ret = recursive_action1(&state);
	free(state.fileName);
	return ret;
}
