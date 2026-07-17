/*
 * (c) 2026, Roberto A. Foglietta <roberto.foglietta@gmail.com>, GPLv2
 *
 ******************************************************************************/

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
//config:	bool "uxsh (0.4 kb)"
//config:	default n
//config:	help
//config:	  uxsh parses the shebang (#!) of a script passed as 1st argument
//config:	  and executes the file script as defined into the shebang line.

int uxsh_main(int argc, char **argv) MAIN_EXTERNALLY_VISIBLE;
int uxsh_main(int argc, char **argv)
{
    char buf[256];
    char *interp, *interp_arg = NULL;
    char *script_path;
    int fd, n;

    script_path = *++argv;
    if (!script_path)
        bb_simple_error_msg_and_die("Missing 1st argument");

    fd = xopen(script_path, O_RDONLY);

    n = full_read(fd, buf, sizeof(buf) - 1);
    close(fd);
    
    if (n < 2 || buf[0] != '#' || buf[1] != '!')
        bb_simple_error_msg_and_die("Invalid shebang (!#)");

    buf[n] = '\0';

    char *nl = strchr(buf, '\n');
    if (nl) *nl = '\0';
    nl = strchr(buf, '\r');
    if (nl) *nl = '\0';

    interp = skip_whitespace(buf + 2);

    char *p = strpbrk(interp, " \t");
    if (p) {
        *p = '\0';
        interp_arg = skip_whitespace(p + 1);
        if (!*interp_arg)
            interp_arg = NULL;
    }

    char **new_argv = xzalloc(sizeof(char*) * (argc + 2));
    int i = 0;

    new_argv[i++] = interp;
    if (interp_arg)
        new_argv[i++] = interp_arg;

    while (*argv)
        new_argv[i++] = *argv++;

    execve(interp, new_argv, environ);
    bb_perror_msg_and_die("exec %s failed", interp);
}

