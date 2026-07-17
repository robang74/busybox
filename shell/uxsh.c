#include "libbb.h"
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>

//applet:IF_UXSH(APPLET(uxsh, BB_DIR_BIN, BB_SUID_DROP))

//kbuild:lib-$(CONFIG_UXSH) += uxsh.o

//usage:#define uxsh_trivial_usage
//usage:       "[FILE] [ARGS...]"
//usage:#define uxsh_full_usage "\n\n"
//usage:       "Execute a script by parsing its shebang line."

//config:config UXSH
//config:	bool "uxsh (0.6 kb)"
//config:	default n
//config:	help
//config:	  uxsh parses the shebang (#!) of a script passed as 1st argument
//config:	  and executes the file script as defined into the shebang line.

int uxsh_main(int argc, char **argv) MAIN_EXTERNALLY_VISIBLE;
int uxsh_main(int argc, char **argv)
{
	char buf[256];
	unsigned char magic[4];
	char *interp, *interp_arg, *newline;
	char **new_argv;
	int src_fd, new_argc, i;

	argv++; /* Skip "uxsh" from the original argv */

	if (!*argv || LONE_DASH(*argv)) {
		src_fd = STDIN_FILENO;
	} else {
		src_fd = xopen(*argv, O_RDONLY);
	}

	/* Peek at the first 4 bytes to check for a valid uxshang safely */
	if (full_read(src_fd, magic, 4) < 2) {
		bb_error_msg_and_die("short read or empty file");
	}

	/* Check if it actually starts with '#!' */
	if (magic[0] != '#' || magic[1] != '!') {
		bb_error_msg_and_die("not a valid script (missing #!)");
	}

	/* Check if the file descriptor is seekable (e.g., a regular file) */
	if (lseek(src_fd, 0, SEEK_CUR) != (off_t)-1) {
		/* It is a regular file, we can safely rewind to the beginning */
		xlseek(src_fd, 0, SEEK_SET);
	} else {
		bb_error_msg_and_die("piped stdin isn't supported");
	}

	/* Read the head of the stream into our buffer for parsing */
	int n = full_read(src_fd, buf, sizeof(buf) - 1);
	if (n < 0) {
		bb_perror_msg_and_die("failed to read script header");
	}
	buf[n] = '\0';

	/* Isolate the first line by stripping newlines and carriage returns */
	newline = strchr(buf, '\n');
	if (newline) *newline = '\0';
	newline = strchr(buf, '\r');
	if (newline) *newline = '\0';

	/* Skip whitespace after the '#!' tokens */
	interp = skip_whitespace(buf + 2);

	/* Find the first space or tab to isolate an optional interpreter argument */
	interp_arg = strpbrk(interp, " \t");
	if (interp_arg) {
		*interp_arg = '\0';
		interp_arg = skip_whitespace(interp_arg + 1);
		if (*interp_arg == '\0') {
			interp_arg = NULL;
		}
	}

	/* Close the read descriptor before execve to prevent descriptor leaks */
	if (src_fd != STDIN_FILENO) {
		close(src_fd);
	}

	/*
	 * Calculate the new argv array size:
	 * 1 (interpreter) + 1 (optional argument) + remaining user arguments + 1 (NULL)
	 */
	new_argc = 1 + (interp_arg ? 1 : 0) + (argc - 1) + 1;
	new_argv = xzalloc(sizeof(char*) * new_argc);

	i = 0;
	new_argv[i++] = interp;
	if (interp_arg) {
		new_argv[i++] = interp_arg;
	}

	/* Append the original user arguments (including the original script path) */
	while (*argv) {
		new_argv[i++] = *argv++;
	}
	new_argv[i] = NULL;

	/* Execute the interpreter passing the rebuilt argv and the current environment */
	execve(new_argv[0], new_argv, environ);

	/* If execve returns, an irreversible execution error occurred */
	bb_perror_msg_and_die("exec %s failed", new_argv[0]);
}

