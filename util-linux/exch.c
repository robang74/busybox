/* vi: set sw=4 ts=4: */
/*
 * exch for busybox
 *
 * Licensed under GPLv2, see LICENSE in this source tree
 */
//config:config EXCH
//config:	bool "exch (4.4 kb)"
//config:	default n
//config:	help
//config:	exch is used to atomically exchange 2 files or directories
//config:
//config:	requires renameat2()

//applet:IF_EXCH(APPLET_NOFORK(exch, exch, BB_DIR_USR_BIN, BB_SUID_DROP, exch))

//kbuild:lib-$(CONFIG_EXCH) += exch.o

//usage:#define exch_trivial_usage
//usage:	"PATH PATH"
//usage:#define exch_full_usage "\n\n"
//usage:	"Atomically exchange 2 paths"

#define _GNU_SOURCE 1 /* for renameat2 */
#include "libbb.h"

int exch_main(int argc, char **argv) MAIN_EXTERNALLY_VISIBLE;
int exch_main(int argc UNUSED_PARAM, char **argv)
{
	getopt32(argv, "^" "" "\0" "=2");
	argv += optind;
	if (renameat2(AT_FDCWD, argv[0], AT_FDCWD, argv[1], RENAME_EXCHANGE))
		bb_perror_msg_and_die("can't exchange '%s' and '%s'", argv[0], argv[1]);
	return EXIT_SUCCESS;
}
